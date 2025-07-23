`lazyllm.module.ModuleBase`
---------------------------

Module是LazyLLM中的顶层组件，具备训练、部署、推理和评测四项关键能力，每个模块可以选择实现其中的部分或者全部的能力，每项能力都可以由一到多个Component组成。 ModuleBase本身不可以直接实例化，继承并实现 `forward` 函数的子类可以作为一个仿函数来使用。 类似pytorch的Moudule，当一个Module A持有了另一个Module B的实例作为成员变量时，会自动加入到submodule中。

如果你需要以下的能力，请让你自定义的类继承自ModuleBase:

1.  组合训练、部署、推理和评测的部分或全部能力，例如Embedding模型需要训练和推理
    
2.  持有的成员变量具备训练、部署和评测的部分或全部能力，并且想通过Module的根节点的 `start`, `update`, `eval` 等方法对其持有的成员进行训练、部署和评测时。
    
3.  将用户设置的参数从最外层直接传到你自定义的模块中（参考Tools.webpages.WebModule）
    
4.  希望能被参数网格搜索模块使用（参考TrialModule）
    

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> class  Module(lazyllm.module.ModuleBase): [](#__codelineno-0-3)...     pass [](#__codelineno-0-4)... [](#__codelineno-0-5)>>> class  Module2(lazyllm.module.ModuleBase): [](#__codelineno-0-6)...     def  __init__(self): [](#__codelineno-0-7)...         super(__class__, self).__init__() [](#__codelineno-0-8)...         self.m = Module() [](#__codelineno-0-9)... [](#__codelineno-0-10)>>> m = Module2() [](#__codelineno-0-11)>>> m.submodules [](#__codelineno-0-12)[<Module type=Module>] [](#__codelineno-0-13)>>> m.m3 = Module() [](#__codelineno-0-14)>>> m.submodules [](#__codelineno-0-15)[<Module type=Module>, <Module type=Module>]` 

Source code in `lazyllm/module/module.py`

|  | 

`class  ModuleBase(metaclass=_MetaBind):
 """Module是LazyLLM中的顶层组件，具备训练、部署、推理和评测四项关键能力，每个模块可以选择实现其中的部分或者全部的能力，每项能力都可以由一到多个Component组成。 ModuleBase本身不可以直接实例化，继承并实现 ``forward`` 函数的子类可以作为一个仿函数来使用。 类似pytorch的Moudule，当一个Module A持有了另一个Module B的实例作为成员变量时，会自动加入到submodule中。   如果你需要以下的能力，请让你自定义的类继承自ModuleBase:   1. 组合训练、部署、推理和评测的部分或全部能力，例如Embedding模型需要训练和推理   2. 持有的成员变量具备训练、部署和评测的部分或全部能力，并且想通过Module的根节点的 ``start``,  ``update``, ``eval`` 等方法对其持有的成员进行训练、部署和评测时。   3. 将用户设置的参数从最外层直接传到你自定义的模块中（参考Tools.webpages.WebModule）   4. 希望能被参数网格搜索模块使用（参考TrialModule）     Examples:
 >>> import lazyllm >>> class Module(lazyllm.module.ModuleBase): ...     pass ... >>> class Module2(lazyllm.module.ModuleBase): ...     def __init__(self): ...         super(__class__, self).__init__() ...         self.m = Module() ... >>> m = Module2() >>> m.submodules [<Module type=Module>] >>> m.m3 = Module() >>> m.submodules [<Module type=Module>, <Module type=Module>] """ builder_keys = []  # keys in builder support Option by default   def  __new__(cls, *args, **kw): sig = inspect.signature(cls.__init__) paras = sig.parameters values = list(paras.values())[1:]  # paras.value()[0] is self for i, p in enumerate(args): if isinstance(p, Option): ann = values[i].annotation assert ann == Option or (isinstance(ann, (tuple, list)) and Option in ann), \ f'{values[i].name} cannot accept Option' for k, v in kw.items(): if isinstance(v, Option): ann = paras[k].annotation assert ann == Option or (isinstance(ann, (tuple, list)) and Option in ann), \ f'{k} cannot accept Option' return object.__new__(cls)   def  __init__(self, *, return_trace=False): self._submodules = [] self._evalset = None self._return_trace = return_trace self.mode_list = ('train', 'server', 'eval') self._set_mid() self._used_by_moduleid = None self._module_name = None self._options = [] self.eval_result = None self._hooks = set()   def  __setattr__(self, name: str, value): if isinstance(value, ModuleBase): self._submodules.append(value) elif isinstance(value, Option): self._options.append(value) elif name.endswith('_args') and isinstance(value, dict): for v in value.values(): if isinstance(v, Option): self._options.append(v) return super().__setattr__(name, value)   def  __getattr__(self, key): def  _setattr(v, *, _return_value=self, **kw): k = key[:-7] if key.endswith('_method') else key if isinstance(v, tuple) and len(v) == 2 and isinstance(v[1], dict): kw.update(v[1]) v = v[0] if len(kw) > 0: setattr(self, f'_{k}_args', kw) setattr(self, f'_{k}', v) if hasattr(self, f'_{k}_setter_hook'): getattr(self, f'_{k}_setter_hook')() return _return_value keys = self.__class__.builder_keys if key in keys: return _setattr elif key.startswith('_') and key[1:] in keys: return None elif key.startswith('_') and key.endswith('_args') and (key[1:-5] in keys or f'{key[1:-4]}method' in keys): return dict() raise AttributeError(f'{self.__class__} object has no attribute {key}')   def  __call__(self, *args, **kw): hook_objs = [] for hook_type in self._hooks: if isinstance(hook_type, LazyLLMHook): hook_objs.append(copy.deepcopy(hook_type)) else: hook_objs.append(hook_type(self)) hook_objs[-1].pre_hook(*args, **kw) try: kw.update(globals['global_parameters'].get(self._module_id, dict())) if (files := globals['lazyllm_files'].get(self._module_id)) is not None: kw['lazyllm_files'] = files if (history := globals['chat_history'].get(self._module_id)) is not None: kw['llm_chat_history'] = history   r = self.forward(**args[0], **kw) if args and isinstance(args[0], kwargs) else self.forward(*args, **kw) if self._return_trace: lazyllm.FileSystemQueue.get_instance('lazy_trace').enqueue(str(r)) except Exception as e: raise RuntimeError( f"\nAn error occured in {self.__class__} with name {self.name}.\n" f"Args:\n{args}\nKwargs\n{kw}\nError messages:\n{e}\n" f"Original traceback:\n{''.join(traceback.format_tb(e.__traceback__))}") for hook_obj in hook_objs[::-1]: hook_obj.post_hook(r) for hook_obj in hook_objs: hook_obj.report() self._clear_usage() return r   def  _stream_output(self, text: str, color: Optional[str] = None, *, cls: Optional[str] = None): (FileSystemQueue.get_instance(cls) if cls else FileSystemQueue()).enqueue(colored_text(text, color)) return ''   @contextmanager def  stream_output(self, stream_output: Optional[Union[bool, Dict]] = None): if stream_output and isinstance(stream_output, dict) and (prefix := stream_output.get('prefix')): self._stream_output(prefix, stream_output.get('prefix_color')) yield if isinstance(stream_output, dict) and (suffix := stream_output.get('suffix')): self._stream_output(suffix, stream_output.get('suffix_color'))   def  used_by(self, module_id): self._used_by_moduleid = module_id return self   def  _clear_usage(self): globals["usage"].pop(self._module_id, None)   # interfaces def  forward(self, *args, **kw): """定义了每次执行的计算步骤，ModuleBase的所有的子类都需要重写这个函数。     Examples:
 >>> import lazyllm >>> class MyModule(lazyllm.module.ModuleBase): ...     def forward(self, input): ...         return input + 1 ... >>> MyModule()(1) 2 """ raise NotImplementedError   def  register_hook(self, hook_type: LazyLLMHook): self._hooks.add(hook_type)   def  unregister_hook(self, hook_type: LazyLLMHook): if hook_type in self._hooks: self._hooks.remove(hook_type)   def  clear_hooks(self): self._hooks = set()   def  _get_train_tasks(self): """定义训练任务，该函数返回训练的pipeline，重写了此函数的子类可以在update阶段被训练/微调。     Examples:
 >>> import lazyllm >>> class MyModule(lazyllm.module.ModuleBase): ...     def _get_train_tasks(self): ...         return lazyllm.pipeline(lambda : 1, lambda x: print(x)) ... >>> MyModule().update() 1 """ return None def  _get_deploy_tasks(self): """定义部署任务，该函数返回训练的pipeline，重写了此函数的子类可以在update/start阶段被部署。     Examples:
 >>> import lazyllm >>> class MyModule(lazyllm.module.ModuleBase): ...     def _get_deploy_tasks(self): ...         return lazyllm.pipeline(lambda : 1, lambda x: print(x)) ... >>> MyModule().start() 1 """ return None def  _get_post_process_tasks(self): return None   def  _set_mid(self, mid=None): self._module_id = mid if mid else str(uuid.uuid4().hex) return self   @property def  name(self): return self._module_name   @name.setter def  name(self, name): self._module_name = name   @property def  submodules(self): return self._submodules   def  evalset(self, evalset, load_f=None, collect_f=lambda x: x): """为Module设置评测集，设置过评测集的Module在 ``update`` 或 ``eval`` 的时候会进行评测，评测结果会存在eval_result变量中。     Examples:
 >>> import lazyllm >>> m = lazyllm.module.TrainableModule().deploy_method(lazyllm.deploy.dummy).finetune_method(lazyllm.finetune.dummy).trainset("").mode("finetune").prompt(None) >>> m.evalset([1, 2, 3]) >>> m.update() INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} >>> print(m.eval_result) ["reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1}"] """ if isinstance(evalset, str) and os.path.exists(evalset): with open(evalset) as f: assert callable(load_f) self._evalset = load_f(f) else: self._evalset = evalset self.eval_result_collet_f = collect_f   # TODO: add lazyllm.eval def  _get_eval_tasks(self): def  set_result(x): self.eval_result = x   def  parallel_infer(): with ThreadPoolExecutor(max_workers=200) as executor: results = list(executor.map(lambda item: self(**item) if isinstance(item, dict) else self(item), self._evalset)) return results if self._evalset: return Pipeline(parallel_infer, lambda x: self.eval_result_collet_f(x), set_result) return None   # update module(train or finetune), def  _update(self, *, mode=None, recursive=True):  # noqa C901 if not mode: mode = list(self.mode_list) if type(mode) is not list: mode = [mode] for item in mode: assert item in self.mode_list, f"Cannot find {item} in mode list: {self.mode_list}" # dfs to get all train tasks train_tasks, deploy_tasks, eval_tasks, post_process_tasks = FlatList(), FlatList(), FlatList(), FlatList() stack, visited = [(self, iter(self.submodules if recursive else []))], set() while len(stack) > 0: try: top = next(stack[-1][1]) stack.append((top, iter(top.submodules))) except StopIteration: top = stack.pop()[0] if top._module_id in visited: continue visited.add(top._module_id) if 'train' in mode: train_tasks.absorb(top._get_train_tasks()) if 'server' in mode: deploy_tasks.absorb(top._get_deploy_tasks()) if 'eval' in mode: eval_tasks.absorb(top._get_eval_tasks()) post_process_tasks.absorb(top._get_post_process_tasks())   if 'train' in mode and len(train_tasks) > 0: Parallel(*train_tasks).set_sync(True)() if 'server' in mode and len(deploy_tasks) > 0: if redis_client: Parallel(*deploy_tasks).set_sync(False)() else: Parallel.sequential(*deploy_tasks)() if 'eval' in mode and len(eval_tasks) > 0: Parallel.sequential(*eval_tasks)() Parallel.sequential(*post_process_tasks)() return self   def  update(self, *, recursive=True): """更新模块（及所有的子模块）。当模块重写了 ``_get_train_tasks`` 方法后，模块会被更新。更新完后会自动进入部署和推理的流程。   Args:
 recursive (bool): 是否递归更新所有的子模块，默认为True     Examples:
 >>> import lazyllm >>> m = lazyllm.module.TrainableModule().finetune_method(lazyllm.finetune.dummy).trainset("").deploy_method(lazyllm.deploy.dummy).mode('finetune').prompt(None) >>> m.evalset([1, 2, 3]) >>> m.update() INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} >>> print(m.eval_result) ["reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1}"] """ return self._update(mode=['train', 'server', 'eval'], recursive=recursive) def  update_server(self, *, recursive=True): return self._update(mode=['server'], recursive=recursive) def  eval(self, *, recursive=True): """对模块（及所有的子模块）进行评测。当模块通过 ``evalset`` 设置了评测集之后，本函数生效。   Args:
 recursive (bool): 是否递归评测所有的子模块，默认为True     Examples:
 >>> import lazyllm >>> class MyModule(lazyllm.module.ModuleBase): ...     def forward(self, input): ...         return f'reply for input' ... >>> m = MyModule() >>> m.evalset([1, 2, 3]) >>> m.eval().eval_result ['reply for input', 'reply for input', 'reply for input'] """ return self._update(mode=['eval'], recursive=recursive) def  start(self): """部署模块及所有的子模块     Examples:
 >>> import lazyllm >>> m = lazyllm.TrainableModule().deploy_method(lazyllm.deploy.dummy).prompt(None) >>> m.start() <Module type=Trainable mode=None basemodel= target= stream=False return_trace=False> >>> m(1) "reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}" """ return self._update(mode=['server'], recursive=True) def  restart(self): """重新重启模块及所有的子模块     Examples:
 >>> import lazyllm >>> m = lazyllm.TrainableModule().deploy_method(lazyllm.deploy.dummy).prompt(None) >>> m.restart() <Module type=Trainable mode=None basemodel= target= stream=False return_trace=False> >>> m(1) "reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}" """ return self.start() def  wait(self): pass   def  stop(self): for m in self.submodules: m.stop()   @property def  options(self): options = self._options.copy() for m in self.submodules: options += m.options return options   def  _overwrote(self, f): return getattr(self.__class__, f) is not getattr(__class__, f)   def  __repr__(self): return lazyllm.make_repr('Module', self.__class__, name=self.name)   def  for_each(self, filter, action): for submodule in self.submodules: if filter(submodule): action(submodule) submodule.for_each(filter, action)` 



 | 

### `_get_deploy_tasks()`

定义部署任务，该函数返回训练的pipeline，重写了此函数的子类可以在update/start阶段被部署。

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> class  MyModule(lazyllm.module.ModuleBase): [](#__codelineno-0-3)...     def  _get_deploy_tasks(self): [](#__codelineno-0-4)...         return lazyllm.pipeline(lambda : 1, lambda x: print(x)) [](#__codelineno-0-5)... [](#__codelineno-0-6)>>> MyModule().start() [](#__codelineno-0-7)1` 

Source code in `lazyllm/module/module.py`

|  | 

 `def  _get_deploy_tasks(self): """定义部署任务，该函数返回训练的pipeline，重写了此函数的子类可以在update/start阶段被部署。     Examples:
 >>> import lazyllm >>> class MyModule(lazyllm.module.ModuleBase): ...     def _get_deploy_tasks(self): ...         return lazyllm.pipeline(lambda : 1, lambda x: print(x)) ... >>> MyModule().start() 1 """ return None` 



 | 

### `_get_train_tasks()`

定义训练任务，该函数返回训练的pipeline，重写了此函数的子类可以在update阶段被训练/微调。

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> class  MyModule(lazyllm.module.ModuleBase): [](#__codelineno-0-3)...     def  _get_train_tasks(self): [](#__codelineno-0-4)...         return lazyllm.pipeline(lambda : 1, lambda x: print(x)) [](#__codelineno-0-5)... [](#__codelineno-0-6)>>> MyModule().update() [](#__codelineno-0-7)1` 

Source code in `lazyllm/module/module.py`

|  | 

 `def  _get_train_tasks(self): """定义训练任务，该函数返回训练的pipeline，重写了此函数的子类可以在update阶段被训练/微调。     Examples:
 >>> import lazyllm >>> class MyModule(lazyllm.module.ModuleBase): ...     def _get_train_tasks(self): ...         return lazyllm.pipeline(lambda : 1, lambda x: print(x)) ... >>> MyModule().update() 1 """ return None` 



 | 

### `eval(*, recursive=True)`

对模块（及所有的子模块）进行评测。当模块通过 `evalset` 设置了评测集之后，本函数生效。

Parameters:

*   **`recursive`** (`bool`, default: `True` ) –
    
    是否递归评测所有的子模块，默认为True
    

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> class  MyModule(lazyllm.module.ModuleBase): [](#__codelineno-0-3)...     def  forward(self, input): [](#__codelineno-0-4)...         return f'reply for input' [](#__codelineno-0-5)... [](#__codelineno-0-6)>>> m = MyModule() [](#__codelineno-0-7)>>> m.evalset([1, 2, 3]) [](#__codelineno-0-8)>>> m.eval().eval_result [](#__codelineno-0-9)['reply for input', 'reply for input', 'reply for input']` 

Source code in `lazyllm/module/module.py`

|  | 

 `def  eval(self, *, recursive=True): """对模块（及所有的子模块）进行评测。当模块通过 ``evalset`` 设置了评测集之后，本函数生效。   Args:
 recursive (bool): 是否递归评测所有的子模块，默认为True     Examples:
 >>> import lazyllm >>> class MyModule(lazyllm.module.ModuleBase): ...     def forward(self, input): ...         return f'reply for input' ... >>> m = MyModule() >>> m.evalset([1, 2, 3]) >>> m.eval().eval_result ['reply for input', 'reply for input', 'reply for input'] """ return self._update(mode=['eval'], recursive=recursive)` 



 | 

### `evalset(evalset, load_f=None, collect_f=lambda x: x)`

为Module设置评测集，设置过评测集的Module在 `update` 或 `eval` 的时候会进行评测，评测结果会存在eval\_result变量中。

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> m = lazyllm.module.TrainableModule().deploy_method(lazyllm.deploy.dummy).finetune_method(lazyllm.finetune.dummy).trainset("").mode("finetune").prompt(None) [](#__codelineno-0-3)>>> m.evalset([1, 2, 3]) [](#__codelineno-0-4)>>> m.update() [](#__codelineno-0-5)INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} [](#__codelineno-0-6)>>> print(m.eval_result) [](#__codelineno-0-7)["reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1}"]` 

Source code in `lazyllm/module/module.py`

|  | 

 `def  evalset(self, evalset, load_f=None, collect_f=lambda x: x): """为Module设置评测集，设置过评测集的Module在 ``update`` 或 ``eval`` 的时候会进行评测，评测结果会存在eval_result变量中。     Examples:
 >>> import lazyllm >>> m = lazyllm.module.TrainableModule().deploy_method(lazyllm.deploy.dummy).finetune_method(lazyllm.finetune.dummy).trainset("").mode("finetune").prompt(None) >>> m.evalset([1, 2, 3]) >>> m.update() INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} >>> print(m.eval_result) ["reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1}"] """ if isinstance(evalset, str) and os.path.exists(evalset): with open(evalset) as f: assert callable(load_f) self._evalset = load_f(f) else: self._evalset = evalset self.eval_result_collet_f = collect_f` 



 | 

### `forward(*args, **kw)`

定义了每次执行的计算步骤，ModuleBase的所有的子类都需要重写这个函数。

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> class  MyModule(lazyllm.module.ModuleBase): [](#__codelineno-0-3)...     def  forward(self, input): [](#__codelineno-0-4)...         return input + 1 [](#__codelineno-0-5)... [](#__codelineno-0-6)>>> MyModule()(1) [](#__codelineno-0-7)2` 

Source code in `lazyllm/module/module.py`

|  | 

 `def  forward(self, *args, **kw): """定义了每次执行的计算步骤，ModuleBase的所有的子类都需要重写这个函数。     Examples:
 >>> import lazyllm >>> class MyModule(lazyllm.module.ModuleBase): ...     def forward(self, input): ...         return input + 1 ... >>> MyModule()(1) 2 """ raise NotImplementedError` 



 | 

### `start()`

部署模块及所有的子模块

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> m = lazyllm.TrainableModule().deploy_method(lazyllm.deploy.dummy).prompt(None) [](#__codelineno-0-3)>>> m.start() [](#__codelineno-0-4)<Module type=Trainable mode=None basemodel= target= stream=False return_trace=False> [](#__codelineno-0-5)>>> m(1) [](#__codelineno-0-6)"reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}"` 

Source code in `lazyllm/module/module.py`

|  | 

 `def  start(self): """部署模块及所有的子模块     Examples:
 >>> import lazyllm >>> m = lazyllm.TrainableModule().deploy_method(lazyllm.deploy.dummy).prompt(None) >>> m.start() <Module type=Trainable mode=None basemodel= target= stream=False return_trace=False> >>> m(1) "reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}" """ return self._update(mode=['server'], recursive=True)` 



 | 

### `restart()`

重新重启模块及所有的子模块

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> m = lazyllm.TrainableModule().deploy_method(lazyllm.deploy.dummy).prompt(None) [](#__codelineno-0-3)>>> m.restart() [](#__codelineno-0-4)<Module type=Trainable mode=None basemodel= target= stream=False return_trace=False> [](#__codelineno-0-5)>>> m(1) [](#__codelineno-0-6)"reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}"` 

Source code in `lazyllm/module/module.py`

|  | 

 `def  restart(self): """重新重启模块及所有的子模块     Examples:
 >>> import lazyllm >>> m = lazyllm.TrainableModule().deploy_method(lazyllm.deploy.dummy).prompt(None) >>> m.restart() <Module type=Trainable mode=None basemodel= target= stream=False return_trace=False> >>> m(1) "reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}" """ return self.start()` 



 | 

### `update(*, recursive=True)`

更新模块（及所有的子模块）。当模块重写了 `_get_train_tasks` 方法后，模块会被更新。更新完后会自动进入部署和推理的流程。

Parameters:

*   **`recursive`** (`bool`, default: `True` ) –
    
    是否递归更新所有的子模块，默认为True
    

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> m = lazyllm.module.TrainableModule().finetune_method(lazyllm.finetune.dummy).trainset("").deploy_method(lazyllm.deploy.dummy).mode('finetune').prompt(None) [](#__codelineno-0-3)>>> m.evalset([1, 2, 3]) [](#__codelineno-0-4)>>> m.update() [](#__codelineno-0-5)INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} [](#__codelineno-0-6)>>> print(m.eval_result) [](#__codelineno-0-7)["reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1}"]` 

Source code in `lazyllm/module/module.py`

|  | 

 `def  update(self, *, recursive=True): """更新模块（及所有的子模块）。当模块重写了 ``_get_train_tasks`` 方法后，模块会被更新。更新完后会自动进入部署和推理的流程。   Args:
 recursive (bool): 是否递归更新所有的子模块，默认为True     Examples:
 >>> import lazyllm >>> m = lazyllm.module.TrainableModule().finetune_method(lazyllm.finetune.dummy).trainset("").deploy_method(lazyllm.deploy.dummy).mode('finetune').prompt(None) >>> m.evalset([1, 2, 3]) >>> m.update() INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} >>> print(m.eval_result) ["reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1}"] """ return self._update(mode=['train', 'server', 'eval'], recursive=recursive)` 



 | 

`lazyllm.module.ActionModule`
-----------------------------

Bases: `[ModuleBase](#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase (lazyllm.module.module.ModuleBase)")`

用于将函数、模块、flow、Module等可调用的对象包装一个Module。被包装的Module（包括flow中的Module）都会变成该Module的submodule。

Parameters:

*   **`action`** (`Callable | list[Callable]`, default: `()` ) –
    
    被包装的对象，是一个或一组可执行的对象。
    

Source code in `lazyllm/module/module.py`

|  | 

`class  ActionModule(ModuleBase):
 """用于将函数、模块、flow、Module等可调用的对象包装一个Module。被包装的Module（包括flow中的Module）都会变成该Module的submodule。   Args:
 action (Callable|list[Callable]): 被包装的对象，是一个或一组可执行的对象。 """
 def  __init__(self, *action, return_trace=False): super().__init__(return_trace=return_trace) if len(action) == 1 and isinstance(action, FlowBase): action = action[0] if isinstance(action, (tuple, list)): action = Pipeline(*action) assert isinstance(action, FlowBase), f'Invalid action type {type(action)}' self.action = action   def  forward(self, *args, **kw): return self.action(*args, **kw)   @property def  submodules(self): try: if isinstance(self.action, FlowBase): submodule = [] self.action.for_each(lambda x: isinstance(x, ModuleBase), lambda x: submodule.append(x)) return submodule except Exception as e: raise RuntimeError(f"{str(e)}\nOriginal traceback:\n{''.join(traceback.format_tb(e.__traceback__))}") return super().submodules   def  __repr__(self): return lazyllm.make_repr('Module', 'Action', subs=[repr(self.action)], name=self._module_name, return_trace=self._return_trace)` 



 | 

`lazyllm.module.TrainableModule`
--------------------------------

Bases: `[UrlModule](#lazyllm.module.UrlModule "            lazyllm.module.UrlModule (lazyllm.module.servermodule.UrlModule)")`

可训练模块，所有模型（包括LLM、Embedding等）都通过TrainableModule提供服务

**`TrainableModule(base_model='', target_path='', *, stream=False, return_trace=False)`**

Parameters:

*   **`base_model`** (`str`, default: `''` ) –
    
    基础模型的名称或路径。如果本地没有该模型，将会自动从模型源下载。
    
*   **`target_path`** (`str`, default: `''` ) –
    
    保存微调任务的路径。如果仅进行推理，可以留空。
    
*   **`source`** (`str`) –
    
    模型来源，可选值为huggingface或...。如果未设置，将从环境变量LAZYLLM\_MODEL\_SOURCE读取。
    
*   **`stream`** (`bool`, default: `False` ) –
    
    是否输出流式结果。如果使用的推理引擎不支持流式输出，该参数将被忽略。
    
*   **`return_trace`** (`bool`, default: `False` ) –
    
    是否在trace中记录结果。
    

**`TrainableModule.trainset(v):`**

设置 TrainableModule 的训练集

Parameters:

*   **`v`** (`str`) –
    
    训练/微调数据集的路径
    

**示例:**

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> m = lazyllm.module.TrainableModule().finetune_method(finetune.dummy).trainset('/file/to/path').deploy_method(None).mode('finetune') [](#__codelineno-0-3)>>> m.update() [](#__codelineno-0-4)INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {}` 

**`TrainableModule.train_method(v, **kw):`**

设置 TrainableModule 的训练方法（暂不支持继续预训练，预计下一版本支持）

Parameters:

*   **`v`** (`LazyLLMTrainBase`) –
    
    训练方法，可选值包括 `train.auto` 等
    
*   **`kw`** (`**dict`) –
    
    训练方法所需的参数，对应 v 的参数
    

**`TrainableModule.finetune_method(v, **kw):`**

设置 TrainableModule 的微调方法及其参数

Parameters:

*   **`v`** (`LazyLLMFinetuneBase`) –
    
    微调方法，可选值包括 `finetune.auto` / `finetune.alpacalora` / `finetune.collie` 等
    
*   **`kw`** (`**dict`) –
    
    微调方法所需的参数，对应 v 的参数
    

**示例:**

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> m = lazyllm.module.TrainableModule().finetune_method(finetune.dummy).deploy_method(None).mode('finetune') [](#__codelineno-0-3)>>> m.update() [](#__codelineno-0-4)INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {}` 

**`TrainableModule.deploy_method(v, **kw):`**

设置 TrainableModule 的部署方法及其参数

Parameters:

*   **`v`** (`LazyLLMDeployBase`) –
    
    部署方法，可选值包括 `deploy.auto` / `deploy.lightllm` / `deploy.vllm` 等
    
*   **`kw`** (`**dict`) –
    
    部署方法所需的参数，对应 v 的参数
    

**示例:**

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> m = lazyllm.module.TrainableModule().deploy_method(deploy.dummy).mode('finetune') [](#__codelineno-0-3)>>> m.evalset([1, 2, 3]) [](#__codelineno-0-4)>>> m.update() [](#__codelineno-0-5)INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} [](#__codelineno-0-6)>>> m.eval_result [](#__codelineno-0-7)["reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1}"]` 

**`TrainableModule.mode(v):`**

设置 TrainableModule 在 update 时执行训练还是微调

Parameters:

*   **`v`** (`str`) –
    
    设置在 update 时执行训练还是微调，可选值为 'finetune' 和 'train'，默认为 'finetune'
    

**示例:**

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> m = lazyllm.module.TrainableModule().finetune_method(finetune.dummy).deploy_method(None).mode('finetune') [](#__codelineno-0-3)>>> m.update() [](#__codelineno-0-4)INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {}` 

**`eval(*, recursive=True)`** 评估该模块（及其所有子模块）。此功能需在模块通过evalset设置评估集后生效。

Parameters:

*   **`recursive`** (`bool)` ) –
    
    是否递归评估所有子模块，默认为True。
    

**`evalset(evalset, load_f=None, collect_f=<function ModuleBase.<lambda>>)`**

为模块设置评估集。已设置评估集的模块将在执行`update`或`eval`时进行评估，评估结果将存储在eval\_result变量中。

 **`evalset(evalset, collect_f=lambda x: ...)→ None`**

Parameters:

*   **`evalset`** (`list)` ) –
    
    评估数据集
    
*   **`collect_f`** (`Callable)` ) –
    
    评估结果的后处理方法，默认不进行后处理。
    

 **`evalset(evalset, load_f=None, collect_f=lambda x: ...)→ None`**

Parameters:

*   **`evalset`** (`str)` ) –
    
    评估集路径
    
*   **`load_f`** (`Callable)` ) –
    
    评估集加载方法，包括文件格式解析和列表转换
    
*   **`collect_f`** (`Callable)` ) –
    
    评估结果后处理方法，默认不进行后处理
    

**示例:**

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> m = lazyllm.module.TrainableModule().deploy_method(deploy.dummy) [](#__codelineno-0-3)>>> m.evalset([1, 2, 3]) [](#__codelineno-0-4)>>> m.update() [](#__codelineno-0-5)INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} [](#__codelineno-0-6)>>> m.eval_result [](#__codelineno-0-7)["reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1}"]` 

**`restart()`**

重启模块及其所有子模块

**示例:**

`[](#__codelineno-1-1)>>> import  lazyllm [](#__codelineno-1-2)>>> m = lazyllm.module.TrainableModule().deploy_method(deploy.dummy) [](#__codelineno-1-3)>>> m.restart() [](#__codelineno-1-4)>>> m(1) [](#__codelineno-1-5)"reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}"` 

start()

部署模块及其所有子模块

**示例:**

`[](#__codelineno-2-1)>>> import  lazyllm [](#__codelineno-2-2)>>> m = lazyllm.module.TrainableModule().deploy_method(deploy.dummy) [](#__codelineno-2-3)>>> m.start() [](#__codelineno-2-4)>>> m(1) [](#__codelineno-2-5)"reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}"` 

Source code in `lazyllm/module/llms/trainablemodule.py`

|  | 

````class  TrainableModule(UrlModule):
 """可训练模块，所有模型（包括LLM、Embedding等）都通过TrainableModule提供服务   <span style="font-size: 20px;">**`TrainableModule(base_model='', target_path='', *, stream=False, return_trace=False)`**</span>     Args:
 base_model (str): 基础模型的名称或路径。如果本地没有该模型，将会自动从模型源下载。 target_path (str): 保存微调任务的路径。如果仅进行推理，可以留空。 source (str): 模型来源，可选值为huggingface或...。如果未设置，将从环境变量LAZYLLM_MODEL_SOURCE读取。 stream (bool): 是否输出流式结果。如果使用的推理引擎不支持流式输出，该参数将被忽略。 return_trace (bool): 是否在trace中记录结果。   <span style="font-size: 20px;">**`TrainableModule.trainset(v):`**</span>   设置 TrainableModule 的训练集   Args:
 v (str): 训练/微调数据集的路径   **示例:**   ```python >>> import lazyllm >>> m = lazyllm.module.TrainableModule().finetune_method(finetune.dummy).trainset('/file/to/path').deploy_method(None).mode('finetune') >>> m.update() INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} ```   <span style="font-size: 20px;">**`TrainableModule.train_method(v, **kw):`**</span>   设置 TrainableModule 的训练方法（暂不支持继续预训练，预计下一版本支持）   Args:
 v (LazyLLMTrainBase): 训练方法，可选值包括 ``train.auto`` 等 kw (**dict): 训练方法所需的参数，对应 v 的参数   <span style="font-size: 20px;">**`TrainableModule.finetune_method(v, **kw):`**</span>   设置 TrainableModule 的微调方法及其参数   Args:
 v (LazyLLMFinetuneBase): 微调方法，可选值包括 ``finetune.auto`` / ``finetune.alpacalora`` / ``finetune.collie`` 等 kw (**dict): 微调方法所需的参数，对应 v 的参数   **示例:**   ```python >>> import lazyllm >>> m = lazyllm.module.TrainableModule().finetune_method(finetune.dummy).deploy_method(None).mode('finetune') >>> m.update() INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} ```   <span style="font-size: 20px;">**`TrainableModule.deploy_method(v, **kw):`**</span>   设置 TrainableModule 的部署方法及其参数   Args:
 v (LazyLLMDeployBase): 部署方法，可选值包括 ``deploy.auto`` / ``deploy.lightllm`` / ``deploy.vllm`` 等 kw (**dict): 部署方法所需的参数，对应 v 的参数   **示例:**   ```python >>> import lazyllm >>> m = lazyllm.module.TrainableModule().deploy_method(deploy.dummy).mode('finetune') >>> m.evalset([1, 2, 3]) >>> m.update() INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} >>> m.eval_result ["reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1}"] ```   <span style="font-size: 20px;">**`TrainableModule.mode(v):`**</span>   设置 TrainableModule 在 update 时执行训练还是微调   Args:
 v (str): 设置在 update 时执行训练还是微调，可选值为 'finetune' 和 'train'，默认为 'finetune'   **示例:**   ```python >>> import lazyllm >>> m = lazyllm.module.TrainableModule().finetune_method(finetune.dummy).deploy_method(None).mode('finetune') >>> m.update() INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} ``` <span style="font-size: 20px;">**`eval(*, recursive=True)`**</span> 评估该模块（及其所有子模块）。此功能需在模块通过evalset设置评估集后生效。   Args:
 recursive (bool) :是否递归评估所有子模块，默认为True。   <span style="font-size: 20px;">**`evalset(evalset, load_f=None, collect_f=<function ModuleBase.<lambda>>)`**</span>   为模块设置评估集。已设置评估集的模块将在执行``update``或``eval``时进行评估，评估结果将存储在eval_result变量中。   <span style="font-size: 18px;">&ensp;**`evalset(evalset, collect_f=lambda x: ...)→ None `**</span>     Args:
 evalset (list) :评估数据集 collect_f (Callable) :评估结果的后处理方法，默认不进行后处理。       <span style="font-size: 18px;">&ensp;**`evalset(evalset, load_f=None, collect_f=lambda x: ...)→ None`**</span>     Args:
 evalset (str) :评估集路径 load_f (Callable) :评估集加载方法，包括文件格式解析和列表转换 collect_f (Callable) :评估结果后处理方法，默认不进行后处理   **示例:**   ```python >>> import lazyllm >>> m = lazyllm.module.TrainableModule().deploy_method(deploy.dummy) >>> m.evalset([1, 2, 3]) >>> m.update() INFO: (lazyllm.launcher) PID: dummy finetune!, and init-args is {} >>> m.eval_result ["reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1}", "reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1}"] ```   <span style="font-size: 20px;">**`restart() `**</span>   重启模块及其所有子模块   **示例:**   ```python >>> import lazyllm >>> m = lazyllm.module.TrainableModule().deploy_method(deploy.dummy) >>> m.restart() >>> m(1) "reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}" ```   <span style="font-size: 20px;">start() </span>   部署模块及其所有子模块   **示例:**   ```python >>> import lazyllm >>> m = lazyllm.module.TrainableModule().deploy_method(deploy.dummy) >>> m.start() >>> m(1) "reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1}" ```   """
 builder_keys = _TrainableModuleImpl.builder_keys   def  __init__(self, base_model: Option = '', target_path='', *, stream: Union[bool, Dict[str, str]] = False, return_trace: bool = False, trust_remote_code: bool = True): super().__init__(url=None, stream=stream, return_trace=return_trace, init_prompt=False) self._template = _UrlTemplateStruct() self._impl = _TrainableModuleImpl(base_model, target_path, stream, None, lazyllm.finetune.auto, lazyllm.deploy.auto, self._template, self._url_wrapper, trust_remote_code) self._stream = stream self.prompt()   template_message = property(lambda self: self._template.template_message) keys_name_handle = property(lambda self: self._template.keys_name_handle) template_headers = property(lambda self: self._template.template_headers) extract_result_func = property(lambda self: self._template.extract_result_func) stream_parse_parameters = property(lambda self: self._template.stream_parse_parameters) stream_url_suffix = property(lambda self: self._template.stream_url_suffix)   base_model = property(lambda self: self._impl._base_model) target_path = property(lambda self: self._impl._target_path) finetuned_model_path = property(lambda self: self._impl._finetuned_model_path) _url_id = property(lambda self: self._impl._module_id)   @property def  series(self): return re.sub(r'\d+$', '', ModelManager.get_model_name(self.base_model).split('-')[0].upper())   @property def  type(self): return ModelManager.get_model_type(self.base_model).upper()   def  get_all_models(self): return self._impl._get_all_finetuned_models()   def  set_specific_finetuned_model(self, model_path): return self._impl._set_specific_finetuned_model(model_path)   @property def  _deploy_type(self): if self._impl._deploy is not lazyllm.deploy.AutoDeploy: return self._impl._deploy elif self._impl._deployer: return type(self._impl._deployer) else: return lazyllm.deploy.AutoDeploy   def  wait(self): if launcher := self._impl._launchers['default'].get('deploy'): launcher.wait()   def  stop(self, task_name: Optional[str] = None): try: launcher = self._impl._launchers['manual' if task_name else 'default'][task_name or 'deploy'] except KeyError: raise RuntimeError('Cannot stop an unstarted task') if not task_name: self._impl._get_deploy_tasks.flag.reset() launcher.cleanup()   def  status(self, task_name: Optional[str] = None): launcher = self._impl._launchers['manual' if task_name else 'default'][task_name or 'deploy'] return launcher.status   # modify default value to '' def  prompt(self, prompt: Union[str, dict] = '', history: Optional[List[List[str]]] = None): if self.base_model != '' and prompt == '' and ModelManager.get_model_type(self.base_model) != 'llm': prompt = None clear_system = isinstance(prompt, dict) and prompt.get('drop_builtin_system') prompter = super(__class__, self).prompt(prompt, history)._prompt self._tools = getattr(prompter, "_tools", None) keys = ModelManager.get_model_prompt_keys(self.base_model).copy() if keys: if clear_system: keys['system'] = '' prompter._set_model_configs(**keys) for key in ["tool_start_token", "tool_args_token", "tool_end_token"]: if key in keys: setattr(self, f"_{key}", keys[key]) return self   def  _loads_str(self, text: str) -> Union[str, Dict]: try: ret = json.loads(text) return self._loads_str(ret) if isinstance(ret, str) else ret except Exception: LOG.error(f"{text} is not a valid json string.") return text   def  _parse_arguments_with_args_token(self, output: str) -> tuple[str, dict]: items = output.split(self._tool_args_token) func_name = items[0].strip() if len(items) == 1: return func_name.split(self._tool_end_token)[0].strip() if getattr(self, "_tool_end_token", None)\ else func_name, {} args = (items[1].split(self._tool_end_token)[0].strip() if getattr(self, "_tool_end_token", None) else items[1].strip()) return func_name, self._loads_str(args) if isinstance(args, str) else args   def  _parse_arguments_without_args_token(self, output: str) -> tuple[str, dict]: items = output.split(self._tool_end_token)[0] if getattr(self, "_tool_end_token", None) else output func_name = "" args = {} try: items = json.loads(items.strip()) func_name = items.get('name', '') args = items.get("parameters", items.get("arguments", {})) except Exception: LOG.error(f"tool calls info {items} parse error")   return func_name, self._loads_str(args) if isinstance(args, str) else args   def  _parse_arguments_with_tools(self, output: Dict[str, Any], tools: List[str]) -> bool: func_name = '' args = {} is_tc = False tc = {} if output.get('name', '') in tools: is_tc = True func_name = output.get('name', '') args = output.get("parameters", output.get("arguments", {})) tc = {'name': func_name, 'arguments': self._loads_str(args) if isinstance(args, str) else args} return is_tc, tc return is_tc, tc   def  _parse_tool_start_token(self, output: str) -> tuple[str, List[Dict]]: tool_calls = [] segs = output.split(self._tool_start_token) content = segs[0] for seg in segs[1:]: func_name, arguments = self._parse_arguments_with_args_token(seg.strip())\ if getattr(self, "_tool_args_token", None)\ else self._parse_arguments_without_args_token(seg.strip()) if func_name: tool_calls.append({"name": func_name, "arguments": arguments})   return content, tool_calls   def  _parse_tools(self, output: str) -> tuple[str, List[Dict]]: tool_calls = [] tools = {tool['function']['name'] for tool in self._tools} lines = output.strip().split("\n") content = [] is_tool_call = False for idx, line in enumerate(lines): if line.startswith("{") and idx > 0: func_name = lines[idx - 1].strip() if func_name in tools: is_tool_call = True if func_name == content[-1].strip(): content.pop() arguments = "\n".join(lines[idx:]).strip() tool_calls.append({'name': func_name, "arguments": arguments}) continue if "{" in line and 'name' in line: try: items = json.loads(line.strip()) items = [items] if isinstance(items, dict) else items if isinstance(items, list): for item in items: is_tool_call, tc = self._parse_arguments_with_tools(item, tools) if is_tool_call: tool_calls.append(tc) except Exception: LOG.error(f"tool calls info {line} parse error") if not is_tool_call: content.append(line) content = "\n".join(content) if len(content) > 0 else '' return content, tool_calls   def  _extract_tool_calls(self, output: str) -> tuple[str, List[Dict]]: tool_calls = [] content = '' if getattr(self, "_tool_start_token", None) and self._tool_start_token in output: content, tool_calls = self._parse_tool_start_token(output) elif self._tools: content, tool_calls = self._parse_tools(output) else: content = output   return content, tool_calls   def  _decode_base64_to_file(self, content: str) -> str: decontent = decode_query_with_filepaths(content) files = [base64_to_file(file_content) if is_base64_with_mime(file_content) else file_content for file_content in decontent["files"]] return encode_query_with_filepaths(query=decontent["query"], files=files)   def  _build_response(self, content: str, tool_calls: List[Dict[str, str]]) -> str: tc = [{'id': str(uuid.uuid4().hex), 'type': 'function', 'function': tool_call} for tool_call in tool_calls] if content and tc: return globals["tool_delimiter"].join([content, json.dumps(tc, ensure_ascii=False)]) elif not content and tc: return globals["tool_delimiter"] + json.dumps(tc, ensure_ascii=False) else: return content   def  _extract_and_format(self, output: str) -> str: """ 1.extract tool calls information; a. If 'tool_start_token' exists, the boundary of tool_calls can be found according to 'tool_start_token', and then the function name and arguments of tool_calls can be extracted according to 'tool_args_token' and 'tool_end_token'. b. If 'tool_start_token' does not exist, the text is segmented using '\n' according to the incoming tools information, and then processed according to the rules. """ content, tool_calls = self._extract_tool_calls(output) if isinstance(content, str) and content.startswith(LAZYLLM_QUERY_PREFIX): content = self._decode_base64_to_file(content) return self._build_response(content, tool_calls)   def  __repr__(self): return lazyllm.make_repr('Module', 'Trainable', mode=self._impl._mode, basemodel=self.base_model, target=self.target_path, name=self._module_name, deploy_type=self._deploy_type, stream=bool(self._stream), return_trace=self._return_trace)   def  __getattr__(self, key): if key in self.__class__.builder_keys: return functools.partial(getattr(self._impl, key), _return_value=self) raise AttributeError(f'{__class__} object has no attribute {key}')   def  _record_usage(self, text_input_for_token_usage: str, temp_output: str): usage = {"prompt_tokens": self._estimate_token_usage(text_input_for_token_usage)} usage["completion_tokens"] = self._estimate_token_usage(temp_output) self._record_usage_impl(usage)   def  _record_usage_impl(self, usage: dict): globals["usage"][self._module_id] = usage par_muduleid = self._used_by_moduleid if par_muduleid is None: return if par_muduleid not in globals["usage"]: globals["usage"][par_muduleid] = usage return existing_usage = globals["usage"][par_muduleid] if existing_usage["prompt_tokens"] == -1 or usage["prompt_tokens"] == -1: globals["usage"][par_muduleid] = {"prompt_tokens": -1, "completion_tokens": -1} else: for k in globals["usage"][par_muduleid]: globals["usage"][par_muduleid][k] += usage[k]   def  forward(self, __input: Union[Tuple[Union[str, Dict], str], str, Dict] = package(), *, llm_chat_history=None, lazyllm_files=None, tools=None, stream_output=False, **kw): __input, files = self._get_files(__input, lazyllm_files) text_input_for_token_usage = __input = self._prompt.generate_prompt(__input, llm_chat_history, tools) url = self._url   if self.template_message: data = self._modify_parameters(copy.deepcopy(self.template_message), kw, optional_keys='modality') data[self.keys_name_handle.get('inputs', 'inputs')] = __input if files and (keys := list(set(self.keys_name_handle).intersection(LazyLLMDeployBase.encoder_map.keys()))): assert len(keys) == 1, 'Only one key is supported for encoder_mapping' data[self.keys_name_handle[keys[0]]] = encode_files(files, LazyLLMDeployBase.encoder_map[keys[0]])   if stream_output: if self.stream_url_suffix and not url.endswith(self.stream_url_suffix): url += self.stream_url_suffix if "stream" in data: data['stream'] = stream_output else: data = __input if stream_output: LOG.warning('stream_output is not supported when template_message is not set, ignore it') assert not kw, 'kw is not supported when template_message is not set'   with self.stream_output((stream_output := (stream_output or self._stream))): return self._forward_impl(data, stream_output=stream_output, url=url, text_input=text_input_for_token_usage)   def  _maybe_has_fc(self, token: str, chunk: str) -> bool: return token and (token.startswith(chunk if token.startswith('\n') else chunk.lstrip('\n')) or token in chunk)   def  _forward_impl(self, data: Union[Tuple[Union[str, Dict], str], str, Dict] = package(), *, url: str, stream_output: Optional[Union[bool, Dict]] = None, text_input: Optional[str] = None): headers = self.template_headers or {'Content-Type': 'application/json'} parse_parameters = self.stream_parse_parameters if stream_output else {"delimiter": b"<|lazyllm_delimiter|>"}   # context bug with httpx, so we use requests with requests.post(url, json=data, stream=True, headers=headers, proxies={'http': None, 'https': None}) as r: if r.status_code != 200: raise requests.RequestException('\n'.join([c.decode('utf-8') for c in r.iter_content(None)]))   messages, cache = '', '' token = getattr(self, "_tool_start_token", '') color = stream_output.get('color') if isinstance(stream_output, dict) else None   for line in r.iter_lines(**parse_parameters): if not line: continue line = self._decode_line(line)   chunk = self._prompt.get_response(self.extract_result_func(line, data)) chunk = chunk[len(messages):] if isinstance(chunk, str) and chunk.startswith(messages) else chunk messages = chunk if not isinstance(chunk, str) else messages + chunk   if not stream_output: continue if not cache: cache = chunk if self._maybe_has_fc(token, chunk) else self._stream_output(chunk, color) elif token in cache: stream_output = False if not cache.startswith(token): self._stream_output(cache.split(token)[0], color) else: cache += chunk if not self._maybe_has_fc(token, cache): cache = self._stream_output(cache, color)   temp_output = self._extract_and_format(messages) if text_input: self._record_usage(text_input, temp_output) return self._formatter(temp_output)   def  _modify_parameters(self, paras: dict, kw: dict, *, optional_keys: Union[List[str], str] = []): for key, value in paras.items(): if key == self.keys_name_handle['inputs']: continue elif isinstance(value, dict): if key in kw: assert set(kw[key].keys()).issubset(set(value.keys())) value.update(kw.pop(key)) else: [setattr(value, k, kw.pop(k)) for k in value.keys() if k in kw] elif key in kw: paras[key] = kw.pop(key)   if isinstance(optional_keys, str): optional_keys = [optional_keys] assert set(kw.keys()).issubset(set(optional_keys)), f'{kw.keys()} is not in {optional_keys}' paras.update(kw) return paras   def  set_default_parameters(self, *, optional_keys: List[str] = [], **kw): self._modify_parameters(self.template_message, kw, optional_keys=optional_keys)```` 



 | 

`lazyllm.module.UrlModule`
--------------------------

Bases: `LLMBase`, `_UrlHelper`

可以将ServerModule部署得到的Url包装成一个Module，调用 `__call__` 时会访问该服务。

Parameters:

*   **`url`** (`str`, default: `''` ) –
    
    要包装的服务的Url
    
*   **`stream`** (`bool`, default: `False` ) –
    
    是否流式请求和输出，默认为非流式
    
*   **`return_trace`** (`bool`, default: `False` ) –
    
    是否将结果记录在trace中，默认为False
    

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> def  demo(input): return input * 2 [](#__codelineno-0-3)... [](#__codelineno-0-4)>>> s = lazyllm.ServerModule(demo, launcher=lazyllm.launchers.empty(sync=False)) [](#__codelineno-0-5)>>> s.start() [](#__codelineno-0-6)INFO:     Uvicorn running on http://0.0.0.0:35485 [](#__codelineno-0-7)>>> u = lazyllm.UrlModule(url=s._url) [](#__codelineno-0-8)>>> print(u(1)) [](#__codelineno-0-9)2` 

Source code in `lazyllm/module/servermodule.py`

|  | 

`class  UrlModule(LLMBase, _UrlHelper):
 """可以将ServerModule部署得到的Url包装成一个Module，调用 ``__call__`` 时会访问该服务。   Args:
 url (str): 要包装的服务的Url stream (bool): 是否流式请求和输出，默认为非流式 return_trace (bool): 是否将结果记录在trace中，默认为False     Examples:
 >>> import lazyllm >>> def demo(input): return input * 2 ... >>> s = lazyllm.ServerModule(demo, launcher=lazyllm.launchers.empty(sync=False)) >>> s.start() INFO:     Uvicorn running on http://0.0.0.0:35485 >>> u = lazyllm.UrlModule(url=s._url) >>> print(u(1)) 2 """   def  __new__(cls, *args, **kw): if cls is not UrlModule: return super().__new__(cls) return ServerModule(*args, **kw)   def  __init__(self, *, url: Optional[str] = '', stream: Union[bool, Dict[str, str]] = False, return_trace: bool = False, init_prompt: bool = True): super().__init__(stream=stream, return_trace=return_trace, init_prompt=init_prompt) _UrlHelper.__init__(self, url)   def  _estimate_token_usage(self, text): if not isinstance(text, str): return 0 # extract english words, number and comma pattern = r"\b[a-zA-Z0-9]+\b|," ascii_words = re.findall(pattern, text) ascii_ch_count = sum(len(ele) for ele in ascii_words) non_ascii_pattern = r"[^\x00-\x7F]" non_ascii_chars = re.findall(non_ascii_pattern, text) non_ascii_char_count = len(non_ascii_chars) return int(ascii_ch_count / 3.0 + non_ascii_char_count + 1)   def  _decode_line(self, line: bytes): try: return pickle.loads(codecs.decode(line, "base64")) except Exception: return line.decode('utf-8')   def  _extract_and_format(self, output: str) -> str: return output   def  forward(self, *args, **kw): """定义了每次执行的计算步骤，ModuleBase的所有的子类都需要重写这个函数。     Examples:
 >>> import lazyllm >>> class MyModule(lazyllm.module.ModuleBase): ...    def forward(self, input): ...        return input + 1 ... >>> MyModule()(1) 2 """ raise NotImplementedError   def  __call__(self, *args, **kw): assert self._url is not None, f'Please start {self.__class__} first' if len(args) > 1: return super(__class__, self).__call__(package(args), **kw) return super(__class__, self).__call__(*args, **kw)   def  __repr__(self): return lazyllm.make_repr('Module', 'Url', name=self._module_name, url=self._url, stream=self._stream, return_trace=self._return_trace)` 



 | 

### `forward(*args, **kw)`

定义了每次执行的计算步骤，ModuleBase的所有的子类都需要重写这个函数。

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> class  MyModule(lazyllm.module.ModuleBase): [](#__codelineno-0-3)...    def  forward(self, input): [](#__codelineno-0-4)...        return input + 1 [](#__codelineno-0-5)... [](#__codelineno-0-6)>>> MyModule()(1) [](#__codelineno-0-7)2` 

Source code in `lazyllm/module/servermodule.py`

|  | 

 `def  forward(self, *args, **kw): """定义了每次执行的计算步骤，ModuleBase的所有的子类都需要重写这个函数。     Examples:
 >>> import lazyllm >>> class MyModule(lazyllm.module.ModuleBase): ...    def forward(self, input): ...        return input + 1 ... >>> MyModule()(1) 2 """ raise NotImplementedError` 



 | 

`lazyllm.module.ServerModule`
-----------------------------

Bases: `[UrlModule](#lazyllm.module.UrlModule "            lazyllm.module.UrlModule (lazyllm.module.servermodule.UrlModule)")`

借助 fastapi，将任意可调用对象包装成 api 服务，可同时启动一个主服务和多个卫星服务。

Parameters:

*   **`m`** (`Callable`, default: `None` ) –
    
    被包装成服务的函数，可以是一个函数，也可以是一个仿函数。当启动卫星服务时，需要是一个实现了 `__call__` 的对象（仿函数）。
    
*   **`pre`** (`Callable`, default: `None` ) –
    
    前处理函数，在服务进程执行，可以是一个函数，也可以是一个仿函数，默认为 `None`。
    
*   **`post`** (`Callable`, default: `None` ) –
    
    后处理函数，在服务进程执行，可以是一个函数，也可以是一个仿函数，默认为 `None`。
    
*   **`stream`** (`bool`, default: `False` ) –
    
    是否流式请求和输出，默认为非流式。
    
*   **`return_trace`** (`bool`, default: `False` ) –
    
    是否将结果记录在 trace 中，默认为`False`。
    
*   **`port`** (`int`, default: `None` ) –
    
    指定服务部署后的端口，默认为 `None` 会随机生成端口。
    
*   **`launcher`** (`LazyLLMLaunchersBase`, default: `None` ) –
    
    用于选择服务执行的计算节点，默认为`launchers.remote`。
    

Source code in `lazyllm/module/servermodule.py`

|  | 

`class  ServerModule(UrlModule):
 """借助 fastapi，将任意可调用对象包装成 api 服务，可同时启动一个主服务和多个卫星服务。   Args:
 m (Callable): 被包装成服务的函数，可以是一个函数，也可以是一个仿函数。当启动卫星服务时，需要是一个实现了 ``__call__`` 的对象（仿函数）。 pre (Callable): 前处理函数，在服务进程执行，可以是一个函数，也可以是一个仿函数，默认为 ``None``。 post (Callable): 后处理函数，在服务进程执行，可以是一个函数，也可以是一个仿函数，默认为 ``None``。 stream (bool): 是否流式请求和输出，默认为非流式。 return_trace (bool): 是否将结果记录在 trace 中，默认为``False``。 port (int): 指定服务部署后的端口，默认为 ``None`` 会随机生成端口。 launcher (LazyLLMLaunchersBase): 用于选择服务执行的计算节点，默认为`` launchers.remote``。 """
 def  __init__(self, m: Optional[Union[str, ModuleBase]] = None, pre: Optional[Callable] = None, post: Optional[Callable] = None, stream: Union[bool, Dict] = False, return_trace: bool = False, port: Optional[int] = None, pythonpath: Optional[str] = None, launcher: Optional[LazyLLMLaunchersBase] = None, url: Optional[str] = None): assert stream is False or return_trace is False, 'Module with stream output has no trace' assert (post is None) or (stream is False), 'Stream cannot be true when post-action exists' if isinstance(m, str): assert url is None, 'url should be None when m is a url' url, m = m, None if url: assert is_valid_url(url), f'Invalid url: {url}' assert m is None, 'm should be None when url is provided' super().__init__(url=url, stream=stream, return_trace=return_trace) self._impl = _ServerModuleImpl(m, pre, post, launcher, port, pythonpath, self._url_wrapper) if url: self._impl._get_deploy_tasks.flag.set()   _url_id = property(lambda self: self._impl._module_id)   def  wait(self): self._impl._launcher.wait()   def  stop(self): self._impl.stop()   @property def  status(self): return self._impl._launcher.status   def  _call(self, fname, *args, **kwargs): args, kwargs = lazyllm.dump_obj(args), lazyllm.dump_obj(kwargs) url = urljoin(self._url.rsplit("/", 1)[0], '_call') r = requests.post(url, json=(fname, args, kwargs), headers={'Content-Type': 'application/json'}) return pickle.loads(codecs.decode(r.content, "base64"))   def  forward(self, __input: Union[Tuple[Union[str, Dict], str], str, Dict] = package(), **kw): headers = { 'Content-Type': 'application/json', 'Global-Parameters': encode_request(globals._pickle_data), 'Session-ID': encode_request(globals._sid) } data = encode_request((__input, kw))   # context bug with httpx, so we use requests with requests.post(self._url, json=data, stream=True, headers=headers, proxies={'http': None, 'https': None}) as r: if r.status_code != 200: raise requests.RequestException('\n'.join([c.decode('utf-8') for c in r.iter_content(None)]))   messages = '' with self.stream_output(self._stream): for line in r.iter_lines(delimiter=b"<|lazyllm_delimiter|>"): line = self._decode_line(line) if self._stream: self._stream_output(str(line), getattr(self._stream, 'get', lambda x: None)('color')) messages = (messages + str(line)) if self._stream else line   temp_output = self._extract_and_format(messages) return self._formatter(temp_output)   def  __repr__(self): return lazyllm.make_repr('Module', 'Server', subs=[repr(self._impl._m)], name=self._module_name, stream=self._stream, return_trace=self._return_trace)` 



 | 

`lazyllm.module.TrialModule`
----------------------------

Bases: `object`

参数网格搜索模块，会遍历其所有的submodule，收集所有的可被搜索的参数，遍历这些参数进行微调、部署和评测

Parameters:

*   **`m`** (`Callable`) –
    
    被网格搜索参数的子模块，微调、部署和评测都会基于这个模块进行
    

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> from  lazyllm  import finetune, deploy [](#__codelineno-0-3)>>> m = lazyllm.TrainableModule('b1', 't').finetune_method(finetune.dummy, **dict(a=lazyllm.Option(['f1', 'f2']))) [](#__codelineno-0-4)>>> m.deploy_method(deploy.dummy).mode('finetune').prompt(None) [](#__codelineno-0-5)>>> s = lazyllm.ServerModule(m, post=lambda x, ori: f'post2({x})') [](#__codelineno-0-6)>>> s.evalset([1, 2, 3]) [](#__codelineno-0-7)>>> t = lazyllm.TrialModule(s) [](#__codelineno-0-8)>>> t.update() [](#__codelineno-0-9)>>> [](#__codelineno-0-10)dummy finetune!, and init-args is {a: f1} [](#__codelineno-0-11)dummy finetune!, and init-args is {a: f2} [](#__codelineno-0-12)[["post2(reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1})", "post2(reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1})", "post2(reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1})"], ["post2(reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1})", "post2(reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1})", "post2(reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1})"]]` 

Source code in `lazyllm/module/trialmodule.py`

|  | 

`class  TrialModule(object):
 """参数网格搜索模块，会遍历其所有的submodule，收集所有的可被搜索的参数，遍历这些参数进行微调、部署和评测   Args:
 m (Callable): 被网格搜索参数的子模块，微调、部署和评测都会基于这个模块进行     Examples:
 >>> import lazyllm >>> from lazyllm import finetune, deploy >>> m = lazyllm.TrainableModule('b1', 't').finetune_method(finetune.dummy, **dict(a=lazyllm.Option(['f1', 'f2']))) >>> m.deploy_method(deploy.dummy).mode('finetune').prompt(None) >>> s = lazyllm.ServerModule(m, post=lambda x, ori: f'post2({x})') >>> s.evalset([1, 2, 3]) >>> t = lazyllm.TrialModule(s) >>> t.update() >>> dummy finetune!, and init-args is {a: f1} dummy finetune!, and init-args is {a: f2} [["post2(reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1})", "post2(reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1})", "post2(reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1})"], ["post2(reply for 1, and parameters is {'do_sample': False, 'temperature': 0.1})", "post2(reply for 2, and parameters is {'do_sample': False, 'temperature': 0.1})", "post2(reply for 3, and parameters is {'do_sample': False, 'temperature': 0.1})"]] """ def  __init__(self, m): self.m = m   @staticmethod def  work(m, q): # update option at module.update() m = copy.deepcopy(m) m.update() q.put(m.eval_result)   def  update(self): options = get_options(self.m) q = multiprocessing.Queue() ps = [] for _ in OptionIter(options, get_options): p = ForkProcess(target=TrialModule.work, args=(self.m, q), sync=True) ps.append(p) p.start() time.sleep(1) [p.join() for p in ps] result = [q.get() for p in ps] LOG.info(f'{result}')` 



 | 

`lazyllm.module.OnlineChatModule`
---------------------------------

用来管理创建目前市面上公开的大模型平台访问模块，目前支持openai、sensenova、glm、kimi、qwen、doubao、deekseek(由于该平台暂时不让充值了，暂时不支持访问)。平台的api key获取方法参见 [开始入门](https://docs.lazyllm.ai/#platform)

Parameters:

*   **`model`** (`str`) –
    
    指定要访问的模型 (注意使用豆包时需用 Model ID 或 Endpoint ID，获取方式详见 [获取推理接入点](https://www.volcengine.com/docs/82379/1099522)。使用模型前，要先在豆包平台开通对应服务。)，默认为 `gpt-3.5-turbo(openai)` / `SenseChat-5(sensenova)` / `glm-4(glm)` / `moonshot-v1-8k(kimi)` / `qwen-plus(qwen)` / `mistral-7b-instruct-v0.2(doubao)`
    
*   **`source`** (`str`) –
    
    指定要创建的模块类型，可选为 `openai` / `sensenova` / `glm` / `kimi` / `qwen` / `doubao` / `deepseek(暂时不支持访问)`
    
*   **`base_url`** (`str`) –
    
    指定要访问的平台的基础链接，默认是官方链接
    
*   **`system_prompt`** (`str`) –
    
    指定请求的system prompt，默认是官方给的system prompt
    
*   **`stream`** (`bool`) –
    
    是否流式请求和输出，默认为流式
    
*   **`return_trace`** (`bool`) –
    
    是否将结果记录在trace中，默认为False
    

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> from  functools  import partial [](#__codelineno-0-3)>>> m = lazyllm.OnlineChatModule(source="sensenova", stream=True) [](#__codelineno-0-4)>>> query = "Hello!" [](#__codelineno-0-5)>>> with lazyllm.ThreadPoolExecutor(1) as executor: [](#__codelineno-0-6)...     future = executor.submit(partial(m, llm_chat_history=[]), query) [](#__codelineno-0-7)...     while True: [](#__codelineno-0-8)...         if value := lazyllm.FileSystemQueue().dequeue(): [](#__codelineno-0-9)...             print(f"output: {''.join(value)}") [](#__codelineno-0-10)...         elif future.done(): [](#__codelineno-0-11)...             break [](#__codelineno-0-12)...     print(f"ret: {future.result()}") [](#__codelineno-0-13)... [](#__codelineno-0-14)output: Hello [](#__codelineno-0-15)output: ! How can I assist you today? [](#__codelineno-0-16)ret: Hello! How can I assist you today? [](#__codelineno-0-17)>>> from  lazyllm.components.formatter  import encode_query_with_filepaths [](#__codelineno-0-18)>>> vlm = lazyllm.OnlineChatModule(source="sensenova", model="SenseChat-Vision") [](#__codelineno-0-19)>>> query = "what is it?" [](#__codelineno-0-20)>>> inputs = encode_query_with_filepaths(query, ["/path/to/your/image"]) [](#__codelineno-0-21)>>> print(vlm(inputs))` 

Source code in `lazyllm/module/llms/onlineChatModule/onlineChatModule.py`

|  | 

`class  OnlineChatModule(metaclass=_ChatModuleMeta):
 """用来管理创建目前市面上公开的大模型平台访问模块，目前支持openai、sensenova、glm、kimi、qwen、doubao、deekseek(由于该平台暂时不让充值了，暂时不支持访问)。平台的api key获取方法参见 [开始入门](/#platform)   Args:
 model (str): 指定要访问的模型 (注意使用豆包时需用 Model ID 或 Endpoint ID，获取方式详见 [获取推理接入点](https://www.volcengine.com/docs/82379/1099522)。使用模型前，要先在豆包平台开通对应服务。)，默认为 ``gpt-3.5-turbo(openai)`` / ``SenseChat-5(sensenova)`` / ``glm-4(glm)`` / ``moonshot-v1-8k(kimi)`` / ``qwen-plus(qwen)`` / ``mistral-7b-instruct-v0.2(doubao)`` source (str): 指定要创建的模块类型，可选为 ``openai`` /  ``sensenova`` /  ``glm`` /  ``kimi`` /  ``qwen`` / ``doubao`` / ``deepseek(暂时不支持访问)`` base_url (str): 指定要访问的平台的基础链接，默认是官方链接 system_prompt (str): 指定请求的system prompt，默认是官方给的system prompt stream (bool): 是否流式请求和输出，默认为流式 return_trace (bool): 是否将结果记录在trace中，默认为False     Examples:
 >>> import lazyllm >>> from functools import partial >>> m = lazyllm.OnlineChatModule(source="sensenova", stream=True) >>> query = "Hello!" >>> with lazyllm.ThreadPoolExecutor(1) as executor: ...     future = executor.submit(partial(m, llm_chat_history=[]), query) ...     while True: ...         if value := lazyllm.FileSystemQueue().dequeue(): ...             print(f"output: {''.join(value)}") ...         elif future.done(): ...             break ...     print(f"ret: {future.result()}") ... output: Hello output: ! How can I assist you today? ret: Hello! How can I assist you today? >>> from lazyllm.components.formatter import encode_query_with_filepaths >>> vlm = lazyllm.OnlineChatModule(source="sensenova", model="SenseChat-Vision") >>> query = "what is it?" >>> inputs = encode_query_with_filepaths(query, ["/path/to/your/image"]) >>> print(vlm(inputs)) """ MODELS = {'openai': OpenAIModule, 'sensenova': SenseNovaModule, 'glm': GLMModule, 'kimi': KimiModule, 'qwen': QwenModule, 'doubao': DoubaoModule, 'deepseek': DeepSeekModule}   @staticmethod def  _encapsulate_parameters(base_url: str, model: str, stream: bool, return_trace: bool, **kwargs) -> Dict[str, Any]: params = {"stream": stream, "return_trace": return_trace} if base_url is not None: params['base_url'] = base_url if model is not None: params['model'] = model params.update(kwargs)   return params   def  __new__(self, model: str = None, source: str = None, base_url: str = None, stream: bool = True, return_trace: bool = False, **kwargs): if model in OnlineChatModule.MODELS.keys() and source is None: source, model = model, source   params = OnlineChatModule._encapsulate_parameters(base_url, model, stream, return_trace, **kwargs)   if kwargs.get("skip_auth", False): source = source or "openai" if not base_url: raise KeyError("base_url must be set for local serving.")   if source is None: if "api_key" in kwargs and kwargs["api_key"]: raise ValueError("No source is given but an api_key is provided.") for source in OnlineChatModule.MODELS.keys(): if lazyllm.config[f'{source}_api_key']: break else: raise KeyError(f"No api_key is configured for any of the models {OnlineChatModule.MODELS.keys()}.")   assert source in OnlineChatModule.MODELS.keys(), f"Unsupported source: {source}" return OnlineChatModule.MODELS[source](**params)` 



 | 

`lazyllm.module.OnlineEmbeddingModule`
--------------------------------------

用来管理创建目前市面上的在线Embedding服务模块，目前支持openai、sensenova、glm、qwen、doubao

Parameters:

*   **`source`** (`str`) –
    
    指定要创建的模块类型，可选为 `openai` / `sensenova` / `glm` / `qwen` / `doubao`
    
*   **`embed_url`** (`str`) –
    
    指定要访问的平台的基础链接，默认是官方链接
    
*   **`embed_mode_name`** (`str`) –
    
    指定要访问的模型 (注意使用豆包时需用 Model ID 或 Endpoint ID，获取方式详见 [获取推理接入点](https://www.volcengine.com/docs/82379/1099522)。使用模型前，要先在豆包平台开通对应服务。)，默认为 `text-embedding-ada-002(openai)` / `nova-embedding-stable(sensenova)` / `embedding-2(glm)` / `text-embedding-v1(qwen)` / `doubao-embedding-text-240715(doubao)`
    

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> m = lazyllm.OnlineEmbeddingModule(source="sensenova") [](#__codelineno-0-3)>>> emb = m("hello world") [](#__codelineno-0-4)>>> print(f"emb: {emb}") [](#__codelineno-0-5)emb: [0.0010528564, 0.0063285828, 0.0049476624, -0.012008667, ..., -0.009124756, 0.0032043457, -0.051696777]` 

Source code in `lazyllm/module/llms/onlineEmbedding/onlineEmbeddingModule.py`

|  | 

`class  OnlineEmbeddingModule(metaclass=__EmbedModuleMeta):
 """用来管理创建目前市面上的在线Embedding服务模块，目前支持openai、sensenova、glm、qwen、doubao   Args:
 source (str): 指定要创建的模块类型，可选为 ``openai`` /  ``sensenova`` /  ``glm`` /  ``qwen`` / ``doubao`` embed_url (str): 指定要访问的平台的基础链接，默认是官方链接 embed_mode_name (str): 指定要访问的模型 (注意使用豆包时需用 Model ID 或 Endpoint ID，获取方式详见 [获取推理接入点](https://www.volcengine.com/docs/82379/1099522)。使用模型前，要先在豆包平台开通对应服务。)，默认为 ``text-embedding-ada-002(openai)`` / ``nova-embedding-stable(sensenova)`` / ``embedding-2(glm)`` / ``text-embedding-v1(qwen)`` / ``doubao-embedding-text-240715(doubao)``     Examples:
 >>> import lazyllm >>> m = lazyllm.OnlineEmbeddingModule(source="sensenova") >>> emb = m("hello world") >>> print(f"emb: {emb}") emb: [0.0010528564, 0.0063285828, 0.0049476624, -0.012008667, ..., -0.009124756, 0.0032043457, -0.051696777] """ EMBED_MODELS = {'openai': OpenAIEmbedding, 'sensenova': SenseNovaEmbedding, 'glm': GLMEmbedding, 'qwen': QwenEmbedding, 'doubao': DoubaoEmbedding} RERANK_MODELS = {'qwen': QwenReranking, 'glm': GLMReranking}   @staticmethod def  _encapsulate_parameters(embed_url: str, embed_model_name: str, **kwargs) -> Dict[str, Any]: params = {} if embed_url is not None: params["embed_url"] = embed_url if embed_model_name is not None: params["embed_model_name"] = embed_model_name params.update(kwargs) return params   @staticmethod def  _check_available_source(available_models): for source in available_models.keys(): if lazyllm.config[f'{source}_api_key']: break else: raise KeyError(f"No api_key is configured for any of the models {available_models.keys()}.")   assert source in available_models.keys(), f"Unsupported source: {source}" return source   def  __new__(self, source: str = None, embed_url: str = None, embed_model_name: str = None, **kwargs): params = OnlineEmbeddingModule._encapsulate_parameters(embed_url, embed_model_name, **kwargs)   if source is None and "api_key" in kwargs and kwargs["api_key"]: raise ValueError("No source is given but an api_key is provided.")   if "type" in params: params.pop("type") if kwargs.get("type", "embed") == "embed": if source is None: source = OnlineEmbeddingModule._check_available_source(OnlineEmbeddingModule.EMBED_MODELS) if source == "doubao": if embed_model_name.startswith("doubao-embedding-vision"): return DoubaoMultimodalEmbedding(**params) else: return DoubaoEmbedding(**params) return OnlineEmbeddingModule.EMBED_MODELS[source](**params) elif kwargs.get("type") == "rerank": if source is None: source = OnlineEmbeddingModule._check_available_source(OnlineEmbeddingModule.RERANK_MODELS) return OnlineEmbeddingModule.RERANK_MODELS[source](**params) else: raise ValueError("Unknown type of online embedding module.")` 



 | 

`lazyllm.module.OnlineChatModuleBase`
-------------------------------------

Bases: `LLMBase`

OnlineChatModuleBase是管理开放平台的LLM接口的公共组件，具备训练、部署、推理等关键能力。OnlineChatModuleBase本身不支持直接实例化， 需要子类继承该类，并实现微调相关的上传文件、创建微调任务、查询微调任务以及和部署相关的创建部署服务、查询部署任务等接口。

如果你需要支持新的开放平台的LLM的能力，请让你自定义的类继承自OnlineChatModuleBase：

1、根据新平台的模型返回参数情况考虑对返回结果进行后处理，如果模型返回的格式和openai一致，可以不用做任何处理

2、如果新平台支持模型的微调，也需要继承FileHandlerBase类，该类主要是验证文件格式，并在自定义类中把.jsonl格式数据转换为模型支持的数据才能用于后面的模型训练

3、如果新平台支持模型的微调，则需要实现文件上传、创建微调服务、查询微调服务的接口。即使新平台不用对微调后的模型进行部署，也请实现一个假的创建部署服务和查询部署服务的接口即可

4、如果新平台支持模型的微调，可以提供一个支持微调的模型列表，有助于在微调服务时进行判断

5、配置新平台支持的api\_key到全局变量，通过lazyllm.config.add(变量名，类型，默认值，环境变量名)进行添加

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> from  lazyllm.module  import OnlineChatModuleBase [](#__codelineno-0-3)>>> from  lazyllm.module.onlineChatModule.fileHandler  import FileHandlerBase [](#__codelineno-0-4)>>> class  NewPlatformChatModule(OnlineChatModuleBase): [](#__codelineno-0-5)...     def  __init__(self, [](#__codelineno-0-6)...                   base_url: str = "<new platform base url>", [](#__codelineno-0-7)...                   model: str = "<new platform model name>", [](#__codelineno-0-8)...                   system_prompt: str = "<new platform system prompt>", [](#__codelineno-0-9)...                   stream: bool = True, [](#__codelineno-0-10)...                   return_trace: bool = False): [](#__codelineno-0-11)...         super().__init__(model_type="new_class_name", [](#__codelineno-0-12)...                          api_key=lazyllm.config['new_platform_api_key'], [](#__codelineno-0-13)...                          base_url=base_url, [](#__codelineno-0-14)...                          system_prompt=system_prompt, [](#__codelineno-0-15)...                          stream=stream, [](#__codelineno-0-16)...                          return_trace=return_trace) [](#__codelineno-0-17)... [](#__codelineno-0-18)>>> class  NewPlatformChatModule1(OnlineChatModuleBase, FileHandlerBase): [](#__codelineno-0-19)...     TRAINABLE_MODELS_LIST = ['model_t1', 'model_t2', 'model_t3'] [](#__codelineno-0-20)...     def  __init__(self, [](#__codelineno-0-21)...                   base_url: str = "<new platform base url>", [](#__codelineno-0-22)...                   model: str = "<new platform model name>", [](#__codelineno-0-23)...                   system_prompt: str = "<new platform system prompt>", [](#__codelineno-0-24)...                   stream: bool = True, [](#__codelineno-0-25)...                   return_trace: bool = False): [](#__codelineno-0-26)...         OnlineChatModuleBase.__init__(self, [](#__codelineno-0-27)...                                       model_type="new_class_name", [](#__codelineno-0-28)...                                       api_key=lazyllm.config['new_platform_api_key'], [](#__codelineno-0-29)...                                       base_url=base_url, [](#__codelineno-0-30)...                                       system_prompt=system_prompt, [](#__codelineno-0-31)...                                       stream=stream, [](#__codelineno-0-32)...                                       trainable_models=NewPlatformChatModule1.TRAINABLE_MODELS_LIST, [](#__codelineno-0-33)...                                       return_trace=return_trace) [](#__codelineno-0-34)...         FileHandlerBase.__init__(self) [](#__codelineno-0-35)... [](#__codelineno-0-36)...     def  _convert_file_format(self, filepath:str) -> str: [](#__codelineno-0-37)...         pass [](#__codelineno-0-38)...         return data_str [](#__codelineno-0-39)... [](#__codelineno-0-40)...     def  _upload_train_file(self, train_file): [](#__codelineno-0-41)...         pass [](#__codelineno-0-42)...         return train_file_id [](#__codelineno-0-43)... [](#__codelineno-0-44)...     def  _create_finetuning_job(self, train_model, train_file_id, **kw): [](#__codelineno-0-45)...         pass [](#__codelineno-0-46)...         return fine_tuning_job_id, status [](#__codelineno-0-47)... [](#__codelineno-0-48)...     def  _query_finetuning_job(self, fine_tuning_job_id): [](#__codelineno-0-49)...         pass [](#__codelineno-0-50)...         return fine_tuned_model, status [](#__codelineno-0-51)... [](#__codelineno-0-52)...     def  _create_deployment(self): [](#__codelineno-0-53)...         pass [](#__codelineno-0-54)...         return self._model_name, "RUNNING" [](#__codelineno-0-55)... [](#__codelineno-0-56)...     def  _query_deployment(self, deployment_id): [](#__codelineno-0-57)...         pass [](#__codelineno-0-58)...         return "RUNNING" [](#__codelineno-0-59)...` 

Source code in `lazyllm/module/llms/onlineChatModule/onlineChatModuleBase.py`

|  | 

`class  OnlineChatModuleBase(LLMBase):
 """OnlineChatModuleBase是管理开放平台的LLM接口的公共组件，具备训练、部署、推理等关键能力。OnlineChatModuleBase本身不支持直接实例化， 需要子类继承该类，并实现微调相关的上传文件、创建微调任务、查询微调任务以及和部署相关的创建部署服务、查询部署任务等接口。   如果你需要支持新的开放平台的LLM的能力，请让你自定义的类继承自OnlineChatModuleBase：   1、根据新平台的模型返回参数情况考虑对返回结果进行后处理，如果模型返回的格式和openai一致，可以不用做任何处理   2、如果新平台支持模型的微调，也需要继承FileHandlerBase类，该类主要是验证文件格式，并在自定义类中把.jsonl格式数据转换为模型支持的数据才能用于后面的模型训练   3、如果新平台支持模型的微调，则需要实现文件上传、创建微调服务、查询微调服务的接口。即使新平台不用对微调后的模型进行部署，也请实现一个假的创建部署服务和查询部署服务的接口即可   4、如果新平台支持模型的微调，可以提供一个支持微调的模型列表，有助于在微调服务时进行判断   5、配置新平台支持的api_key到全局变量，通过lazyllm.config.add(变量名，类型，默认值，环境变量名)进行添加     Examples:
 >>> import lazyllm >>> from lazyllm.module import OnlineChatModuleBase >>> from lazyllm.module.onlineChatModule.fileHandler import FileHandlerBase >>> class NewPlatformChatModule(OnlineChatModuleBase): ...     def __init__(self, ...                   base_url: str = "<new platform base url>", ...                   model: str = "<new platform model name>", ...                   system_prompt: str = "<new platform system prompt>", ...                   stream: bool = True, ...                   return_trace: bool = False): ...         super().__init__(model_type="new_class_name", ...                          api_key=lazyllm.config['new_platform_api_key'], ...                          base_url=base_url, ...                          system_prompt=system_prompt, ...                          stream=stream, ...                          return_trace=return_trace) ... >>> class NewPlatformChatModule1(OnlineChatModuleBase, FileHandlerBase): ...     TRAINABLE_MODELS_LIST = ['model_t1', 'model_t2', 'model_t3'] ...     def __init__(self, ...                   base_url: str = "<new platform base url>", ...                   model: str = "<new platform model name>", ...                   system_prompt: str = "<new platform system prompt>", ...                   stream: bool = True, ...                   return_trace: bool = False): ...         OnlineChatModuleBase.__init__(self, ...                                       model_type="new_class_name", ...                                       api_key=lazyllm.config['new_platform_api_key'], ...                                       base_url=base_url, ...                                       system_prompt=system_prompt, ...                                       stream=stream, ...                                       trainable_models=NewPlatformChatModule1.TRAINABLE_MODELS_LIST, ...                                       return_trace=return_trace) ...         FileHandlerBase.__init__(self) ... ...     def _convert_file_format(self, filepath:str) -> str: ...         pass ...         return data_str ... ...     def _upload_train_file(self, train_file): ...         pass ...         return train_file_id ... ...     def _create_finetuning_job(self, train_model, train_file_id, **kw): ...         pass ...         return fine_tuning_job_id, status ... ...     def _query_finetuning_job(self, fine_tuning_job_id): ...         pass ...         return fine_tuned_model, status ... ...     def _create_deployment(self): ...         pass ...         return self._model_name, "RUNNING" ... ...     def _query_deployment(self, deployment_id): ...         pass ...         return "RUNNING" ... """ TRAINABLE_MODEL_LIST = [] VLM_MODEL_LIST = [] NO_PROXY = True   def  __init__(self, model_series: str, api_key: str, base_url: str, model_name: str, stream: Union[bool, Dict[str, str]], return_trace: bool = False, skip_auth: bool = False, static_params: StaticParams = {}, **kwargs): super().__init__(stream=stream, return_trace=return_trace) self._model_series = model_series if skip_auth and not api_key: raise ValueError("api_key is required") self._api_key = api_key self._base_url = base_url self._model_name = model_name self.trainable_models = self.TRAINABLE_MODEL_LIST self._set_headers() self._set_chat_url() self._is_trained = False self._model_optional_params = {} self._vlm_force_format_input_with_files = False self._static_params = static_params   @property def  series(self): return self._model_series   @property def  type(self): return "LLM"   @property def  static_params(self) -> StaticParams: return self._static_params   @static_params.setter def  static_params(self, value: StaticParams): if not isinstance(value, dict): raise TypeError("static_params must be a dict (TypedDict)") self._static_params = value   def  prompt(self, prompt: Optional[str] = None, history: Optional[List[List[str]]] = None): super().prompt('' if prompt is None else prompt, history=history) self._prompt._set_model_configs(system=self._get_system_prompt()) return self   def  share(self, prompt: Optional[Union[str, dict, PrompterBase]] = None, format: Optional[FormatterBase] = None, stream: Optional[Union[bool, Dict[str, str]]] = None, history: Optional[List[List[str]]] = None, copy_static_params: bool = False): new = super().share(prompt, format, stream, history) if copy_static_params: new._static_params = copy.deepcopy(self._static_params) return new   def  _get_system_prompt(self): raise NotImplementedError("_get_system_prompt is not implemented.")   def  _set_headers(self): self._headers = { 'Content-Type': 'application/json', **({'Authorization': 'Bearer ' + self._api_key} if self._api_key else {}) }   def  _set_chat_url(self): self._url = urljoin(self._base_url, 'chat/completions')   def  _get_models_list(self): url = urljoin(self._base_url, 'models') headers = {'Authorization': 'Bearer ' + self._api_key} if self._api_key else None with requests.get(url, headers=headers) as r: if r.status_code != 200: raise requests.RequestException('\n'.join([c.decode('utf-8') for c in r.iter_content(None)]))   res_json = r.json() return res_json   def  _convert_msg_format(self, msg: Dict[str, Any]): return msg   def  _str_to_json(self, msg: str, stream_output: bool): if isinstance(msg, bytes): pattern = re.compile(r"^data:\s*") msg = re.sub(pattern, "", msg.decode('utf-8')) try: message = self._convert_msg_format(json.loads(msg)) if not stream_output: return message color = stream_output.get('color') if isinstance(stream_output, dict) else None for item in message.get("choices", []): delta = item.get('message', item.get('delta', {})) if (reasoning_content := delta.get("reasoning_content", '')): self._stream_output(reasoning_content, color, cls='think') elif (content := delta.get("content", '')) and not delta.get('tool_calls'): self._stream_output(content, color) lazyllm.LOG.debug(f"message: {message}") return message except Exception: return ""   def  _extract_specified_key_fields(self, response: Dict[str, Any]): if not ("choices" in response and isinstance(response["choices"], list)): raise ValueError(f"The response {response} does not contain a 'choices' field.") outputs = response['choices'][0].get("message") or response['choices'][0].get("delta", {}) if 'reasoning_content' in outputs and outputs["reasoning_content"] and 'content' in outputs: outputs['content'] = r'<think>' + outputs.pop('reasoning_content') + r'</think>' + outputs['content']   result, tool_calls = outputs.get('content', ''), outputs.get('tool_calls') if tool_calls: try: if isinstance(tool_calls, list): [item.pop('index', None) for item in tool_calls] tool_calls = tool_calls if isinstance(tool_calls, str) else json.dumps(tool_calls, ensure_ascii=False) if tool_calls: result += '<|tool_calls|>' + tool_calls except (KeyError, IndexError, TypeError): pass return result   def  _merge_stream_result(self, src: List[Union[str, int, list, dict]], force_join: bool = False): src = [ele for ele in src if ele is not None] if not src: return None elif len(src) == 1: return src[0] assert len(set(map(type, src))) == 1, f"The elements in the list: {src} are of inconsistent types"   if isinstance(src[0], str): src = [ele for ele in src if ele] if not src: return '' if force_join or not all(src[0] == ele for ele in src): return ''.join(src) elif isinstance(src[0], list): assert len(set(map(len, src))) == 1, f"The lists of elements: {src} have different lengths." ret = list(map(self._merge_stream_result, zip(*src))) return ret[0] if isinstance(ret[0], list) else ret elif isinstance(src[0], dict):  # list of dicts if 'index' in src[-1]: grouped = [list(g) for _, g in groupby(sorted(src, key=itemget('index')), key=itemget("index"))] if len(grouped) > 1: return [self._merge_stream_result(src) for src in grouped] return {k: self._merge_stream_result([d.get(k) for d in src], k == 'content') for k in set().union(*src)} return src[-1]   def  forward(self, __input: Union[Dict, str] = None, *, llm_chat_history: List[List[str]] = None, tools: List[Dict[str, Any]] = None, stream_output: bool = False, lazyllm_files=None, **kw): """LLM inference interface""" stream_output = stream_output or self._stream if lazyllm_files: __input = encode_query_with_filepaths(__input, lazyllm_files) params = {'input': __input, 'history': llm_chat_history, 'return_dict': True} if tools: params["tools"] = tools data = self._prompt.generate_prompt(**params) data.update(self._static_params, **dict(model=self._model_name, stream=bool(stream_output)))   if len(kw) > 0: data.update(kw) if len(self._model_optional_params) > 0: data.update(self._model_optional_params)   if isinstance(__input, str) and (__input.startswith(LAZYLLM_QUERY_PREFIX) or (self._vlm_force_format_input_with_files and data["model"] in self.VLM_MODEL_LIST)): for idx, message in enumerate(data["messages"]): content = message["content"] if content.startswith(LAZYLLM_QUERY_PREFIX): content = decode_query_with_filepaths(content) query_files = self._format_input_with_files(content) data["messages"][idx]["content"] = query_files   proxies = {'http': None, 'https': None} if self.NO_PROXY else None with requests.post(self._url, json=data, headers=self._headers, stream=stream_output, proxies=proxies) as r: if r.status_code != 200:  # request error raise requests.RequestException('\n'.join([c.decode('utf-8') for c in r.iter_content(None)])) \ if stream_output else requests.RequestException(r.text)   with self.stream_output(stream_output): msg_json = list(filter(lambda x: x, ([self._str_to_json(line, stream_output) for line in r.iter_lines() if len(line)] if stream_output else [self._str_to_json(r.text, stream_output)]),))   usage = {"prompt_tokens": -1, "completion_tokens": -1} if len(msg_json) > 0 and "usage" in msg_json[-1] and isinstance(msg_json[-1]["usage"], dict): for k in usage: usage[k] = msg_json[-1]["usage"].get(k, usage[k]) self._record_usage(usage) extractor = self._extract_specified_key_fields(self._merge_stream_result(msg_json)) return self._formatter(extractor) if extractor else ""   def  _record_usage(self, usage: dict): globals["usage"][self._module_id] = usage par_muduleid = self._used_by_moduleid if par_muduleid is None: return if par_muduleid not in globals["usage"]: globals["usage"][par_muduleid] = usage return existing_usage = globals["usage"][par_muduleid] if existing_usage["prompt_tokens"] == -1 or usage["prompt_tokens"] == -1: globals["usage"][par_muduleid] = {"prompt_tokens": -1, "completion_tokens": -1} else: for k in globals["usage"][par_muduleid]: globals["usage"][par_muduleid][k] += usage[k]   def  _upload_train_file(self, train_file) -> str: raise NotImplementedError(f"{self._model_series} not implemented _upload_train_file method in subclass")   def  _create_finetuning_job(self, train_model, train_file_id, **kw) -> Tuple[str, str]: raise NotImplementedError(f"{self._model_series} not implemented _create_finetuning_job method in subclass")   def  _query_finetuning_job(self, fine_tuning_job_id) -> Tuple[str, str]: raise NotImplementedError(f"{self._model_series} not implemented _query_finetuning_job method in subclass")   def  _query_finetuned_jobs(self) -> dict: raise NotImplementedError(f"{self._model_series} not implemented _query_finetuned_jobs method in subclass")   def  _get_finetuned_model_names(self) -> Tuple[List[str], List[str]]: raise NotImplementedError(f"{self._model_series} not implemented _get_finetuned_model_names method in subclass")   def  set_train_tasks(self, train_file, **kw): self._train_file = train_file self._train_parameters = kw   def  set_specific_finetuned_model(self, model_id): valid_jobs, _ = self._get_finetuned_model_names() valid_model_id = [model for _, model in valid_jobs] if model_id in valid_model_id: self._model_name = model_id self._is_trained = True else: raise ValueError(f"Cannot find modle({model_id}), in fintuned model list: {valid_model_id}")   def  _get_temp_save_dir_path(self): save_dir = os.path.join(lazyllm.config['temp_dir'], 'online_model_sft_log') if not os.path.exists(save_dir): os.system(f'mkdir -p {save_dir}') else: delete_old_files(save_dir) return save_dir   def  _validate_api_key(self): try: self._query_finetuned_jobs() return True except Exception: return False   def  _get_train_tasks(self): if not self._model_name or not self._train_file: raise ValueError("train_model and train_file is required") if self._model_name not in self.trainable_models: lazyllm.LOG.log_once(f"The current model {self._model_name} is not in the trainable \ model list {self.trainable_models}. The deadline for this list is June 1, 2024. \ This model may not be trainable. If your model is a new model, \ you can ignore this warning.")   def  _create_for_finetuning_job(): """ create for finetuning job to finish """ file_id = self._upload_train_file(train_file=self._train_file) lazyllm.LOG.info(f"{os.path.basename(self._train_file)} upload success! file id is {file_id}") (fine_tuning_job_id, status) = self._create_finetuning_job(self._model_name, file_id, **self._train_parameters) lazyllm.LOG.info(f"fine tuning job {fine_tuning_job_id} created, status: {status}")   if status.lower() == "failed": raise ValueError(f"Fine tuning job {fine_tuning_job_id} failed") while status.lower() != "succeeded": try: # wait 10 seconds before querying again time.sleep(random.randint(60, 120)) (fine_tuned_model, status) = self._query_finetuning_job(fine_tuning_job_id) lazyllm.LOG.info(f"fine tuning job {fine_tuning_job_id} status: {status}") if status.lower() == "failed": raise ValueError(f"Finetuning job {fine_tuning_job_id} failed") except ValueError: raise ValueError(f"Finetuning job {fine_tuning_job_id} failed")   lazyllm.LOG.info(f"fine tuned model: {fine_tuned_model} finished") self._model_name = fine_tuned_model self._is_trained = True   return Pipeline(_create_for_finetuning_job)   def  _create_deployment(self) -> Tuple[str, str]: raise NotImplementedError(f"{self._model_series} not implemented _create_deployment method in subclass")   def  _query_deployment(self, deployment_id) -> str: raise NotImplementedError(f"{self._model_series} not implemented _query_deployment method in subclass")   def  _get_deploy_tasks(self): if not self._is_trained: return None   def  _start_for_deployment(): (deployment_id, status) = self._create_deployment() lazyllm.LOG.info(f"deployment {deployment_id} created, status: {status}")   if status.lower() == "failed": raise ValueError(f"Deployment task {deployment_id} failed") status = self._query_deployment(deployment_id) while status.lower() != "running": # wait 10 seconds before querying again time.sleep(10) status = self._query_deployment(deployment_id) lazyllm.LOG.info(f"deployment {deployment_id} status: {status}") if status.lower() == "failed": raise ValueError(f"Deployment task {deployment_id} failed") lazyllm.LOG.info(f"deployment {deployment_id} finished") return Pipeline(_start_for_deployment)   def  _format_vl_chat_query(self, query: str): return [{"type": "text", "text": query}]   def  _format_vl_chat_image_url(self, image_url: str, mime: str) -> List[Dict[str, str]]: return [{"type": "image_url", "image_url": {"url": image_url}}]   # for online vlm def  _format_input_with_files(self, query_files: str) -> List[Dict[str, str]]: if isinstance(query_files, str): return self._format_vl_chat_query(query_files) assert isinstance(query_files, dict), "query_files must be a dict." output = [{"type": "text", "text": query_files["query"]}] files = query_files.get("files", []) assert isinstance(files, list), "files must be a list." for file in files: mime = None if not file.startswith("http"): file, mime = image_to_base64(file) output.extend(self._format_vl_chat_image_url(file, mime)) return output   def  __repr__(self): return lazyllm.make_repr('Module', 'OnlineChat', name=self._module_name, url=self._base_url, stream=bool(self._stream), return_trace=self._return_trace)` 



 | 

`lazyllm.module.OnlineEmbeddingModuleBase`
------------------------------------------

Bases: `[ModuleBase](#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase (lazyllm.module.module.ModuleBase)")`

OnlineEmbeddingModuleBase是管理开放平台的嵌入模型接口的基类，用于请求文本获取嵌入向量。不建议直接对该类进行直接实例化。需要特定平台类继承该类进行实例化。

如果你需要支持新的开放平台的嵌入模型的能力，请让你自定义的类继承自OnlineEmbeddingModuleBase：

1、如果新平台的嵌入模型的请求和返回数据格式都和openai一样，可以不用做任何处理，只传url和模型即可

2、如果新平台的嵌入模型的请求或者返回的数据格式和openai不一样，需要重写\_encapsulated\_data或\_parse\_response方法。

3、配置新平台支持的api\_key到全局变量，通过lazyllm.config.add(变量名，类型，默认值，环境变量名)进行添加

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> from  lazyllm.module  import OnlineEmbeddingModuleBase [](#__codelineno-0-3)>>> class  NewPlatformEmbeddingModule(OnlineEmbeddingModuleBase): [](#__codelineno-0-4)...     def  __init__(self, [](#__codelineno-0-5)...                 embed_url: str = '<new platform embedding url>', [](#__codelineno-0-6)...                 embed_model_name: str = '<new platform embedding model name>'): [](#__codelineno-0-7)...         super().__init__(embed_url, lazyllm.config['new_platform_api_key'], embed_model_name) [](#__codelineno-0-8)... [](#__codelineno-0-9)>>> class  NewPlatformEmbeddingModule1(OnlineEmbeddingModuleBase): [](#__codelineno-0-10)...     def  __init__(self, [](#__codelineno-0-11)...                 embed_url: str = '<new platform embedding url>', [](#__codelineno-0-12)...                 embed_model_name: str = '<new platform embedding model name>'): [](#__codelineno-0-13)...         super().__init__(embed_url, lazyllm.config['new_platform_api_key'], embed_model_name) [](#__codelineno-0-14)... [](#__codelineno-0-15)...     def  _encapsulated_data(self, text:str, **kwargs): [](#__codelineno-0-16)...         pass [](#__codelineno-0-17)...         return json_data [](#__codelineno-0-18)... [](#__codelineno-0-19)...     def  _parse_response(self, response: dict[str, any]): [](#__codelineno-0-20)...         pass [](#__codelineno-0-21)...         return embedding` 

Source code in `lazyllm/module/llms/onlineEmbedding/onlineEmbeddingModuleBase.py`

|  | 

`class  OnlineEmbeddingModuleBase(ModuleBase):
 """OnlineEmbeddingModuleBase是管理开放平台的嵌入模型接口的基类，用于请求文本获取嵌入向量。不建议直接对该类进行直接实例化。需要特定平台类继承该类进行实例化。   如果你需要支持新的开放平台的嵌入模型的能力，请让你自定义的类继承自OnlineEmbeddingModuleBase：   1、如果新平台的嵌入模型的请求和返回数据格式都和openai一样，可以不用做任何处理，只传url和模型即可   2、如果新平台的嵌入模型的请求或者返回的数据格式和openai不一样，需要重写_encapsulated_data或_parse_response方法。   3、配置新平台支持的api_key到全局变量，通过lazyllm.config.add(变量名，类型，默认值，环境变量名)进行添加     Examples:
 >>> import lazyllm >>> from lazyllm.module import OnlineEmbeddingModuleBase >>> class NewPlatformEmbeddingModule(OnlineEmbeddingModuleBase): ...     def __init__(self, ...                 embed_url: str = '<new platform embedding url>', ...                 embed_model_name: str = '<new platform embedding model name>'): ...         super().__init__(embed_url, lazyllm.config['new_platform_api_key'], embed_model_name) ... >>> class NewPlatformEmbeddingModule1(OnlineEmbeddingModuleBase): ...     def __init__(self, ...                 embed_url: str = '<new platform embedding url>', ...                 embed_model_name: str = '<new platform embedding model name>'): ...         super().__init__(embed_url, lazyllm.config['new_platform_api_key'], embed_model_name) ... ...     def _encapsulated_data(self, text:str, **kwargs): ...         pass ...         return json_data ... ...     def _parse_response(self, response: dict[str, any]): ...         pass ...         return embedding """ NO_PROXY = True   def  __init__(self, model_series: str, embed_url: str, api_key: str, embed_model_name: str, return_trace: bool = False): super().__init__(return_trace=return_trace) self._model_series = model_series self._embed_url = embed_url self._api_key = api_key self._embed_model_name = embed_model_name self._set_headers()   @property def  series(self): return self._model_series   @property def  type(self): return "EMBED"   def  _set_headers(self) -> Dict[str, str]: self._headers = { "Content-Type": "application/json", "Authorization": f"Bearer {self._api_key}" }   def  forward(self, input: Union[List, str], **kwargs) -> List[float]: data = self._encapsulated_data(input, **kwargs) proxies = {'http': None, 'https': None} if self.NO_PROXY else None with requests.post(self._embed_url, json=data, headers=self._headers, proxies=proxies) as r: if r.status_code == 200: return self._parse_response(r.json()) else: raise requests.RequestException('\n'.join([c.decode('utf-8') for c in r.iter_content(None)]))   def  _encapsulated_data(self, input: Union[List, str], **kwargs) -> Dict[str, str]: json_data = { "input": input, "model": self._embed_model_name } if len(kwargs) > 0: json_data.update(kwargs)   return json_data   def  _parse_response(self, response: Dict[str, Any]) -> List[float]: return response['data'][0]['embedding']` 



 |