import threading
from queue import Queue
import functools
from .globals import globals
from concurrent.futures import ThreadPoolExecutor as TPE

def _sid_setter(sid):
    globals._init_sid(sid)

class Thread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, prehook=None, daemon=None):
        self.q = Queue()
        if not isinstance(prehook, (tuple, list)): prehook = [prehook] if prehook else []
        prehook.insert(0, functools.partial(_sid_setter, sid=globals._sid))
        super().__init__(group, self.work, name, (prehook, target, args), kwargs, daemon=daemon)

    def work(self, prehook, target, args, **kw):
        [p() for p in prehook]
        try:
            r = target(*args, **kw)
        except Exception as e:
            self.q.put(e)
        else:
            self.q.put(r)

    def get_result(self):
        r = self.q.get()
        if isinstance(r, Exception):
            raise r
        return r


class ThreadPoolExecutor(TPE):
    """
    继承ThreadPoolExecutor的自定义线程池，主要区别是：在submit()的时候，初始化了sid全局变量
    """
    def submit(self, fn, /, *args, **kwargs):
        # 定义一个内部函数impl，用于包装原始函数fn
        def impl(sid, *a, **kw):
            # 初始化sid（会话ID）：首先尝试获取协程任务ID，如果失败则使用线程ID
            globals._init_sid(sid)
            # 调用原始函数fn，并传递参数
            return fn(*a, **kw)

        # 使用functools.partial将当前的sid绑定到impl函数上
        # 然后调用父类TPE的submit方法来提交这个部分应用的函数以及相关参数
        return super(__class__, self).submit(functools.partial(impl, globals._sid), *args, **kwargs)
