import threading
import contextvars
import copy
from typing import Any, Tuple, Optional, List, Dict
from pydantic import BaseModel as struct
from .common import package, kwargs
from .deprecated import deprecated
import asyncio
from .utils import obj2str, str2obj


class ReadWriteLock(object):
    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0

    class ReadLock:
        def __init__(self, rw_lock):
            self.rw_lock = rw_lock

        def __enter__(self):
            with self.rw_lock._read_ready:
                self.rw_lock._readers += 1

        def __exit__(self, exc_type, exc_value, traceback):
            with self.rw_lock._read_ready:
                self.rw_lock._readers -= 1
                if self.rw_lock._readers == 0:
                    self.rw_lock._read_ready.notify_all()

    class WriteLock:
        def __init__(self, rw_lock):
            self.rw_lock = rw_lock

        def __enter__(self):
            self.rw_lock._read_ready.acquire()
            while self.rw_lock._readers > 0:
                self.rw_lock._read_ready.wait()

        def __exit__(self, exc_type, exc_value, traceback):
            self.rw_lock._read_ready.release()

    def read_lock(self):
        return self.ReadLock(self)

    def write_lock(self):
        return self.WriteLock(self)

    def __deepcopy__(self, *args, **kw):
        return ReadWriteLock()

    def __reduce__(self):
        return ReadWriteLock, ()


class ThreadSafeDict(dict):
    def __init__(self, *args, **kw):
        super(__class__, self).__init__(*args, **kw)
        self._lock = ReadWriteLock()

    def __getitem__(self, key):
        with self._lock.read_lock():
            return super(__class__, self).__getitem__(key)

    def __setitem__(self, key, value):
        with self._lock.write_lock():
            return super(__class__, self).__setitem__(key, value)

    def __delitem__(self, key):
        with self._lock.read_lock():
            return super(__class__, self).__delitem__(key)

    def __contains__(self, key):
        with self._lock.read_lock():
            return super(__class__, self).__contains__(key)

    def get(self, key, __default=None):
        with self._lock.read_lock():
            return super(__class__, self).get(key, __default)

    def keys(self):
        with self._lock.read_lock():
            return super(__class__, self).keys()

    def values(self):
        with self._lock.read_lock():
            return super(__class__, self).values()

    def items(self):
        with self._lock.read_lock():
            return super(__class__, self).items()

    def update(self, *args, **kwargs):
        with self._lock.write_lock():
            return super(__class__, self).update(*args, **kwargs)

    def clear(self):
        with self._lock.write_lock():
            return super(__class__, self).clear()

    def pop(self, key, __default=None):
        with self._lock.write_lock():
            return super(__class__, self).pop(key, __default)

    def __len__(self):
        with self._lock.read_lock():
            return super(__class__, self).__len__()

    def __str__(self):
        with self._lock.read_lock():
            return super(__class__, self).__str__()

    def __repr__(self):
        with self._lock.read_lock():
            return super(__class__, self).__repr__()

    def __reduce__(self):
        with self._lock.read_lock():
            return (self.__class__, (dict(self),))


class Globals(object):
    # 这个结构记录每一个sid会话的自身的数据
    __global_attrs__ = ThreadSafeDict(
        chat_history={}, global_parameters={}, bind_args={}, tool_delimiter="<|tool_calls|>", lazyllm_files={}, usage={}
    )

    def __init__(self):
        # 初始化数据存储，使用线程安全字典
        # __data 是 Globals 类的实例变量，不是全局变量
        # __data 是线程安全的容器
        # __data 是一个 ThreadSafeDict 实例，用于存储所有会话的数据
        # 它本身不是基于线程或协程的，而是一个线程安全的字典
        # 真正的数据隔离机制：
        # 数据隔离是通过 _sid（会话ID）实现的，而不是通过 __data 本身
        # __data 存储了所有会话的数据，结构为：{sid1: data1, sid2: data2, ...}
        # 每个线程/协程通过自己的 _sid 访问对应的数据
        self.__data = ThreadSafeDict()

        # 创建上下文变量用于存储会话ID
        # 1. contextvars.ContextVar
        # 这是 Python 标准库中的 contextvars 模块提供的一个类
        # 用于创建上下文变量，这是一种在异步编程中非常有用的数据结构
        # 它允许在同一个线程或协程中不同层级的函数间共享数据，而不会相互干扰
        # 2. 'local_var' 参数
        # 这是 ContextVar 的名称，用于调试和标识
        # 名称本身没有功能性作用，主要是为了调试时识别变量
        # 3. 作用和意义
        # 协程安全: 在异步编程中，不同协程可以有各自独立的变量值
        # 上下文隔离: 每个执行上下文（线程或协程）都有自己的变量副本
        # 自动传播: 当线程创建新协程时，上下文变量会自动传播给子协程
        # 在当前代码中的作用
        # 在 Globals 类中，这个 __sid 变量用于：
        # 存储会话ID: 保存当前线程或协程的唯一标识符
        # 上下文跟踪: 确保在异步操作中能够正确识别和跟踪不同的会话
        # 数据隔离: 结合 self.__data 实现每个会话的数据隔离
        self.__sid = contextvars.ContextVar('local_var')

        # 初始化会话ID
        self._init_sid()

    def _init_sid(self, sid: Optional[str] = None):
        """
        获取协程id或者线程id形成sid(会话标识符，用于追踪会话)
        - 系统会尝试获取当前协程的任务ID：
        - 如果获取失败（不在协程环境中），则使用当前线程ID：
        """
        # 如果没有提供sid，则自动生成
        if sid is None:
            try:
                # 尝试获取当前协程的任务ID
                sid = f'aid-{hex(id(asyncio.current_task()))}'
            except Exception:
                # 如果失败，则使用当前线程ID
                sid = f'tid-{hex(threading.get_ident())}'
        # 设置会话ID到上下文变量中
        self.__sid.set(sid)
        return sid

    @property
    def _sid(self) -> str:
        """
        globals._sid 是基于线程/协程的实例，而不是唯一的全局实例。

        sid的生成机制：

        在 _init_sid 方法中，系统会尝试获取当前协程的任务ID：f'aid-{hex(id(asyncio.current_task()))}'
        如果获取失败（不在协程环境中），则使用当前线程ID：f'tid-{hex(threading.get_ident())}'
        每个线程/协程拥有独立的sid：

        不同的线程或协程会有不同的 _sid 值
        这意味着每个线程/协程在 globals.__data 中都有自己独立的数据存储空间
        数据隔离：

        虽然 globals 本身是全局单例，但每个线程/协程通过自己的 _sid 访问各自独立的数据
        这种设计实现了线程安全的同时，允许不同线程/协程拥有各自独立的上下文状态
        使用场景：

        这种机制特别适用于需要维护会话状态的场景，如聊天历史、参数设置等
        每个用户请求或任务可以在自己的会话上下文中独立运行，互不干扰
        因此，globals._sid 提供的是每个线程/协程独立的会话实例，而不是所有线程共享的唯一全局实例。
        """

        # 获取当前会话ID
        try:
            sid = self.__sid.get()
        except Exception:
            # 如果获取失败则重新初始化
            sid = self._init_sid()
        # 如果该会话ID不在数据中，则创建新的数据副本
        if sid not in self.__data:
            self.__data[sid] = copy.deepcopy(__class__.__global_attrs__)
        return sid

    @property
    def _data(self):
        # 返回当前会话的数据
        return self._get_data()

    def _get_data(self, rois: Optional[List[str]] = None) -> dict:
        # 根据指定的键列表获取数据
        if rois:
            assert isinstance(rois, (tuple, list))
            return {k: v for k, v in self.__data[self._sid].items() if k in rois}
        # 如果没有指定键列表，则返回所有数据
        return self.__data[self._sid]

    @property
    def _pickle_data(self):
        # 获取可序列化的数据，排除某些特定键
        exclude_keys = ['bind_args',]
        return {k: v for k, v in self._data.items() if k not in exclude_keys}

    def _update(self, d: Optional[Dict]) -> None:
        # 更新当前会话的数据
        if d:
            self._data.update(d)

    def __setitem__(self, __key: str, __value: Any):
        # 设置指定键的值
        self._data[__key] = __value

    def __getitem__(self, __key: str):
        # 获取指定键的值
        try:
            return self._data[__key]
        except KeyError:
            # 如果键不存在则抛出异常
            raise KeyError(f'Cannot find key {__key}, current session-id is {self._sid}')

    def get(self, __key: str, default: Any = None):
        # 获取指定键的值，如果不存在则返回默认值
        try:
            return self[__key]
        except KeyError:
            return default

    def __setattr__(self, __name: str, __value: Any):
        # 设置属性值
        if __name in __class__.__global_attrs__:
            # 如果是全局属性，则存储到数据中
            self[__name] = __value
        else:
            # 否则调用父类方法
            super(__class__, self).__setattr__(__name, __value)

    def __getattr__(self, __name: str) -> Any:
        # 获取属性值
        if __name in __class__.__global_attrs__:
            # 如果是全局属性，则从数据中获取
            return self[__name]
        # 如果不是全局属性则抛出异常
        raise AttributeError(f'Attr {__name} not found in globals')

    def clear(self):
        # 清除当前会话的数据
        self.__data.pop(self._sid, None)

    def _clear_all(self):
        # 清除所有会话的数据
        self.__data.clear()

    def __contains__(self, item):
        # 检查指定项是否在当前会话数据中
        return item in self.__data[self._sid]

    def pop(self, *args, **kw):
        # 弹出并返回指定键的值
        return self._data.pop(*args, **kw)

# 创建全局实例
globals = Globals()

@deprecated
class LazyLlmRequest(object):
    input: Any = package()
    kwargs: Any = kwargs()
    global_parameters: dict = dict()


@deprecated
class LazyLlmResponse(struct):
    messages: Any = None
    trace: str = ''
    err: Tuple[int, str] = (0, '')

    def __repr__(self): return repr(self.messages)
    def __str__(self): return str(self.messages)


def encode_request(input):
    return obj2str(input)


def decode_request(input, default=None):
    if input is None: return default
    return str2obj(input)
