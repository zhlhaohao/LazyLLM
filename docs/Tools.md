Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase (lazyllm.ModuleBase)")`, `BuiltinGroups`

初始化一个具有可选用户界面的文档模块。

此构造函数初始化一个可以有或没有用户界面的文档模块。如果启用了用户界面，它还会提供一个ui界面来管理文档操作接口，并提供一个用于用户界面交互的网页。

Parameters:

*   **`dataset_path`** (`str`, default: `None` ) –

    数据集目录的路径。此目录应包含要由文档模块管理的文档。

*   **`embed`** (`Optional[Union[Callable, Dict[str, Callable]]]`, default: `None` ) –

    用于生成文档 embedding 的对象。如果需要对文本生成多个 embedding，此处需要通过字典的方式指定多个 embedding 模型，key 标识 embedding 对应的名字, value 为对应的 embedding 模型。

*   **`manager`** (`bool`, default: `False` ) –

    指示是否为文档模块创建用户界面的标志。默认为 False。

*   **`launcher`** (`optional`, default: `None` ) –

    负责启动服务器模块的对象或函数。如果未提供，则使用 `lazyllm.launchers` 中的默认异步启动器 (`sync=False`)。

*   **`store_conf`** (`optional`, default: `None` ) –

    配置使用哪种存储后端和索引后端。

*   **`doc_fields`** (`optional`, default: `None` ) –

    配置需要存储和检索的字段继对应的类型（目前只有 Milvus 后端会用到）。


Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> from  lazyllm.tools  import Document [](#__codelineno-0-3)>>> m = lazyllm.OnlineEmbeddingModule(source="glm") [](#__codelineno-0-4)>>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False)  # or documents = Document(dataset_path='your_doc_path', embed={"key": m}, manager=False) [](#__codelineno-0-5)>>> m1 = lazyllm.TrainableModule("bge-large-zh-v1.5").start() [](#__codelineno-0-6)>>> document1 = Document(dataset_path='your_doc_path', embed={"online": m, "local": m1}, manager=False)`

`[](#__codelineno-0-1)>>> store_conf = { [](#__codelineno-0-2)>>>     'type': 'chroma', [](#__codelineno-0-3)>>>     'indices': { [](#__codelineno-0-4)>>>         'smart_embedding_index': { [](#__codelineno-0-5)>>>             'backend': 'milvus', [](#__codelineno-0-6)>>>             'kwargs': { [](#__codelineno-0-7)>>>                 'uri': '/tmp/tmp.db', [](#__codelineno-0-8)>>>                 'index_kwargs': { [](#__codelineno-0-9)>>>                     'index_type': 'HNSW', [](#__codelineno-0-10)>>>                     'metric_type': 'COSINE' [](#__codelineno-0-11)>>>                  } [](#__codelineno-0-12)>>>             }, [](#__codelineno-0-13)>>>         }, [](#__codelineno-0-14)>>>     }, [](#__codelineno-0-15)>>> } [](#__codelineno-0-16)>>> doc_fields = { [](#__codelineno-0-17)>>>     'author': DocField(data_type=DataType.VARCHAR, max_size=128, default_value=' '), [](#__codelineno-0-18)>>>     'public_year': DocField(data_type=DataType.INT32), [](#__codelineno-0-19)>>> } [](#__codelineno-0-20)>>> document2 = Document(dataset_path='your_doc_path', embed={"online": m, "local": m1}, store_conf=store_conf, doc_fields=doc_fields)`

Source code in `lazyllm/tools/rag/document.py`

|  |

```
class  Document(ModuleBase, BuiltinGroups, metaclass=_MetaDocument):
 """初始化一个具有可选用户界面的文档模块。   此构造函数初始化一个可以有或没有用户界面的文档模块。如果启用了用户界面，它还会提供一个ui界面来管理文档操作接口，并提供一个用于用户界面交互的网页。   Args:
 dataset_path (str): 数据集目录的路径。此目录应包含要由文档模块管理的文档。 embed (Optional[Union[Callable, Dict[str, Callable]]]): 用于生成文档 embedding 的对象。如果需要对文本生成多个 embedding，此处需要通过字典的方式指定多个 embedding 模型，key 标识 embedding 对应的名字, value 为对应的 embedding 模型。 manager (bool, optional): 指示是否为文档模块创建用户界面的标志。默认为 False。 launcher (optional): 负责启动服务器模块的对象或函数。如果未提供，则使用 `lazyllm.launchers` 中的默认异步启动器 (`sync=False`)。 store_conf (optional): 配置使用哪种存储后端和索引后端。 doc_fields (optional): 配置需要存储和检索的字段继对应的类型（目前只有 Milvus 后端会用到）。     Examples:
 >>> import lazyllm >>> from lazyllm.tools import Document >>> m = lazyllm.OnlineEmbeddingModule(source="glm") >>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False)  # or documents = Document(dataset_path='your_doc_path', embed={"key": m}, manager=False) >>> m1 = lazyllm.TrainableModule("bge-large-zh-v1.5").start() >>> document1 = Document(dataset_path='your_doc_path', embed={"online": m, "local": m1}, manager=False)   >>> store_conf = { >>>     'type': 'chroma', >>>     'indices': { >>>         'smart_embedding_index': { >>>             'backend': 'milvus', >>>             'kwargs': { >>>                 'uri': '/tmp/tmp.db', >>>                 'index_kwargs': { >>>                     'index_type': 'HNSW', >>>                     'metric_type': 'COSINE' >>>                  } >>>             }, >>>         }, >>>     }, >>> } >>> doc_fields = { >>>     'author': DocField(data_type=DataType.VARCHAR, max_size=128, default_value=' '), >>>     'public_year': DocField(data_type=DataType.INT32), >>> } >>> document2 = Document(dataset_path='your_doc_path', embed={"online": m, "local": m1}, store_conf=store_conf, doc_fields=doc_fields) """ class  _Manager(ModuleBase): def  __init__(self, dataset_path: Optional[str], embed: Optional[Union[Callable, Dict[str, Callable]]] = None, manager: Union[bool, str] = False, server: Union[bool, int] = False, name: Optional[str] = None, launcher: Optional[Launcher] = None, store_conf: Optional[Dict] = None, doc_fields: Optional[Dict[str, DocField]] = None, cloud: bool = False, doc_files: Optional[List[str]] = None, processor: Optional[DocumentProcessor] = None): super().__init__() self._origin_path, self._doc_files, self._cloud = dataset_path, doc_files, cloud   if dataset_path and not os.path.exists(dataset_path): defatult_path = os.path.join(lazyllm.config["data_path"], dataset_path) if os.path.exists(defatult_path): dataset_path = defatult_path elif dataset_path: dataset_path = os.path.join(os.getcwd(), dataset_path)   self._launcher: Launcher = launcher if launcher else lazyllm.launchers.remote(sync=False) self._dataset_path = dataset_path self._embed = self._get_embeds(embed) self._processor = processor   self._dlm = None if (self._cloud or self._doc_files is not None) else DocListManager( dataset_path, name, enable_path_monitoring=False if manager else True) self._kbs = CallableDict({DocListManager.DEFAULT_GROUP_NAME: DocImpl( embed=self._embed, dlm=self._dlm, doc_files=doc_files, global_metadata_desc=doc_fields, store_conf=store_conf, processor=processor, algo_name=name)})   if manager: self._manager = ServerModule(DocManager(self._dlm), launcher=self._launcher) if manager == 'ui': self._docweb = DocWebModule(doc_server=self._manager) if server: self._kbs = ServerModule(self._kbs, port=(None if isinstance(server, bool) else int(server))) self._global_metadata_desc = doc_fields   @property def  url(self): if hasattr(self, '_manager'): return self._manager._url return None   @property @deprecated('Document.manager.url') def  _url(self): return self.url   @property def  web_url(self): if hasattr(self, '_docweb'): return self._docweb.url return None   def  _get_embeds(self, embed): embeds = embed if isinstance(embed, dict) else {EMBED_DEFAULT_KEY: embed} if embed else {} for embed in embeds.values(): if isinstance(embed, ModuleBase): self._submodules.append(embed) return embeds   def  add_kb_group(self, name, doc_fields: Optional[Dict[str, DocField]] = None, store_conf: Optional[Dict] = None, embed: Optional[Union[Callable, Dict[str, Callable]]] = None): embed = self._get_embeds(embed) if embed else self._embed if isinstance(self._kbs, ServerModule): self._kbs._impl._m[name] = DocImpl(dlm=self._dlm, embed=embed, kb_group_name=name, global_metadata_desc=doc_fields, store_conf=store_conf) else: self._kbs[name] = DocImpl(dlm=self._dlm, embed=self._embed, kb_group_name=name, global_metadata_desc=doc_fields, store_conf=store_conf) self._dlm.add_kb_group(name=name)   def  get_doc_by_kb_group(self, name): return self._kbs._impl._m[name] if isinstance(self._kbs, ServerModule) else self._kbs[name]   def  stop(self): if hasattr(self, '_docweb'): self._docweb.stop() self._launcher.cleanup()   def  __call__(self, *args, **kw): return self._kbs(*args, **kw)   def  __new__(cls, *args, **kw): if url := kw.pop('url', None): name = kw.pop('name', None) assert name, 'Document name must be provided with `url`' assert not args and not kw, 'Only `name` is supported with `url`' return UrlDocument(url, name) else: return super().__new__(cls)   def  __init__(self, dataset_path: Optional[str] = None, embed: Optional[Union[Callable, Dict[str, Callable]]] = None, create_ui: bool = False, manager: Union[bool, str, "Document._Manager", DocumentProcessor] = False, server: Union[bool, int] = False, name: Optional[str] = None, launcher: Optional[Launcher] = None, doc_files: Optional[List[str]] = None, doc_fields: Dict[str, DocField] = None, store_conf: Optional[Dict] = None): super().__init__() if create_ui: lazyllm.LOG.warning('`create_ui` for Document is deprecated, use `manager` instead') manager = create_ui if isinstance(dataset_path, (tuple, list)): doc_fields = dataset_path dataset_path = None if doc_files is not None: assert dataset_path is None and not manager, ( 'Manager and dataset_path are not supported for Document with temp-files') assert store_conf is None or store_conf['type'] == 'map', ( 'Only map store is supported for Document with temp-files')   if isinstance(manager, Document._Manager): assert not server, 'Server infomation is already set to by manager' assert not launcher, 'Launcher infomation is already set to by manager' assert not manager._cloud, 'manager is not allowed to share in cloud mode' assert manager._doc_files is None, 'manager is not allowed to share with temp files' if dataset_path != manager._dataset_path and dataset_path != manager._origin_path: raise RuntimeError(f'Document path mismatch, expected `{manager._dataset_path}`' f'while received `{dataset_path}`') manager.add_kb_group(name=name, doc_fields=doc_fields, store_conf=store_conf, embed=embed) self._manager = manager self._curr_group = name else: if isinstance(manager, DocumentProcessor): processor, cloud = manager, True processor._impl.start() manager = False assert name, '`Name` of Document is necessary when using cloud service' assert store_conf['type'] != 'map', 'Cloud manager is not supported when using map store' assert not dataset_path, 'Cloud manager is not supported with local dataset path' else: cloud, processor = False, None self._manager = Document._Manager(dataset_path, embed, manager, server, name, launcher, store_conf, doc_fields, cloud=cloud, doc_files=doc_files, processor=processor) self._curr_group = DocListManager.DEFAULT_GROUP_NAME self._doc_to_db_processor: DocToDbProcessor = None   def  _list_all_files_in_dataset(self) -> List[str]: files_list = [] for root, _, files in os.walk(self._manager._dataset_path): files = [os.path.join(root, file_path) for file_path in files] files_list.extend(files) return files_list   def  connect_sql_manager( self, sql_manager: SqlManager, schma: Optional[DocInfoSchema] = None, force_refresh: bool = True, ): def  format_schema_to_dict(schema: DocInfoSchema): if schema is None: return None, None desc_dict = {ele["key"]: ele["desc"] for ele in schema} type_dict = {ele["key"]: ele["type"] for ele in schema} return desc_dict, type_dict   def  compare_schema(old_schema: DocInfoSchema, new_schema: DocInfoSchema): old_desc_dict, old_type_dict = format_schema_to_dict(old_schema) new_desc_dict, new_type_dict = format_schema_to_dict(new_schema) return old_desc_dict == new_desc_dict and old_type_dict == new_type_dict   # 1. Check valid arguments if sql_manager.check_connection().status != DBStatus.SUCCESS: raise RuntimeError(f'Failed to connect to sql manager: {sql_manager._gen_conn_url()}') pre_doc_table_schema = None if self._doc_to_db_processor: pre_doc_table_schema = self._doc_to_db_processor.doc_info_schema assert pre_doc_table_schema or schma, "doc_table_schma must be given"   schema_equal = compare_schema(pre_doc_table_schema, schma) assert ( schema_equal or force_refresh is True ), "When changing doc_table_schema, force_refresh should be set to True"   # 2. Init handler if needed need_init_processor = False if self._doc_to_db_processor is None: need_init_processor = True else: # avoid reinit for the same db if sql_manager != self._doc_to_db_processor.sql_manager: need_init_processor = True if need_init_processor: self._doc_to_db_processor = DocToDbProcessor(sql_manager)   # 3. Reset doc_table_schema if needed if schma and not schema_equal: # This api call will clear existing db table "lazyllm_doc_elements" self._doc_to_db_processor._reset_doc_info_schema(schma)   def  get_sql_manager(self): if self._doc_to_db_processor is None: raise None return self._doc_to_db_processor.sql_manager   def  extract_db_schema( self, llm: Union[OnlineChatModule, TrainableModule], print_schema: bool = False ) -> DocInfoSchema: file_paths = self._list_all_files_in_dataset() schema = extract_db_schema_from_files(file_paths, llm) if print_schema: lazyllm.LOG.info(f"Extracted Schema:\n\t{schema}\n") return schema   def  update_database(self, llm: Union[OnlineChatModule, TrainableModule]): assert self._doc_to_db_processor, "Please call connect_db to init handler first" file_paths = self._list_all_files_in_dataset() info_dicts = self._doc_to_db_processor.extract_info_from_docs(llm, file_paths) self._doc_to_db_processor.export_info_to_db(info_dicts)   @deprecated('Document(dataset_path, manager=doc.manager, name=xx, doc_fields=xx, store_conf=xx)') def  create_kb_group(self, name: str, doc_fields: Optional[Dict[str, DocField]] = None, store_conf: Optional[Dict] = None) -> "Document": self._manager.add_kb_group(name=name, doc_fields=doc_fields, store_conf=store_conf) doc = copy.copy(self) doc._curr_group = name return doc   @property @deprecated('Document._manager') def  _impls(self): return self._manager   @property def  _impl(self) -> DocImpl: return self._manager.get_doc_by_kb_group(self._curr_group)   @property def  manager(self): return self._manager._processor or self._manager   def  activate_group(self, group_name: str, embed_keys: Optional[Union[str, List[str]]] = None): if isinstance(embed_keys, str): embed_keys = [embed_keys] elif embed_keys is None: embed_keys = [] self._impl.activate_group(group_name, embed_keys)   def  activate_groups(self, groups: Union[str, List[str]]): if isinstance(groups, str): groups = [groups] for group in groups: self.activate_group(group)   @DynamicDescriptor def  create_node_group(self, name: str = None, *, transform: Callable, parent: str = LAZY_ROOT_NAME, trans_node: bool = None, num_workers: int = 0, display_name: str = None, group_type: NodeGroupType = NodeGroupType.CHUNK, **kwargs) -> None: """ 创建一个由指定规则生成的 node group。   Args:
 name (str): node group 的名称。 transform (Callable): 将 node 转换成 node group 的转换规则，函数原型是 `(DocNode, group_name, **kwargs) -> List[DocNode]`。目前内置的有 [SentenceSplitter][lazyllm.tools.SentenceSplitter]。用户也可以自定义转换规则。 trans_node (bool): 决定了transform的输入和输出是 `DocNode` 还是 `str` ，默认为None。只有在 `transform` 为 `Callable` 时才可以设置为true。 num_workers (int): Transform时所用的新线程数量，默认为0 parent (str): 需要进一步转换的节点。转换之后得到的一系列新的节点将会作为该父节点的子节点。如果不指定则从根节点开始转换。 kwargs: 和具体实现相关的参数。     Examples:   >>> import lazyllm >>> from lazyllm.tools import Document, SentenceSplitter >>> m = lazyllm.OnlineEmbeddingModule(source="glm") >>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False) >>> documents.create_node_group(name="sentences", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100) """ if isinstance(self, type): DocImpl.create_global_node_group(name, transform=transform, parent=parent, trans_node=trans_node, num_workers=num_workers, display_name=display_name, group_type=group_type, **kwargs) else: self._impl.create_node_group(name, transform=transform, parent=parent, trans_node=trans_node, num_workers=num_workers, display_name=display_name, group_type=group_type, **kwargs)   @DynamicDescriptor def  add_reader(self, pattern: str, func: Optional[Callable] = None): """ 用于实例指定文件读取器，作用范围仅对注册的 Document 对象可见。注册的文件读取器必须是 Callable 对象。只能通过函数调用的方式进行注册。并且通过实例注册的文件读取器的优先级高于通过类注册的文件读取器，并且实例和类注册的文件读取器的优先级高于系统默认的文件读取器。即优先级的顺序是：实例文件读取器 > 类文件读取器 > 系统默认文件读取器。   Args:
 pattern (str): 文件读取器适用的匹配规则 func (Callable): 文件读取器，必须是Callable的对象     Examples:   >>> from lazyllm.tools.rag import Document, DocNode >>> from lazyllm.tools.rag.readers import ReaderBase >>> class YmlReader(ReaderBase): ...     def _load_data(self, file, fs=None): ...         try: ...             import yaml ...         except ImportError: ...             raise ImportError("yaml is required to read YAML file: `pip install pyyaml`") ...         with open(file, 'r') as f: ...             data = yaml.safe_load(f) ...         print("Call the class YmlReader.") ...         return [DocNode(text=data)] ... >>> def processYml(file): ...     with open(file, 'r') as f: ...         data = f.read() ...     print("Call the function processYml.") ...     return [DocNode(text=data)] ... >>> doc1 = Document(dataset_path="your_files_path", create_ui=False) >>> doc2 = Document(dataset_path="your_files_path", create_ui=False) >>> doc1.add_reader("**/*.yml", YmlReader) >>> print(doc1._impl._local_file_reader) {'**/*.yml': <class '__main__.YmlReader'>} >>> print(doc2._impl._local_file_reader) {} >>> files = ["your_yml_files"] >>> Document.register_global_reader("**/*.yml", processYml) >>> doc1._impl._reader.load_data(input_files=files) Call the class YmlReader. >>> doc2._impl._reader.load_data(input_files=files) Call the function processYml. """ if isinstance(self, type): return DocImpl.register_global_reader(pattern=pattern, func=func) else: self._impl.add_reader(pattern, func)   @classmethod def  register_global_reader(cls, pattern: str, func: Optional[Callable] = None): """ 用于指定文件读取器，作用范围对于所有的 Document 对象都可见。注册的文件读取器必须是 Callable 对象。可以使用装饰器的方式进行注册，也可以通过函数调用的方式进行注册。   Args:
 pattern (str): 文件读取器适用的匹配规则 func (Callable): 文件读取器，必须是Callable的对象     Examples:   >>> from lazyllm.tools.rag import Document, DocNode >>> @Document.register_global_reader("**/*.yml") >>> def processYml(file): ...     with open(file, 'r') as f: ...         data = f.read() ...     return [DocNode(text=data)] ... >>> doc1 = Document(dataset_path="your_files_path", create_ui=False) >>> doc2 = Document(dataset_path="your_files_path", create_ui=False) >>> files = ["your_yml_files"] >>> docs1 = doc1._impl._reader.load_data(input_files=files) >>> docs2 = doc2._impl._reader.load_data(input_files=files) >>> print(docs1[0].text == docs2[0].text) # True """ return cls.add_reader(pattern, func)   def  get_store(self): return StorePlaceholder()   def  get_embed(self): return EmbedPlaceholder()   def  register_index(self, index_type: str, index_cls: IndexBase, *args, **kwargs) -> None: self._impl.register_index(index_type, index_cls, *args, **kwargs)   def  _forward(self, func_name: str, *args, **kw): return self._manager(self._curr_group, func_name, *args, **kw)   def  find_parent(self, target) -> Callable: """ 查找指定节点的父节点。   Args:
 group (str): 需要查找的节点名称     Examples:   >>> import lazyllm >>> from lazyllm.tools import Document, SentenceSplitter >>> m = lazyllm.OnlineEmbeddingModule(source="glm") >>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False) >>> documents.create_node_group(name="parent", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100) >>> documents.create_node_group(name="children", transform=SentenceSplitter, parent="parent", chunk_size=1024, chunk_overlap=100) >>> documents.find_parent('children') """ return functools.partial(self._forward, 'find_parent', group=target)   def  find_children(self, target) -> Callable: """ 查找指定节点的子节点。   Args:
 group (str): 需要查找的名称     Examples:   >>> import lazyllm >>> from lazyllm.tools import Document, SentenceSplitter >>> m = lazyllm.OnlineEmbeddingModule(source="glm") >>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False) >>> documents.create_node_group(name="parent", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100) >>> documents.create_node_group(name="children", transform=SentenceSplitter, parent="parent", chunk_size=1024, chunk_overlap=100) >>> documents.find_children('parent') """ return functools.partial(self._forward, 'find_children', group=target)   def  find(self, target) -> Callable: return functools.partial(self._forward, 'find', group=target)   def  forward(self, *args, **kw) -> List[DocNode]: return self._forward('retrieve', *args, **kw)   def  clear_cache(self, group_names: Optional[List[str]]) -> None: return self._forward('clear_cache', group_names)   def  _get_post_process_tasks(self): return lazyllm.pipeline(lambda *a: self._forward('_lazy_init'))   def  __repr__(self): return lazyllm.make_repr("Module", "Document", manager=hasattr(self._manager, '_manager'), server=isinstance(self._manager._kbs, ServerModule))
 ```



 |

### `add_reader(pattern, func=None)`

用于实例指定文件读取器，作用范围仅对注册的 Document 对象可见。注册的文件读取器必须是 Callable 对象。只能通过函数调用的方式进行注册。并且通过实例注册的文件读取器的优先级高于通过类注册的文件读取器，并且实例和类注册的文件读取器的优先级高于系统默认的文件读取器。即优先级的顺序是：实例文件读取器 > 类文件读取器 > 系统默认文件读取器。

Parameters:

*   **`pattern`** (`str`) –

    文件读取器适用的匹配规则

*   **`func`** (`Callable`, default: `None` ) –

    文件读取器，必须是Callable的对象


Examples:

``>>> from lazyllm.tools.rag import Document, DocNode
>>> from lazyllm.tools.rag.readers import ReaderBase
>>> class YmlReader(ReaderBase):
...     def _load_data(self, file, fs=None):
...         try:
...             import yaml
...         except ImportError:
...             raise ImportError("yaml is required to read YAML file: `pip install pyyaml`")
...         with open(file, 'r') as f:
...             data = yaml.safe_load(f)
...         print("Call the class YmlReader.")
...         return [DocNode(text=data)]
...
>>> def processYml(file):
...     with open(file, 'r') as f:
...         data = f.read()
...     print("Call the function processYml.")
...     return [DocNode(text=data)]
...
>>> doc1 = Document(dataset_path="your_files_path", create_ui=False)
>>> doc2 = Document(dataset_path="your_files_path", create_ui=False)
>>> doc1.add_reader("**/*.yml", YmlReader)
>>> print(doc1._impl._local_file_reader)
{'**/*.yml': <class '__main__.YmlReader'>}
>>> print(doc2._impl._local_file_reader)
{}
>>> files = ["your_yml_files"]
>>> Document.register_global_reader("**/*.yml", processYml)
>>> doc1._impl._reader.load_data(input_files=files)
Call the class YmlReader.
>>> doc2._impl._reader.load_data(input_files=files)
Call the function processYml.``

Source code in `lazyllm/tools/rag/document.py`

|  |

 ``@DynamicDescriptor def  add_reader(self, pattern: str, func: Optional[Callable] = None): """ 用于实例指定文件读取器，作用范围仅对注册的 Document 对象可见。注册的文件读取器必须是 Callable 对象。只能通过函数调用的方式进行注册。并且通过实例注册的文件读取器的优先级高于通过类注册的文件读取器，并且实例和类注册的文件读取器的优先级高于系统默认的文件读取器。即优先级的顺序是：实例文件读取器 > 类文件读取器 > 系统默认文件读取器。   Args:
 pattern (str): 文件读取器适用的匹配规则 func (Callable): 文件读取器，必须是Callable的对象     Examples:   >>> from lazyllm.tools.rag import Document, DocNode >>> from lazyllm.tools.rag.readers import ReaderBase >>> class YmlReader(ReaderBase): ...     def _load_data(self, file, fs=None): ...         try: ...             import yaml ...         except ImportError: ...             raise ImportError("yaml is required to read YAML file: `pip install pyyaml`") ...         with open(file, 'r') as f: ...             data = yaml.safe_load(f) ...         print("Call the class YmlReader.") ...         return [DocNode(text=data)] ... >>> def processYml(file): ...     with open(file, 'r') as f: ...         data = f.read() ...     print("Call the function processYml.") ...     return [DocNode(text=data)] ... >>> doc1 = Document(dataset_path="your_files_path", create_ui=False) >>> doc2 = Document(dataset_path="your_files_path", create_ui=False) >>> doc1.add_reader("**/*.yml", YmlReader) >>> print(doc1._impl._local_file_reader) {'**/*.yml': <class '__main__.YmlReader'>} >>> print(doc2._impl._local_file_reader) {} >>> files = ["your_yml_files"] >>> Document.register_global_reader("**/*.yml", processYml) >>> doc1._impl._reader.load_data(input_files=files) Call the class YmlReader. >>> doc2._impl._reader.load_data(input_files=files) Call the function processYml. """ if isinstance(self, type): return DocImpl.register_global_reader(pattern=pattern, func=func) else: self._impl.add_reader(pattern, func)``



 |

### `create_node_group(name=None, *, transform, parent=LAZY_ROOT_NAME, trans_node=None, num_workers=0, display_name=None, group_type=NodeGroupType.CHUNK, **kwargs)`

创建一个由指定规则生成的 node group。

Parameters:

*   **`name`** (`str`, default: `None` ) –

    node group 的名称。

*   **`transform`** (`Callable`) –

    将 node 转换成 node group 的转换规则，函数原型是 `(DocNode, group_name, **kwargs) -> List[DocNode]`。目前内置的有 [SentenceSplitter](#lazyllm.tools.SentenceSplitter "            lazyllm.tools.SentenceSplitter")。用户也可以自定义转换规则。

*   **`trans_node`** (`bool`, default: `None` ) –

    决定了transform的输入和输出是 `DocNode` 还是 `str` ，默认为None。只有在 `transform` 为 `Callable` 时才可以设置为true。

*   **`num_workers`** (`int`, default: `0` ) –

    Transform时所用的新线程数量，默认为0

*   **`parent`** (`str`, default: `LAZY_ROOT_NAME` ) –

    需要进一步转换的节点。转换之后得到的一系列新的节点将会作为该父节点的子节点。如果不指定则从根节点开始转换。

*   **`kwargs`** –

    和具体实现相关的参数。


Examples:

`>>> import lazyllm
>>> from lazyllm.tools import Document, SentenceSplitter
>>> m = lazyllm.OnlineEmbeddingModule(source="glm")
>>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False)
>>> documents.create_node_group(name="sentences", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100)`

Source code in `lazyllm/tools/rag/document.py`

|  |

 ``@DynamicDescriptor def  create_node_group(self, name: str = None, *, transform: Callable, parent: str = LAZY_ROOT_NAME, trans_node: bool = None, num_workers: int = 0, display_name: str = None, group_type: NodeGroupType = NodeGroupType.CHUNK, **kwargs) -> None: """ 创建一个由指定规则生成的 node group。   Args:
 name (str): node group 的名称。 transform (Callable): 将 node 转换成 node group 的转换规则，函数原型是 `(DocNode, group_name, **kwargs) -> List[DocNode]`。目前内置的有 [SentenceSplitter][lazyllm.tools.SentenceSplitter]。用户也可以自定义转换规则。 trans_node (bool): 决定了transform的输入和输出是 `DocNode` 还是 `str` ，默认为None。只有在 `transform` 为 `Callable` 时才可以设置为true。 num_workers (int): Transform时所用的新线程数量，默认为0 parent (str): 需要进一步转换的节点。转换之后得到的一系列新的节点将会作为该父节点的子节点。如果不指定则从根节点开始转换。 kwargs: 和具体实现相关的参数。     Examples:   >>> import lazyllm >>> from lazyllm.tools import Document, SentenceSplitter >>> m = lazyllm.OnlineEmbeddingModule(source="glm") >>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False) >>> documents.create_node_group(name="sentences", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100) """ if isinstance(self, type): DocImpl.create_global_node_group(name, transform=transform, parent=parent, trans_node=trans_node, num_workers=num_workers, display_name=display_name, group_type=group_type, **kwargs) else: self._impl.create_node_group(name, transform=transform, parent=parent, trans_node=trans_node, num_workers=num_workers, display_name=display_name, group_type=group_type, **kwargs)``



 |

### `find_children(target)`

查找指定节点的子节点。

Parameters:

*   **`group`** (`str`) –

    需要查找的名称


Examples:

`>>> import lazyllm
>>> from lazyllm.tools import Document, SentenceSplitter
>>> m = lazyllm.OnlineEmbeddingModule(source="glm")
>>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False)
>>> documents.create_node_group(name="parent", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100)
>>> documents.create_node_group(name="children", transform=SentenceSplitter, parent="parent", chunk_size=1024, chunk_overlap=100)
>>> documents.find_children('parent')`

Source code in `lazyllm/tools/rag/document.py`

|  |

 `def  find_children(self, target) -> Callable: """ 查找指定节点的子节点。   Args:
 group (str): 需要查找的名称     Examples:   >>> import lazyllm >>> from lazyllm.tools import Document, SentenceSplitter >>> m = lazyllm.OnlineEmbeddingModule(source="glm") >>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False) >>> documents.create_node_group(name="parent", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100) >>> documents.create_node_group(name="children", transform=SentenceSplitter, parent="parent", chunk_size=1024, chunk_overlap=100) >>> documents.find_children('parent') """ return functools.partial(self._forward, 'find_children', group=target)`



 |

### `find_parent(target)`

查找指定节点的父节点。

Parameters:

*   **`group`** (`str`) –

    需要查找的节点名称


Examples:

`>>> import lazyllm
>>> from lazyllm.tools import Document, SentenceSplitter
>>> m = lazyllm.OnlineEmbeddingModule(source="glm")
>>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False)
>>> documents.create_node_group(name="parent", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100)
>>> documents.create_node_group(name="children", transform=SentenceSplitter, parent="parent", chunk_size=1024, chunk_overlap=100)
>>> documents.find_parent('children')`

Source code in `lazyllm/tools/rag/document.py`

|  |

 `def  find_parent(self, target) -> Callable: """ 查找指定节点的父节点。   Args:
 group (str): 需要查找的节点名称     Examples:   >>> import lazyllm >>> from lazyllm.tools import Document, SentenceSplitter >>> m = lazyllm.OnlineEmbeddingModule(source="glm") >>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False) >>> documents.create_node_group(name="parent", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100) >>> documents.create_node_group(name="children", transform=SentenceSplitter, parent="parent", chunk_size=1024, chunk_overlap=100) >>> documents.find_parent('children') """ return functools.partial(self._forward, 'find_parent', group=target)`



 |

### `register_global_reader(pattern, func=None)` `classmethod`

用于指定文件读取器，作用范围对于所有的 Document 对象都可见。注册的文件读取器必须是 Callable 对象。可以使用装饰器的方式进行注册，也可以通过函数调用的方式进行注册。

Parameters:

*   **`pattern`** (`str`) –

    文件读取器适用的匹配规则

*   **`func`** (`Callable`, default: `None` ) –

    文件读取器，必须是Callable的对象


Examples:

`>>> from lazyllm.tools.rag import Document, DocNode
>>> @Document.register_global_reader("**/*.yml")
>>> def processYml(file):
...     with open(file, 'r') as f:
...         data = f.read()
...     return [DocNode(text=data)]
...
>>> doc1 = Document(dataset_path="your_files_path", create_ui=False)
>>> doc2 = Document(dataset_path="your_files_path", create_ui=False)
>>> files = ["your_yml_files"]
>>> docs1 = doc1._impl._reader.load_data(input_files=files)
>>> docs2 = doc2._impl._reader.load_data(input_files=files)
>>> print(docs1[0].text == docs2[0].text)
# True`

Source code in `lazyllm/tools/rag/document.py`

|  |

 `@classmethod def  register_global_reader(cls, pattern: str, func: Optional[Callable] = None): """ 用于指定文件读取器，作用范围对于所有的 Document 对象都可见。注册的文件读取器必须是 Callable 对象。可以使用装饰器的方式进行注册，也可以通过函数调用的方式进行注册。   Args:
 pattern (str): 文件读取器适用的匹配规则 func (Callable): 文件读取器，必须是Callable的对象     Examples:   >>> from lazyllm.tools.rag import Document, DocNode >>> @Document.register_global_reader("**/*.yml") >>> def processYml(file): ...     with open(file, 'r') as f: ...         data = f.read() ...     return [DocNode(text=data)] ... >>> doc1 = Document(dataset_path="your_files_path", create_ui=False) >>> doc2 = Document(dataset_path="your_files_path", create_ui=False) >>> files = ["your_yml_files"] >>> docs1 = doc1._impl._reader.load_data(input_files=files) >>> docs2 = doc2._impl._reader.load_data(input_files=files) >>> print(docs1[0].text == docs2[0].text) # True """ return cls.add_reader(pattern, func)`



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`

文件读取器的基类，它继承自 ModuleBase 基类，具有 Callable 的能力，继承自该类的子类只需要实现 \_load\_data 函数即可，它的返回参数类型为 List\[DocNode\]. 一般 \_load\_data 函数的入参为 file (Path), fs(AbstractFileSystem) 三个参数。

Parameters:

*   **`args`** (`Any`, default: `()` ) –

    根据需要传输相应的位置参数

*   **`return_trace`** (`bool`, default: `True` ) –

    设置是否记录trace日志

*   **`kwargs`** (`Dict`, default: `{}` ) –

    根据需要传输相应的关键字参数


Examples:

``>>> from lazyllm.tools.rag.readers import ReaderBase
>>> from lazyllm.tools.rag import DocNode, Document
>>> from typing import Dict, Optional, List
>>> from pathlib import Path
>>> from fsspec import AbstractFileSystem
>>> @Document.register_global_reader("**/*.yml")
>>> class YmlReader(ReaderBase):
...     def _load_data(self, file: Path, fs: Optional[AbstractFileSystem] = None) -> List[DocNode]:
...         try:
...             import yaml
...         except ImportError:
...             raise ImportError("yaml is required to read YAML file: `pip install pyyaml`")
...         with open(file, 'r') as f:
...             data = yaml.safe_load(f)
...         print("Call the class YmlReader.")
...         return [DocNode(text=data)]
...
>>> files = ["your_yml_files"]
>>> doc = Document(dataset_path="your_files_path", create_ui=False)
>>> reader = doc._impl._reader.load_data(input_files=files)
# Call the class YmlReader.``

Source code in `lazyllm/tools/rag/readers/readerBase.py`

|  |

``class  LazyLLMReaderBase(ModuleBase, metaclass=LazyLLMRegisterMetaClass):
 """ 文件读取器的基类，它继承自 ModuleBase 基类，具有 Callable 的能力，继承自该类的子类只需要实现 _load_data 函数即可，它的返回参数类型为 List[DocNode]. 一般 _load_data 函数的入参为 file (Path), fs(AbstractFileSystem) 三个参数。   Args:
 args (Any): 根据需要传输相应的位置参数 return_trace (bool): 设置是否记录trace日志 kwargs (Dict): 根据需要传输相应的关键字参数     Examples:   >>> from lazyllm.tools.rag.readers import ReaderBase >>> from lazyllm.tools.rag import DocNode, Document >>> from typing import Dict, Optional, List >>> from pathlib import Path >>> from fsspec import AbstractFileSystem >>> @Document.register_global_reader("**/*.yml") >>> class YmlReader(ReaderBase): ...     def _load_data(self, file: Path, fs: Optional[AbstractFileSystem] = None) -> List[DocNode]: ...         try: ...             import yaml ...         except ImportError: ...             raise ImportError("yaml is required to read YAML file: `pip install pyyaml`") ...         with open(file, 'r') as f: ...             data = yaml.safe_load(f) ...         print("Call the class YmlReader.") ...         return [DocNode(text=data)] ... >>> files = ["your_yml_files"] >>> doc = Document(dataset_path="your_files_path", create_ui=False) >>> reader = doc._impl._reader.load_data(input_files=files) # Call the class YmlReader. """ def  __init__(self, *args, return_trace: bool = True, **kwargs): super().__init__(return_trace=return_trace)   def  _lazy_load_data(self, *args, **load_kwargs) -> Iterable[DocNode]: raise NotImplementedError(f"{self.__class__.__name__} does not implement lazy_load_data method.")   def  _load_data(self, *args, **load_kwargs) -> List[DocNode]: return list(self._lazy_load_data(*args, **load_kwargs))   def  forward(self, *args, **kwargs) -> List[DocNode]: return self._load_data(*args, **kwargs)``



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase (lazyllm.ModuleBase)")`, `_PostProcess`

用于创建节点（文档）后处理和重排序的模块。

Parameters:

*   **`name`** (`str`, default: `'ModuleReranker'` ) –

    用于后处理和重排序过程的排序器类型。默认为 'Reranker'。

*   **`kwargs`** –

    传递给重新排序器实例化的其他关键字参数。


详细解释排序器类型

*   Reranker: 实例化一个具有指定模型和 top\_n 参数的 SentenceTransformerRerank 重排序器。
*   KeywordFilter: 实例化一个具有指定必需和排除关键字的 KeywordNodePostprocessor。它根据这些关键字的存在或缺失来过滤节点。

Examples:

`>>> import lazyllm
>>> from lazyllm.tools import Document, Reranker, Retriever
>>> m = lazyllm.OnlineEmbeddingModule()
>>> documents = Document(dataset_path='/path/to/user/data', embed=m, manager=False)
>>> retriever = Retriever(documents, group_name='CoarseChunk', similarity='bm25', similarity_cut_off=0.01, topk=6)
>>> reranker = Reranker(name='ModuleReranker', model='bge-reranker-large', topk=1)
>>> ppl = lazyllm.ActionModule(retriever, reranker)
>>> ppl.start()
>>> print(ppl("user query"))`

Source code in `lazyllm/tools/rag/rerank.py`

|  |

``class  Reranker(ModuleBase, _PostProcess):
 """用于创建节点（文档）后处理和重排序的模块。   Args:
 name: 用于后处理和重排序过程的排序器类型。默认为 'Reranker'。 kwargs: 传递给重新排序器实例化的其他关键字参数。   详细解释排序器类型   - Reranker: 实例化一个具有指定模型和 top_n 参数的 SentenceTransformerRerank 重排序器。 - KeywordFilter: 实例化一个具有指定必需和排除关键字的 KeywordNodePostprocessor。它根据这些关键字的存在或缺失来过滤节点。     Examples:   >>> import lazyllm >>> from lazyllm.tools import Document, Reranker, Retriever >>> m = lazyllm.OnlineEmbeddingModule() >>> documents = Document(dataset_path='/path/to/user/data', embed=m, manager=False) >>> retriever = Retriever(documents, group_name='CoarseChunk', similarity='bm25', similarity_cut_off=0.01, topk=6) >>> reranker = Reranker(name='ModuleReranker', model='bge-reranker-large', topk=1) >>> ppl = lazyllm.ActionModule(retriever, reranker) >>> ppl.start() >>> print(ppl("user query")) """ registered_reranker = dict()   def  __new__(cls, name: str = "ModuleReranker", *args, **kwargs): assert name in cls.registered_reranker, f"Reranker: {name} is not registered, please register first." item = cls.registered_reranker[name] if isinstance(item, type) and issubclass(item, Reranker): return super(Reranker, cls).__new__(item) else: return super(Reranker, cls).__new__(cls)   def  __init__(self, name: str = "ModuleReranker", target: Optional[str] = None, output_format: Optional[str] = None, join: Union[bool, str] = False, **kwargs) -> None: super().__init__() self._name = name self._kwargs = kwargs lazyllm.deprecated(bool(target), '`target` parameter of reranker') _PostProcess.__init__(self, output_format, join)   def  forward(self, nodes: List[DocNode], query: str = "") -> List[DocNode]: results = self.registered_reranker[self._name](nodes, query=query, **self._kwargs) LOG.debug(f"Rerank use `{self._name}` and get nodes: {results}") return self._post_process(results)   @classmethod def  register_reranker( cls: "Reranker", func: Optional[Callable] = None, batch: bool = False ): def  decorator(f): if isinstance(f, type): cls.registered_reranker[f.__name__] = f return f else: def  wrapper(nodes, **kwargs): if batch: return f(nodes, **kwargs) else: results = [f(node, **kwargs) for node in nodes] return [result for result in results if result]   cls.registered_reranker[f.__name__] = wrapper return wrapper   return decorator(func) if func else decorator``



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase (lazyllm.ModuleBase)")`, `_PostProcess`

创建一个用于文档查询和检索的检索模块。此构造函数初始化一个检索模块，该模块根据指定的相似度度量配置文档检索过程。

Parameters:

*   **`doc`** (`object`) –

    文档模块实例。该文档模块可以是单个实例，也可以是一个实例的列表。如果是单个实例，表示对单个Document进行检索，如果是实例的列表，则表示对多个Document进行检索。

*   **`group_name`** (`str`) –

    在哪个 node group 上进行检索。

*   **`similarity`** (`Optional[str]`, default: `None` ) –

    用于设置文档检索的相似度函数。默认为 'dummy'。候选集包括 \["bm25", "bm25\_chinese", "cosine"\]。

*   **`similarity_cut_off`** (`Union[float, Dict[str, float]]`, default: `float('-inf')` ) –

    当相似度低于指定值时丢弃该文档。在多 embedding 场景下，如果需要对不同的 embedding 指定不同的值，则需要使用字典的方式指定，key 表示指定的是哪个 embedding，value 表示相应的阈值。如果所有的 embedding 使用同一个阈值，则只指定一个数值即可。

*   **`index`** (`str`, default: `'default'` ) –

    用于文档检索的索引类型。目前仅支持 'default'。

*   **`topk`** (`int`, default: `6` ) –

    表示取相似度最高的多少篇文档。

*   **`embed_keys`** (`Optional[List[str]]`, default: `None` ) –

    表示通过哪些 embedding 做检索，不指定表示用全部 embedding 进行检索。

*   **`similarity_kw`** –

    传递给 similarity 计算函数的其它参数。

*   **`output_format`** (`Optional[str]`, default: `None` ) –

    代表输出格式，默认为None，可选值有 'content' 和 'dict'，其中 content 对应输出格式为字符串，dict 对应字典。

*   **`join`** (`Union[bool, str]`, default: `False` ) –

    是否联合输出的 k 个节点，当输出格式为 content 时，如果设置该值为 True，则输出一个长字符串，如果设置为 False 则输出一个字符串列表，其中每个字符串对应每个节点的文本内容。当输出格式是 dict 时，不能联合输出，此时join默认为False,，将输出一个字典，包括'content、'embedding'、'metadata'三个key。


其中 `group_name` 有三个内置的切分策略，都是使用 `SentenceSplitter` 做切分，区别在于块大小不同：

*   CoarseChunk: 块大小为 1024，重合长度为 100
*   MediumChunk: 块大小为 256，重合长度为 25
*   FineChunk: 块大小为 128，重合长度为 12

此外，LazyLLM提供了内置的`Image`节点组存储了所有图像节点，支持图像嵌入和检索。

Examples:

`>>> import lazyllm
>>> from lazyllm.tools import Retriever, Document, SentenceSplitter
>>> m = lazyllm.OnlineEmbeddingModule()
>>> documents = Document(dataset_path='/path/to/user/data', embed=m, manager=False)
>>> rm = Retriever(documents, group_name='CoarseChunk', similarity='bm25', similarity_cut_off=0.01, topk=6)
>>> rm.start()
>>> print(rm("user query"))
>>> m1 = lazyllm.TrainableModule('bge-large-zh-v1.5').start()
>>> document1 = Document(dataset_path='/path/to/user/data', embed={'online':m , 'local': m1}, manager=False)
>>> document1.create_node_group(name='sentences', transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100)
>>> retriever = Retriever(document1, group_name='sentences', similarity='cosine', similarity_cut_off=0.4, embed_keys=['local'], topk=3)
>>> print(retriever("user query"))
>>> document2 = Document(dataset_path='/path/to/user/data', embed={'online':m , 'local': m1}, manager=False)
>>> document2.create_node_group(name='sentences', transform=SentenceSplitter, chunk_size=512, chunk_overlap=50)
>>> retriever2 = Retriever([document1, document2], group_name='sentences', similarity='cosine', similarity_cut_off=0.4, embed_keys=['local'], topk=3)
>>> print(retriever2("user query"))
>>>
>>> filters = {
>>>     "author": ["A", "B", "C"],
>>>     "public_year": [2002, 2003, 2004],
>>> }
>>> document3 = Document(dataset_path='/path/to/user/data', embed={'online':m , 'local': m1}, manager=False)
>>> document3.create_node_group(name='sentences', transform=SentenceSplitter, chunk_size=512, chunk_overlap=50)
>>> retriever3 = Retriever([document1, document3], group_name='sentences', similarity='cosine', similarity_cut_off=0.4, embed_keys=['local'], topk=3)
>>> print(retriever3(query="user query", filters=filters))
>>> document4 = Document(dataset_path='/path/to/user/data', embed=lazyllm.TrainableModule('siglip'))
>>> retriever4 = Retriever(document4, group_name='Image', similarity='cosine')
>>> nodes = retriever4("user query")
>>> print([node.get_content() for node in nodes])
>>> document5 = Document(dataset_path='/path/to/user/data', embed=m, manager=False)
>>> rm = Retriever(document5, group_name='CoarseChunk', similarity='bm25_chinese', similarity_cut_off=0.01, topk=3, output_format='content')
>>> rm.start()
>>> print(rm("user query"))
>>> document6 = Document(dataset_path='/path/to/user/data', embed=m, manager=False)
>>> rm = Retriever(document6, group_name='CoarseChunk', similarity='bm25_chinese', similarity_cut_off=0.01, topk=3, output_format='content', join=True)
>>> rm.start()
>>> print(rm("user query"))
>>> document7 = Document(dataset_path='/path/to/user/data', embed=m, manager=False)
>>> rm = Retriever(document7, group_name='CoarseChunk', similarity='bm25_chinese', similarity_cut_off=0.01, topk=3, output_format='dict')
>>> rm.start()
>>> print(rm("user query"))`

Source code in `lazyllm/tools/rag/retriever.py`

|  |

``class  Retriever(ModuleBase, _PostProcess):
 """ 创建一个用于文档查询和检索的检索模块。此构造函数初始化一个检索模块，该模块根据指定的相似度度量配置文档检索过程。   Args:
 doc: 文档模块实例。该文档模块可以是单个实例，也可以是一个实例的列表。如果是单个实例，表示对单个Document进行检索，如果是实例的列表，则表示对多个Document进行检索。 group_name: 在哪个 node group 上进行检索。 similarity: 用于设置文档检索的相似度函数。默认为 'dummy'。候选集包括 ["bm25", "bm25_chinese", "cosine"]。 similarity_cut_off: 当相似度低于指定值时丢弃该文档。在多 embedding 场景下，如果需要对不同的 embedding 指定不同的值，则需要使用字典的方式指定，key 表示指定的是哪个 embedding，value 表示相应的阈值。如果所有的 embedding 使用同一个阈值，则只指定一个数值即可。 index: 用于文档检索的索引类型。目前仅支持 'default'。 topk: 表示取相似度最高的多少篇文档。 embed_keys: 表示通过哪些 embedding 做检索，不指定表示用全部 embedding 进行检索。 similarity_kw: 传递给 similarity 计算函数的其它参数。 output_format: 代表输出格式，默认为None，可选值有 'content' 和 'dict'，其中 content 对应输出格式为字符串，dict 对应字典。 join: 是否联合输出的 k 个节点，当输出格式为 content 时，如果设置该值为 True，则输出一个长字符串，如果设置为 False 则输出一个字符串列表，其中每个字符串对应每个节点的文本内容。当输出格式是 dict 时，不能联合输出，此时join默认为False,，将输出一个字典，包括'content、'embedding'、'metadata'三个key。   其中 `group_name` 有三个内置的切分策略，都是使用 `SentenceSplitter` 做切分，区别在于块大小不同：   - CoarseChunk: 块大小为 1024，重合长度为 100 - MediumChunk: 块大小为 256，重合长度为 25 - FineChunk: 块大小为 128，重合长度为 12   此外，LazyLLM提供了内置的`Image`节点组存储了所有图像节点，支持图像嵌入和检索。     Examples:   >>> import lazyllm >>> from lazyllm.tools import Retriever, Document, SentenceSplitter >>> m = lazyllm.OnlineEmbeddingModule() >>> documents = Document(dataset_path='/path/to/user/data', embed=m, manager=False) >>> rm = Retriever(documents, group_name='CoarseChunk', similarity='bm25', similarity_cut_off=0.01, topk=6) >>> rm.start() >>> print(rm("user query")) >>> m1 = lazyllm.TrainableModule('bge-large-zh-v1.5').start() >>> document1 = Document(dataset_path='/path/to/user/data', embed={'online':m , 'local': m1}, manager=False) >>> document1.create_node_group(name='sentences', transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100) >>> retriever = Retriever(document1, group_name='sentences', similarity='cosine', similarity_cut_off=0.4, embed_keys=['local'], topk=3) >>> print(retriever("user query")) >>> document2 = Document(dataset_path='/path/to/user/data', embed={'online':m , 'local': m1}, manager=False) >>> document2.create_node_group(name='sentences', transform=SentenceSplitter, chunk_size=512, chunk_overlap=50) >>> retriever2 = Retriever([document1, document2], group_name='sentences', similarity='cosine', similarity_cut_off=0.4, embed_keys=['local'], topk=3) >>> print(retriever2("user query")) >>> >>> filters = { >>>     "author": ["A", "B", "C"], >>>     "public_year": [2002, 2003, 2004], >>> } >>> document3 = Document(dataset_path='/path/to/user/data', embed={'online':m , 'local': m1}, manager=False) >>> document3.create_node_group(name='sentences', transform=SentenceSplitter, chunk_size=512, chunk_overlap=50) >>> retriever3 = Retriever([document1, document3], group_name='sentences', similarity='cosine', similarity_cut_off=0.4, embed_keys=['local'], topk=3) >>> print(retriever3(query="user query", filters=filters)) >>> document4 = Document(dataset_path='/path/to/user/data', embed=lazyllm.TrainableModule('siglip')) >>> retriever4 = Retriever(document4, group_name='Image', similarity='cosine') >>> nodes = retriever4("user query") >>> print([node.get_content() for node in nodes]) >>> document5 = Document(dataset_path='/path/to/user/data', embed=m, manager=False) >>> rm = Retriever(document5, group_name='CoarseChunk', similarity='bm25_chinese', similarity_cut_off=0.01, topk=3, output_format='content') >>> rm.start() >>> print(rm("user query")) >>> document6 = Document(dataset_path='/path/to/user/data', embed=m, manager=False) >>> rm = Retriever(document6, group_name='CoarseChunk', similarity='bm25_chinese', similarity_cut_off=0.01, topk=3, output_format='content', join=True) >>> rm.start() >>> print(rm("user query")) >>> document7 = Document(dataset_path='/path/to/user/data', embed=m, manager=False) >>> rm = Retriever(document7, group_name='CoarseChunk', similarity='bm25_chinese', similarity_cut_off=0.01, topk=3, output_format='dict') >>> rm.start() >>> print(rm("user query")) """ def  __init__(self, doc: object, group_name: str, similarity: Optional[str] = None, similarity_cut_off: Union[float, Dict[str, float]] = float("-inf"), index: str = "default", topk: int = 6, embed_keys: Optional[List[str]] = None, target: Optional[str] = None, output_format: Optional[str] = None, join: Union[bool, str] = False, **kwargs): super().__init__()   if similarity: _, mode, _ = registered_similarities[similarity] else: mode = 'embedding'  # TODO FIXME XXX should be removed after similarity args refactor group_name, target = str(group_name), (str(target) if target else None)   self._docs: List[Document] = [doc] if isinstance(doc, Document) else doc for doc in self._docs: assert isinstance(doc, (Document, UrlDocument)), 'Only Document or List[Document] are supported' if isinstance(doc, UrlDocument): continue self._submodules.append(doc) if mode == 'embedding' and embed_keys is None: embed_keys = list(doc._impl.embed.keys()) doc.activate_group(group_name, embed_keys) if target: doc.activate_group(target)   self._group_name = group_name self._similarity = similarity  # similarity function str self._similarity_cut_off = similarity_cut_off self._index = index self._topk = topk self._similarity_kw = kwargs  # kw parameters self._embed_keys = embed_keys self._target = target _PostProcess.__init__(self, output_format, join)   @once_wrapper def  _lazy_init(self): docs = [doc for doc in self._docs if isinstance(doc, UrlDocument) or self._group_name in doc._impl.node_groups or self._group_name in DocImpl._builtin_node_groups or self._group_name in DocImpl._global_node_groups] if not docs: raise RuntimeError(f'Group {self._group_name} not found in document {self._docs}') self._docs = docs   def  forward( self, query: str, filters: Optional[Dict[str, Union[str, int, List, Set]]] = None, **kwargs ) -> Union[List[DocNode], str]: self._lazy_init() all_nodes: List[DocNode] = [] for doc in self._docs: nodes = doc.forward(query=query, group_name=self._group_name, similarity=self._similarity, similarity_cut_off=self._similarity_cut_off, index=self._index, topk=self._topk, similarity_kws=self._similarity_kw, embed_keys=self._embed_keys, filters=filters, **kwargs) if nodes and self._target and self._target != nodes[0]._group: nodes = doc.find(self._target)(nodes) all_nodes.extend(nodes) return self._post_process(all_nodes)``



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase (lazyllm.ModuleBase)")`

DocManager类管理文档列表及相关操作，并通过API提供文档上传、删除、分组等功能。

Parameters:

*   **`dlm`** (`DocListManager`) –

    文档列表管理器，用于处理具体的文档操作。


Source code in `lazyllm/tools/rag/doc_manager.py`

|  |

``class  DocManager(lazyllm.ModuleBase):
 """ DocManager类管理文档列表及相关操作，并通过API提供文档上传、删除、分组等功能。   Args:
 dlm (DocListManager): 文档列表管理器，用于处理具体的文档操作。   """
 def  __init__(self, dlm: DocListManager) -> None: super().__init__() # disable path monitoring in case of competition adding/deleting files self._manager = dlm self._manager.enable_path_monitoring = False   def  __reduce__(self): self._manager.enable_path_monitoring = False return (__class__, (self._manager,))   @app.get("/", response_model=BaseResponse, summary="docs") def  document(self): """ 提供默认文档页面的重定向接口。   **Returns:**   - RedirectResponse: 重定向到 `/docs` 页面。 """
 return RedirectResponse(url="/docs")   @app.get("/list_kb_groups") def  list_kb_groups(self): """ 列出所有文档分组的接口。   **Returns:**   - BaseResponse: 包含所有文档分组的数据。 """
 try: return BaseResponse(data=self._manager.list_all_kb_group()) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   # returns an error message if invalid @staticmethod def  _validate_metadata(metadata: Dict) -> Optional[str]: if metadata.get(RAG_DOC_ID): return f"metadata MUST not contain key `{RAG_DOC_ID}`" if metadata.get(RAG_DOC_PATH): return f"metadata MUST not contain key `{RAG_DOC_PATH}`" return None   def  _gen_unique_filepath(self, file_path: str) -> str: suffix = os.path.splitext(file_path)[1] prefix = file_path[0: len(file_path) - len(suffix)] pattern = f"{prefix}%{suffix}" MAX_TRIES = 10000 exist_paths = set(self._manager.get_existing_paths_by_pattern(pattern)) if file_path not in exist_paths: return file_path for i in range(1, MAX_TRIES): new_path = f"{prefix}-{i}{suffix}" if new_path not in exist_paths: return new_path return f"{str(uuid.uuid4())}{suffix}"   @app.post("/upload_files") def  upload_files(self, files: List[UploadFile], override: bool = False,  # noqa C901 metadatas: Optional[str] = None, user_path: Optional[str] = None): """ 上传文件并更新其状态的接口。可以同时上传多个文件。   Args:
 files (List[UploadFile]): 上传的文件列表。 override (bool): 是否覆盖已存在的文件。默认为False。 metadatas (Optional[str]): 文件的元数据，JSON格式。 user_path (Optional[str]): 用户自定义的文件上传路径。   **Returns:**   - BaseResponse: 上传结果和文件ID。 """
 try: if user_path: user_path = user_path.lstrip('/') if metadatas: metadatas: Optional[List[Dict[str, str]]] = json.loads(metadatas) if len(files) != len(metadatas): return BaseResponse(code=400, msg='Length of files and metadatas should be the same', data=None) for idx, mt in enumerate(metadatas): err_msg = self._validate_metadata(mt) if err_msg: return BaseResponse(code=400, msg=f'file [{files[idx].filename}]: {err_msg}', data=None) file_paths = [os.path.join(self._manager._path, user_path or '', file.filename) for file in files] paths_is_new = [True] * len(file_paths) if override is True: is_success, msg, paths_is_new = self._manager.validate_paths(file_paths) if not is_success: return BaseResponse(code=500, msg=msg, data=None) directorys = set(os.path.dirname(path) for path in file_paths) [os.makedirs(directory, exist_ok=True) for directory in directorys if directory] ids, results = [], [] for i in range(len(files)): file_path = file_paths[i] content = files[i].file.read() metadata = metadatas[i] if metadatas else None if override is False: file_path = self._gen_unique_filepath(file_path) with open(file_path, 'wb') as f: f.write(content) msg = "success" doc_id = gen_docid(file_path) if paths_is_new[i]: docs = self._manager.add_files( [file_path], metadatas=[metadata], status=DocListManager.Status.success) if not docs: msg = f"Failed: path {file_path} already exists in Database." else: self._manager.update_kb_group(cond_file_ids=[doc_id], new_need_reparse=True) msg = f"Success: path {file_path} will be reparsed." ids.append(doc_id) results.append(msg) return BaseResponse(data=[ids, results]) except Exception as e: lazyllm.LOG.error(f'upload_files exception: {e}') return BaseResponse(code=500, msg=str(e), data=None)   @app.post("/add_files") def  add_files(self, files: List[str] = Body(...), group_name: str = Body(None), metadatas: Optional[str] = Body(None)): try: if metadatas: metadatas: Optional[List[Dict[str, str]]] = json.loads(metadatas) assert len(files) == len(metadatas), 'Length of files and metadatas should be the same'   exists_files_info = self._manager.list_files(limit=None, details=True, status=DocListManager.Status.all) exists_files_info = {row[2]: row[0] for row in exists_files_info}   exist_ids = [] new_files = [] new_metadatas = [] id_mapping = {}   for idx, file in enumerate(files): if os.path.exists(file): exist_id = exists_files_info.get(file, None) if exist_id: update_kws = dict(fileid=exist_id, status=DocListManager.Status.success) if metadatas: update_kws["meta"] = json.dumps(metadatas[idx]) self._manager.update_file_message(**update_kws) exist_ids.append(exist_id) id_mapping[file] = exist_id else: new_files.append(file) if metadatas: new_metadatas.append(metadatas[idx]) else: id_mapping[file] = None   new_ids = self._manager.add_files(new_files, metadatas=new_metadatas, status=DocListManager.Status.success) if group_name: self._manager.add_files_to_kb_group(new_ids + exist_ids, group=group_name)   for file, new_id in zip(new_files, new_ids): id_mapping[file] = new_id return_ids = [id_mapping[file] for file in files]   return BaseResponse(data=return_ids) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   @app.get("/list_files") def  list_files(self, limit: Optional[int] = None, details: bool = True, alive: Optional[bool] = None): """ 列出已上传文件的接口。   Args:
 limit (Optional[int]): 返回的文件数量限制。默认为None。 details (bool): 是否返回详细信息。默认为True。 alive (Optional[bool]): 如果为True，只返回未删除的文件。默认为None。   **Returns:**   - BaseResponse: 文件列表数据。 """
 try: status = [DocListManager.Status.success, DocListManager.Status.waiting, DocListManager.Status.working, DocListManager.Status.failed] if alive else DocListManager.Status.all return BaseResponse(data=self._manager.list_files(limit=limit, details=details, status=status)) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   @app.get("/reparse_files") def  reparse_files(self, file_ids: List[str], group_name: Optional[str] = None): try: self._manager.update_need_reparsing(file_ids, group_name) return BaseResponse() except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   @app.get("/list_files_in_group") def  list_files_in_group(self, group_name: Optional[str] = None, limit: Optional[int] = None, alive: Optional[bool] = None): """ 列出指定分组中文件的接口。   Args:
 group_name (Optional[str]): 文件分组名称。 limit (Optional[int]): 返回的文件数量限制。默认为None。 alive (Optional[bool]): 是否只返回未删除的文件。   **Returns:**   - BaseResponse: 分组文件列表。 """
 try: status = [DocListManager.Status.success, DocListManager.Status.waiting, DocListManager.Status.working, DocListManager.Status.failed] if alive else DocListManager.Status.all return BaseResponse(data=self._manager.list_kb_group_files(group_name, limit, details=True, status=status)) except Exception as e: return BaseResponse(code=500, msg=str(e) + '\ntraceback:\n' + str(traceback.format_exc()), data=None)   class  FileGroupRequest(BaseModel): file_ids: List[str] group_name: Optional[str] = Field(None)   @app.post("/add_files_to_group_by_id") def  add_files_to_group_by_id(self, request: FileGroupRequest): """ 通过文件ID将文件添加到指定分组的接口。   Args:
 request (FileGroupRequest): 包含文件ID和分组名称的请求。   **Returns:**   - BaseResponse: 操作结果。 """
 try: self._manager.add_files_to_kb_group(request.file_ids, request.group_name) return BaseResponse() except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   @app.post("/add_files_to_group") def  add_files_to_group(self, files: List[UploadFile], group_name: str, override: bool = False, metadatas: Optional[str] = None, user_path: Optional[str] = None): """ 将文件上传后直接添加到指定分组的接口。   Args:
 files (List[UploadFile]): 上传的文件列表。 group_name (str): 要添加到的分组名称。 override (bool): 是否覆盖已存在的文件。默认为False。 metadatas (Optional[str]): 文件元数据，JSON格式。 user_path (Optional[str]): 用户自定义的文件上传路径。   **Returns:**   - BaseResponse: 操作结果和文件ID。 """
 try: response = self.upload_files(files, override=override, metadatas=metadatas, user_path=user_path) if response.code != 200: return response ids = response.data[0] self._manager.add_files_to_kb_group(ids, group_name) return BaseResponse(data=ids) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   @app.post("/delete_files") def  delete_files(self, request: FileGroupRequest): """ 删除指定文件的接口。   Args:
 request (FileGroupRequest): 包含文件ID和分组名称的请求。   **Returns:**   - BaseResponse: 删除操作结果。 """
 try: if request.group_name: return self.delete_files_from_group(request) else: documents = self._manager.delete_files(request.file_ids) deleted_ids = set([ele.doc_id for ele in documents]) for doc in documents: if os.path.exists(path := doc.path): os.remove(path) results = ["Success" if ele.doc_id in deleted_ids else "Failed" for ele in documents] return BaseResponse(data=[request.file_ids, results]) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   @app.post("/delete_files_from_group") def  delete_files_from_group(self, request: FileGroupRequest): try: self._manager.update_kb_group(cond_file_ids=request.file_ids, cond_group=request.group_name, new_status=DocListManager.Status.deleting) return BaseResponse() except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   class  AddMetadataRequest(BaseModel): doc_ids: List[str] kv_pair: Dict[str, Union[bool, int, float, str, list]]   @app.post("/add_metadata") def  add_metadata(self, add_metadata_request: AddMetadataRequest): doc_ids = add_metadata_request.doc_ids kv_pair = add_metadata_request.kv_pair try: docs = self._manager.get_docs(doc_ids) if not docs: return BaseResponse(code=400, msg="Failed, no doc found") doc_meta = {} for doc in docs: meta_dict = json.loads(doc.meta) if doc.meta else {} for k, v in kv_pair.items(): if k not in meta_dict or not meta_dict[k]: meta_dict[k] = v elif isinstance(meta_dict[k], list): meta_dict[k].extend(v) if isinstance(v, list) else meta_dict[k].append(v) else: meta_dict[k] = ([meta_dict[k]] + v) if isinstance(v, list) else [meta_dict[k], v] doc_meta[doc.doc_id] = meta_dict self._manager.set_docs_new_meta(doc_meta) return BaseResponse(data=None) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   class  DeleteMetadataRequest(BaseModel): doc_ids: List[str] keys: Optional[List[str]] = Field(None) kv_pair: Optional[Dict[str, Union[bool, int, float, str, list]]] = Field(None)   def  _inplace_del_meta(self, meta_dict, kv_pair: Dict[str, Union[None, bool, int, float, str, list]]): # alert: meta_dict is not a deepcopy for k, v in kv_pair.items(): if k not in meta_dict: continue if v is None: meta_dict.pop(k, None) elif isinstance(meta_dict[k], list): if isinstance(v, (bool, int, float, str)): v = [v] # delete v exists in meta_dict[k] meta_dict[k] = list(set(meta_dict[k]) - set(v)) else: # old meta[k] not a list, use v as condition to delete the key if meta_dict[k] == v: meta_dict.pop(k, None)   @app.post("/delete_metadata_item") def  delete_metadata_item(self, del_metadata_request: DeleteMetadataRequest): doc_ids = del_metadata_request.doc_ids kv_pair = del_metadata_request.kv_pair keys = del_metadata_request.keys try: if keys is not None: # convert keys to kv_pair if kv_pair: kv_pair.update({k: None for k in keys}) else: kv_pair = {k: None for k in keys} if not kv_pair: # clear metadata self._manager.set_docs_new_meta({doc_id: {} for doc_id in doc_ids}) else: docs = self._manager.get_docs(doc_ids) if not docs: return BaseResponse(code=400, msg="Failed, no doc found") doc_meta = {} for doc in docs: meta_dict = json.loads(doc.meta) if doc.meta else {} self._inplace_del_meta(meta_dict, kv_pair) doc_meta[doc.doc_id] = meta_dict self._manager.set_docs_new_meta(doc_meta) return BaseResponse(data=None) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   class  UpdateMetadataRequest(BaseModel): doc_ids: List[str] kv_pair: Dict[str, Union[bool, int, float, str, list]]   @app.post("/update_or_create_metadata_keys") def  update_or_create_metadata_keys(self, update_metadata_request: UpdateMetadataRequest): doc_ids = update_metadata_request.doc_ids kv_pair = update_metadata_request.kv_pair try: docs = self._manager.get_docs(doc_ids) if not docs: return BaseResponse(code=400, msg="Failed, no doc found") for doc in docs: doc_meta = {} meta_dict = json.loads(doc.meta) if doc.meta else {} for k, v in kv_pair.items(): meta_dict[k] = v doc_meta[doc.doc_id] = meta_dict self._manager.set_docs_new_meta(doc_meta) return BaseResponse(data=None) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   class  ResetMetadataRequest(BaseModel): doc_ids: List[str] new_meta: Dict[str, Union[bool, int, float, str, list]]   @app.post("/reset_metadata") def  reset_metadata(self, reset_metadata_request: ResetMetadataRequest): doc_ids = reset_metadata_request.doc_ids new_meta = reset_metadata_request.new_meta try: docs = self._manager.get_docs(doc_ids) if not docs: return BaseResponse(code=400, msg="Failed, no doc found") self._manager.set_docs_new_meta({doc.doc_id: new_meta for doc in docs}) return BaseResponse(data=None) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   class  QueryMetadataRequest(BaseModel): doc_id: str key: Optional[str] = None   @app.post("/query_metadata") def  query_metadata(self, query_metadata_request: QueryMetadataRequest): doc_id = query_metadata_request.doc_id key = query_metadata_request.key try: docs = self._manager.get_docs(doc_id) if not docs: return BaseResponse(data=None) doc = docs[0] meta_dict = json.loads(doc.meta) if doc.meta else {} if not key: return BaseResponse(data=meta_dict) if key not in meta_dict: return BaseResponse(code=400, msg=f"Failed, key {key} does not exist") return BaseResponse(data=meta_dict[key]) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)   def  __repr__(self): return lazyllm.make_repr("Module", "DocManager")``



 |

### `add_files_to_group(files, group_name, override=False, metadatas=None, user_path=None)`

将文件上传后直接添加到指定分组的接口。

Parameters:

*   **`files`** (`List[UploadFile]`) –

    上传的文件列表。

*   **`group_name`** (`str`) –

    要添加到的分组名称。

*   **`override`** (`bool`, default: `False` ) –

    是否覆盖已存在的文件。默认为False。

*   **`metadatas`** (`Optional[str]`, default: `None` ) –

    文件元数据，JSON格式。

*   **`user_path`** (`Optional[str]`, default: `None` ) –

    用户自定义的文件上传路径。


**Returns:**

*   BaseResponse: 操作结果和文件ID。

Source code in `lazyllm/tools/rag/doc_manager.py`

|  |

 `@app.post("/add_files_to_group") def  add_files_to_group(self, files: List[UploadFile], group_name: str, override: bool = False, metadatas: Optional[str] = None, user_path: Optional[str] = None): """ 将文件上传后直接添加到指定分组的接口。   Args:
 files (List[UploadFile]): 上传的文件列表。 group_name (str): 要添加到的分组名称。 override (bool): 是否覆盖已存在的文件。默认为False。 metadatas (Optional[str]): 文件元数据，JSON格式。 user_path (Optional[str]): 用户自定义的文件上传路径。   **Returns:**   - BaseResponse: 操作结果和文件ID。 """
 try: response = self.upload_files(files, override=override, metadatas=metadatas, user_path=user_path) if response.code != 200: return response ids = response.data[0] self._manager.add_files_to_kb_group(ids, group_name) return BaseResponse(data=ids) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)`



 |

### `add_files_to_group_by_id(request)`

通过文件ID将文件添加到指定分组的接口。

Parameters:

*   **`request`** (`FileGroupRequest`) –

    包含文件ID和分组名称的请求。


**Returns:**

*   BaseResponse: 操作结果。

Source code in `lazyllm/tools/rag/doc_manager.py`

|  |

 `@app.post("/add_files_to_group_by_id") def  add_files_to_group_by_id(self, request: FileGroupRequest): """ 通过文件ID将文件添加到指定分组的接口。   Args:
 request (FileGroupRequest): 包含文件ID和分组名称的请求。   **Returns:**   - BaseResponse: 操作结果。 """
 try: self._manager.add_files_to_kb_group(request.file_ids, request.group_name) return BaseResponse() except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)`



 |

### `delete_files(request)`

删除指定文件的接口。

Parameters:

*   **`request`** (`FileGroupRequest`) –

    包含文件ID和分组名称的请求。


**Returns:**

*   BaseResponse: 删除操作结果。

Source code in `lazyllm/tools/rag/doc_manager.py`

|  |

 `@app.post("/delete_files") def  delete_files(self, request: FileGroupRequest): """ 删除指定文件的接口。   Args:
 request (FileGroupRequest): 包含文件ID和分组名称的请求。   **Returns:**   - BaseResponse: 删除操作结果。 """
 try: if request.group_name: return self.delete_files_from_group(request) else: documents = self._manager.delete_files(request.file_ids) deleted_ids = set([ele.doc_id for ele in documents]) for doc in documents: if os.path.exists(path := doc.path): os.remove(path) results = ["Success" if ele.doc_id in deleted_ids else "Failed" for ele in documents] return BaseResponse(data=[request.file_ids, results]) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)`



 |

### `document()`

提供默认文档页面的重定向接口。

**Returns:**

*   RedirectResponse: 重定向到 `/docs` 页面。

Source code in `lazyllm/tools/rag/doc_manager.py`

|  |

 ``@app.get("/", response_model=BaseResponse, summary="docs") def  document(self): """ 提供默认文档页面的重定向接口。   **Returns:**   - RedirectResponse: 重定向到 `/docs` 页面。 """
 return RedirectResponse(url="/docs")``



 |

### `list_files(limit=None, details=True, alive=None)`

列出已上传文件的接口。

Parameters:

*   **`limit`** (`Optional[int]`, default: `None` ) –

    返回的文件数量限制。默认为None。

*   **`details`** (`bool`, default: `True` ) –

    是否返回详细信息。默认为True。

*   **`alive`** (`Optional[bool]`, default: `None` ) –

    如果为True，只返回未删除的文件。默认为None。


**Returns:**

*   BaseResponse: 文件列表数据。

Source code in `lazyllm/tools/rag/doc_manager.py`

|  |

 `@app.get("/list_files") def  list_files(self, limit: Optional[int] = None, details: bool = True, alive: Optional[bool] = None): """ 列出已上传文件的接口。   Args:
 limit (Optional[int]): 返回的文件数量限制。默认为None。 details (bool): 是否返回详细信息。默认为True。 alive (Optional[bool]): 如果为True，只返回未删除的文件。默认为None。   **Returns:**   - BaseResponse: 文件列表数据。 """
 try: status = [DocListManager.Status.success, DocListManager.Status.waiting, DocListManager.Status.working, DocListManager.Status.failed] if alive else DocListManager.Status.all return BaseResponse(data=self._manager.list_files(limit=limit, details=details, status=status)) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)`



 |

### `list_files_in_group(group_name=None, limit=None, alive=None)`

列出指定分组中文件的接口。

Parameters:

*   **`group_name`** (`Optional[str]`, default: `None` ) –

    文件分组名称。

*   **`limit`** (`Optional[int]`, default: `None` ) –

    返回的文件数量限制。默认为None。

*   **`alive`** (`Optional[bool]`, default: `None` ) –

    是否只返回未删除的文件。


**Returns:**

*   BaseResponse: 分组文件列表。

Source code in `lazyllm/tools/rag/doc_manager.py`

|  |

 `@app.get("/list_files_in_group") def  list_files_in_group(self, group_name: Optional[str] = None, limit: Optional[int] = None, alive: Optional[bool] = None): """ 列出指定分组中文件的接口。   Args:
 group_name (Optional[str]): 文件分组名称。 limit (Optional[int]): 返回的文件数量限制。默认为None。 alive (Optional[bool]): 是否只返回未删除的文件。   **Returns:**   - BaseResponse: 分组文件列表。 """
 try: status = [DocListManager.Status.success, DocListManager.Status.waiting, DocListManager.Status.working, DocListManager.Status.failed] if alive else DocListManager.Status.all return BaseResponse(data=self._manager.list_kb_group_files(group_name, limit, details=True, status=status)) except Exception as e: return BaseResponse(code=500, msg=str(e) + '\ntraceback:\n' + str(traceback.format_exc()), data=None)`



 |

### `list_kb_groups()`

列出所有文档分组的接口。

**Returns:**

*   BaseResponse: 包含所有文档分组的数据。

Source code in `lazyllm/tools/rag/doc_manager.py`

|  |

 `@app.get("/list_kb_groups") def  list_kb_groups(self): """ 列出所有文档分组的接口。   **Returns:**   - BaseResponse: 包含所有文档分组的数据。 """
 try: return BaseResponse(data=self._manager.list_all_kb_group()) except Exception as e: return BaseResponse(code=500, msg=str(e), data=None)`



 |

### `upload_files(files, override=False, metadatas=None, user_path=None)`

上传文件并更新其状态的接口。可以同时上传多个文件。

Parameters:

*   **`files`** (`List[UploadFile]`) –

    上传的文件列表。

*   **`override`** (`bool`, default: `False` ) –

    是否覆盖已存在的文件。默认为False。

*   **`metadatas`** (`Optional[str]`, default: `None` ) –

    文件的元数据，JSON格式。

*   **`user_path`** (`Optional[str]`, default: `None` ) –

    用户自定义的文件上传路径。


**Returns:**

*   BaseResponse: 上传结果和文件ID。

Source code in `lazyllm/tools/rag/doc_manager.py`

|  |

 `@app.post("/upload_files") def  upload_files(self, files: List[UploadFile], override: bool = False,  # noqa C901 metadatas: Optional[str] = None, user_path: Optional[str] = None): """ 上传文件并更新其状态的接口。可以同时上传多个文件。   Args:
 files (List[UploadFile]): 上传的文件列表。 override (bool): 是否覆盖已存在的文件。默认为False。 metadatas (Optional[str]): 文件的元数据，JSON格式。 user_path (Optional[str]): 用户自定义的文件上传路径。   **Returns:**   - BaseResponse: 上传结果和文件ID。 """
 try: if user_path: user_path = user_path.lstrip('/') if metadatas: metadatas: Optional[List[Dict[str, str]]] = json.loads(metadatas) if len(files) != len(metadatas): return BaseResponse(code=400, msg='Length of files and metadatas should be the same', data=None) for idx, mt in enumerate(metadatas): err_msg = self._validate_metadata(mt) if err_msg: return BaseResponse(code=400, msg=f'file [{files[idx].filename}]: {err_msg}', data=None) file_paths = [os.path.join(self._manager._path, user_path or '', file.filename) for file in files] paths_is_new = [True] * len(file_paths) if override is True: is_success, msg, paths_is_new = self._manager.validate_paths(file_paths) if not is_success: return BaseResponse(code=500, msg=msg, data=None) directorys = set(os.path.dirname(path) for path in file_paths) [os.makedirs(directory, exist_ok=True) for directory in directorys if directory] ids, results = [], [] for i in range(len(files)): file_path = file_paths[i] content = files[i].file.read() metadata = metadatas[i] if metadatas else None if override is False: file_path = self._gen_unique_filepath(file_path) with open(file_path, 'wb') as f: f.write(content) msg = "success" doc_id = gen_docid(file_path) if paths_is_new[i]: docs = self._manager.add_files( [file_path], metadatas=[metadata], status=DocListManager.Status.success) if not docs: msg = f"Failed: path {file_path} already exists in Database." else: self._manager.update_kb_group(cond_file_ids=[doc_id], new_need_reparse=True) msg = f"Success: path {file_path} will be reparsed." ids.append(doc_id) results.append(msg) return BaseResponse(data=[ids, results]) except Exception as e: lazyllm.LOG.error(f'upload_files exception: {e}') return BaseResponse(code=500, msg=str(e), data=None)`



 |

Bases: `NodeTransform`

将句子拆分成指定大小的块。可以指定相邻块之间重合部分的大小。

Parameters:

*   **`chunk_size`** (`int`, default: `1024` ) –

    拆分之后的块大小

*   **`chunk_overlap`** (`int`, default: `200` ) –

    相邻两个块之间重合的内容长度


Examples:

`>>> import lazyllm
>>> from lazyllm.tools import Document, SentenceSplitter
>>> m = lazyllm.OnlineEmbeddingModule(source="glm")
>>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False)
>>> documents.create_node_group(name="sentences", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100)`

Source code in `lazyllm/tools/rag/transform.py`

|  |

``class  SentenceSplitter(NodeTransform):
 """ 将句子拆分成指定大小的块。可以指定相邻块之间重合部分的大小。   Args:
 chunk_size (int): 拆分之后的块大小 chunk_overlap (int): 相邻两个块之间重合的内容长度     Examples:   >>> import lazyllm >>> from lazyllm.tools import Document, SentenceSplitter >>> m = lazyllm.OnlineEmbeddingModule(source="glm") >>> documents = Document(dataset_path='your_doc_path', embed=m, manager=False) >>> documents.create_node_group(name="sentences", transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100) """ def  __init__(self, chunk_size: int = 1024, chunk_overlap: int = 200, num_workers: int = 0): super(__class__, self).__init__(num_workers=num_workers) if chunk_overlap > chunk_size: raise ValueError( f'Got a larger chunk overlap ({chunk_overlap}) than chunk size ' f'({chunk_size}), should be smaller.' )   assert ( chunk_size > 0 and chunk_overlap >= 0 ), 'chunk size should > 0 and chunk_overlap should >= 0'   try: if 'TIKTOKEN_CACHE_DIR' not in os.environ and 'DATA_GYM_CACHE_DIR' not in os.environ: path = os.path.join(config['model_path'], 'tiktoken') os.makedirs(path, exist_ok=True) os.environ['TIKTOKEN_CACHE_DIR'] = path self._tiktoken_tokenizer = tiktoken.encoding_for_model('gpt-3.5-turbo') os.environ.pop('TIKTOKEN_CACHE_DIR') except requests.exceptions.ConnectionError: LOG.error( 'Unable to download the vocabulary file for tiktoken `gpt-3.5-turbo`. ' 'Please check your internet connection. ' 'Alternatively, you can manually download the file ' 'and set the `TIKTOKEN_CACHE_DIR` environment variable.' ) raise except Exception as e: LOG.error(f'Unable to build tiktoken tokenizer with error `{e}`') raise self._punkt_st_tokenizer = nltk.tokenize.PunktSentenceTokenizer()   self._sentence_split_fns = [ partial(split_text_keep_separator, separator='\n\n\n'),  # paragraph self._punkt_st_tokenizer.tokenize, ]   self._sub_sentence_split_fns = [ lambda t: re.findall(r'[^,.;。？！]+[,.;。？！]?', t), partial(split_text_keep_separator, separator=' '), list,  # split by character ]   self.chunk_size = chunk_size self.chunk_overlap = chunk_overlap   def  transform(self, node: DocNode, **kwargs) -> List[str]: return self.split_text( node.get_text(), metadata_size=self._get_metadata_size(node), )   def  _get_metadata_size(self, node: DocNode) -> int: # Return the bigger size to ensure chunk_size < limit return max( self._token_size(node.get_metadata_str(mode=MetadataMode.EMBED)), self._token_size(node.get_metadata_str(mode=MetadataMode.LLM)), )   def  split_text(self, text: str, metadata_size: int) -> List[str]: if text == '': return [''] effective_chunk_size = self.chunk_size - metadata_size if effective_chunk_size <= 0: raise ValueError( f'Metadata length ({metadata_size}) is longer than chunk size ' f'({self.chunk_size}). Consider increasing the chunk size or ' 'decreasing the size of your metadata to avoid this.' ) elif effective_chunk_size < 50: LOG.warning( f'Metadata length ({metadata_size}) is close to chunk size ' f'({self.chunk_size}). Resulting chunks are less than 50 tokens. ' 'Consider increasing the chunk size or decreasing the size of ' 'your metadata to avoid this.' )   splits = self._split(text, effective_chunk_size) chunks = self._merge(splits, effective_chunk_size) return chunks   def  _split(self, text: str, chunk_size: int) -> List[_Split]: """Break text into splits that are smaller than chunk size.   The order of splitting is: 1. split by paragraph separator 2. split by chunking tokenizer 3. split by second chunking regex 4. split by default separator (' ') 5. split by character """ token_size = self._token_size(text) if token_size <= chunk_size: return [_Split(text, is_sentence=True, token_size=token_size)]   text_splits_by_fns, is_sentence = self._get_splits_by_fns(text)   text_splits = [] for text in text_splits_by_fns: token_size = self._token_size(text) if token_size <= chunk_size: text_splits.append( _Split( text, is_sentence=is_sentence, token_size=token_size, ) ) else: recursive_text_splits = self._split(text, chunk_size=chunk_size) text_splits.extend(recursive_text_splits) return text_splits   def  _merge(self, splits: List[_Split], chunk_size: int) -> List[str]: chunks: List[str] = [] cur_chunk: List[Tuple[str, int]] = []  # list of (text, length) cur_chunk_len = 0 is_chunk_new = True   def  close_chunk() -> None: nonlocal cur_chunk, cur_chunk_len, is_chunk_new   chunks.append(''.join([text for text, _ in cur_chunk])) last_chunk = cur_chunk cur_chunk = [] cur_chunk_len = 0 is_chunk_new = True   # Add overlap to the next chunk using the last one first overlap_len = 0 for text, length in reversed(last_chunk): if overlap_len + length > self.chunk_overlap: break cur_chunk.append((text, length)) overlap_len += length cur_chunk_len += length cur_chunk.reverse()   i = 0 while i < len(splits): cur_split = splits[i] if cur_split.token_size > chunk_size: raise ValueError('Single token exceeded chunk size') if cur_chunk_len + cur_split.token_size > chunk_size and not is_chunk_new: # if adding split to current chunk exceeds chunk size close_chunk() else: if ( cur_split.is_sentence or cur_chunk_len + cur_split.token_size <= chunk_size or is_chunk_new  # new chunk, always add at least one split ): # add split to chunk cur_chunk_len += cur_split.token_size cur_chunk.append((cur_split.text, cur_split.token_size)) i += 1 is_chunk_new = False else: close_chunk()   # handle the last chunk if not is_chunk_new: chunks.append(''.join([text for text, _ in cur_chunk]))   # Remove whitespace only chunks and remove leading and trailing whitespace. return [stripped_chunk for chunk in chunks if (stripped_chunk := chunk.strip())]   def  _token_size(self, text: str) -> int: return len(self._tiktoken_tokenizer.encode(text, allowed_special='all'))   def  _get_splits_by_fns(self, text: str) -> Tuple[List[str], bool]: for split_fn in self._sentence_split_fns: splits = split_fn(text) if len(splits) > 1: return splits, True   for split_fn in self._sub_sentence_split_fns: splits = split_fn(text) if len(splits) > 1: break   return splits, False``



 |

Bases: `NodeTransform`

一个文本摘要和关键词提取器，负责分析用户输入的文本，并根据请求任务提供简洁的摘要或提取相关关键词。

Parameters:

*   **`llm`** (`[TrainableModule](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.TrainableModule "            lazyllm.module.TrainableModule (lazyllm.TrainableModule)")`) –

    可训练的模块

*   **`language`** (`str`) –

    语言种类，目前只支持中文（zh）和英文（en）

*   **`task_type`** (`str`) –

    目前支持两种任务：摘要（summary）和关键词抽取（keywords）。


Examples:

`>>> from lazyllm import TrainableModule
>>> from lazyllm.tools.rag import LLMParser
>>> llm = TrainableModule("internlm2-chat-7b")
>>> summary_parser = LLMParser(llm, language="en", task_type="summary")`

Source code in `lazyllm/tools/rag/transform.py`

|  |

`class  LLMParser(NodeTransform):
 """ 一个文本摘要和关键词提取器，负责分析用户输入的文本，并根据请求任务提供简洁的摘要或提取相关关键词。   Args:
 llm (TrainableModule): 可训练的模块 language (str): 语言种类，目前只支持中文（zh）和英文（en） task_type (str): 目前支持两种任务：摘要（summary）和关键词抽取（keywords）。     Examples:   >>> from lazyllm import TrainableModule >>> from lazyllm.tools.rag import LLMParser >>> llm = TrainableModule("internlm2-chat-7b") >>> summary_parser = LLMParser(llm, language="en", task_type="summary") """ def  __init__(self, llm: TrainableModule, language: str, task_type: str, num_workers: int = 30): super(__class__, self).__init__(num_workers=num_workers) assert language in ['en', 'zh'], f'Not supported language {language}' assert task_type in ['summary', 'keywords', 'qa', 'qa_img'], f'Not supported task_type {task_type}' self._task_type = task_type if self._task_type == 'qa_img': prompt = dict(system=templates[language][task_type], user='{input}') else: prompt = dict(system=templates[language][task_type], user='#input:\n{input}\n#output:\n') self._llm = llm.share(prompt=AlpacaPrompter(prompt), stream=False, format=self._format) self._task_type = task_type   def  transform(self, node: DocNode, **kwargs) -> List[str]: """ 在指定的文档上执行设定的任务。   Args:
 node (DocNode): 需要执行抽取任务的文档。     Examples:   >>> import lazyllm >>> from lazyllm.tools import LLMParser >>> llm = lazyllm.TrainableModule("internlm2-chat-7b").start() >>> m = lazyllm.TrainableModule("bge-large-zh-v1.5").start() >>> summary_parser = LLMParser(llm, language="en", task_type="summary") >>> keywords_parser = LLMParser(llm, language="en", task_type="keywords") >>> documents = lazyllm.Document(dataset_path="/path/to/your/data", embed=m, manager=False) >>> rm = lazyllm.Retriever(documents, group_name='CoarseChunk', similarity='bm25', topk=6) >>> doc_nodes = rm("test") >>> summary_result = summary_parser.transform(doc_nodes[0]) >>> keywords_result = keywords_parser.transform(doc_nodes[0]) """ if self._task_type == 'qa_img': inputs = encode_query_with_filepaths('Extract QA pairs from images.', [node.image_path]) else: inputs = node.get_text() result = self._llm(inputs) return [result] if isinstance(result, str) else result   def  _format(self, input): if self._task_type == 'keywords': return [s.strip() for s in input.split(',')] elif self._task_type in ('qa', 'qa_img'): return [QADocNode(query=q.strip()[3:].strip(), answer=a.strip()[3:].strip()) for q, a in zip( list(filter(None, map(str.strip, input.split("\n"))))[::2], list(filter(None, map(str.strip, input.split("\n"))))[1::2])] return input`



 |

### `transform(node, **kwargs)`

在指定的文档上执行设定的任务。

Parameters:

*   **`node`** (`DocNode`) –

    需要执行抽取任务的文档。


Examples:

`>>> import lazyllm
>>> from lazyllm.tools import LLMParser
>>> llm = lazyllm.TrainableModule("internlm2-chat-7b").start()
>>> m = lazyllm.TrainableModule("bge-large-zh-v1.5").start()
>>> summary_parser = LLMParser(llm, language="en", task_type="summary")
>>> keywords_parser = LLMParser(llm, language="en", task_type="keywords")
>>> documents = lazyllm.Document(dataset_path="/path/to/your/data", embed=m, manager=False)
>>> rm = lazyllm.Retriever(documents, group_name='CoarseChunk', similarity='bm25', topk=6)
>>> doc_nodes = rm("test")
>>> summary_result = summary_parser.transform(doc_nodes[0])
>>> keywords_result = keywords_parser.transform(doc_nodes[0])`

Source code in `lazyllm/tools/rag/transform.py`

|  |

 `def  transform(self, node: DocNode, **kwargs) -> List[str]: """ 在指定的文档上执行设定的任务。   Args:
 node (DocNode): 需要执行抽取任务的文档。     Examples:   >>> import lazyllm >>> from lazyllm.tools import LLMParser >>> llm = lazyllm.TrainableModule("internlm2-chat-7b").start() >>> m = lazyllm.TrainableModule("bge-large-zh-v1.5").start() >>> summary_parser = LLMParser(llm, language="en", task_type="summary") >>> keywords_parser = LLMParser(llm, language="en", task_type="keywords") >>> documents = lazyllm.Document(dataset_path="/path/to/your/data", embed=m, manager=False) >>> rm = lazyllm.Retriever(documents, group_name='CoarseChunk', similarity='bm25', topk=6) >>> doc_nodes = rm("test") >>> summary_result = summary_parser.transform(doc_nodes[0]) >>> keywords_result = keywords_parser.transform(doc_nodes[0]) """ if self._task_type == 'qa_img': inputs = encode_query_with_filepaths('Extract QA pairs from images.', [node.image_path]) else: inputs = node.get_text() result = self._llm(inputs) return [result] if isinstance(result, str) else result`



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase (lazyllm.module.module.ModuleBase)")`

WebModule是LazyLLM为开发者提供的基于Web的交互界面。在初始化并启动一个WebModule之后，开发者可以从页面上看到WebModule背后的模块结构，并将Chatbot组件的输入传输给自己开发的模块进行处理。 模块返回的结果和日志会直接显示在网页的“处理日志”和Chatbot组件上。除此之外，WebModule支持在网页上动态加入Checkbox或Text组件用于向模块发送额外的参数。 WebModule页面还提供“使用上下文”，“流式输出”和“追加输出”的Checkbox，可以用来改变页面和后台模块的交互方式。

 **`WebModule.init_web(component_descs) -> gradio.Blocks`** 使用gradio库生成演示web页面，初始化session相关数据以便在不同的页面保存各自的对话和日志，然后使用传入的component\_descs参数为页面动态添加Checkbox和Text组件，最后设置页面上的按钮和文本框的相应函数 之后返回整个页面。WebModule的\_\_init\_\_函数调用此方法生成页面。

Parameters:

*   **`component_descs`** (`list`) –

    用于动态向页面添加组件的列表。列表中的每个元素也是一个列表，其中包含5个元素，分别是组件对应的模块ID，模块名，组件名，组件类型（目前仅支持Checkbox和Text），组件默认值。


Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> def  func2(in_str, do_sample=True, temperature=0.0, *args, **kwargs): [](#__codelineno-0-3)...     return f"func2:{in_str}|do_sample:{str(do_sample)}|temp:{temperature}" [](#__codelineno-0-4)... [](#__codelineno-0-5)>>> m1=lazyllm.ActionModule(func2) [](#__codelineno-0-6)>>> m1.name="Module1" [](#__codelineno-0-7)>>> w = lazyllm.WebModule(m1, port=[20570, 20571, 20572], components={ [](#__codelineno-0-8)...         m1:[('do_sample', 'Checkbox', True), ('temperature', 'Text', 0.1)]}, [](#__codelineno-0-9)...                       text_mode=lazyllm.tools.WebModule.Mode.Refresh) [](#__codelineno-0-10)>>> w.start() [](#__codelineno-0-11)193703: 2024-06-07 10:26:00 lazyllm SUCCESS: ...`

Source code in `lazyllm/tools/webpages/webmodule.py`

|  |

``class  WebModule(ModuleBase):
 """WebModule是LazyLLM为开发者提供的基于Web的交互界面。在初始化并启动一个WebModule之后，开发者可以从页面上看到WebModule背后的模块结构，并将Chatbot组件的输入传输给自己开发的模块进行处理。 模块返回的结果和日志会直接显示在网页的“处理日志”和Chatbot组件上。除此之外，WebModule支持在网页上动态加入Checkbox或Text组件用于向模块发送额外的参数。 WebModule页面还提供“使用上下文”，“流式输出”和“追加输出”的Checkbox，可以用来改变页面和后台模块的交互方式。   <span style="font-size: 20px;">&ensp;**`WebModule.init_web(component_descs) -> gradio.Blocks`**</span> 使用gradio库生成演示web页面，初始化session相关数据以便在不同的页面保存各自的对话和日志，然后使用传入的component_descs参数为页面动态添加Checkbox和Text组件，最后设置页面上的按钮和文本框的相应函数 之后返回整个页面。WebModule的__init__函数调用此方法生成页面。   Args:
 component_descs (list): 用于动态向页面添加组件的列表。列表中的每个元素也是一个列表，其中包含5个元素，分别是组件对应的模块ID，模块名，组件名，组件类型（目前仅支持Checkbox和Text），组件默认值。     Examples:
 >>> import lazyllm >>> def func2(in_str, do_sample=True, temperature=0.0, *args, **kwargs): ...     return f"func2:{in_str}|do_sample:{str(do_sample)}|temp:{temperature}" ... >>> m1=lazyllm.ActionModule(func2) >>> m1.name="Module1" >>> w = lazyllm.WebModule(m1, port=[20570, 20571, 20572], components={ ...         m1:[('do_sample', 'Checkbox', True), ('temperature', 'Text', 0.1)]}, ...                       text_mode=lazyllm.tools.WebModule.Mode.Refresh) >>> w.start() 193703: 2024-06-07 10:26:00 lazyllm SUCCESS: ... """ class  Mode: Dynamic = 0 Refresh = 1 Appendix = 2   def  __init__(self, m: Any, *, components: Dict[Any, Any] = dict(), title: str = '对话演示终端', port: Optional[Union[int, range, tuple, list]] = None, history: List[Any] = [], text_mode: Optional[Mode] = None, trace_mode: Optional[Mode] = None, audio: bool = False, stream: bool = False, files_target: Optional[Union[Any, List[Any]]] = None, static_paths: Optional[Union[str, Path, List[Union[str, Path]]]] = None, encode_files: bool = False, share: bool = False) -> None: super().__init__() # Set the static directory of gradio so that gradio can access local resources in the directory if isinstance(static_paths, (str, Path)): self._static_paths = [static_paths] elif isinstance(static_paths, list) and all(isinstance(p, (str, Path)) for p in static_paths): self._static_paths = static_paths elif static_paths is None: self._static_paths = [] else: raise ValueError(f"static_paths only supported str, path or list types. Not supported {static_paths}") self.m = lazyllm.ActionModule(m) if isinstance(m, lazyllm.FlowBase) else m self.pool = lazyllm.ThreadPoolExecutor(max_workers=50) self.title = title self.port = port or range(20500, 20799) components = sum([[([k._module_id, k._module_name] + list(v)) for v in vs] for k, vs in components.items()], []) self.ckeys = [[c[0], c[2]] for c in components] if isinstance(m, (OnlineChatModule, TrainableModule)) and not history: history = [m] self.history = [h._module_id for h in history] if trace_mode: LOG.warn('trace_mode is deprecated') self.text_mode = text_mode if text_mode else WebModule.Mode.Dynamic self.cach_path = self._set_up_caching() self.audio = audio self.stream = stream self.files_target = files_target if isinstance(files_target, list) or files_target is None else [files_target] self.encode_files = encode_files self.share = share self.demo = self.init_web(components) self.url = None signal.signal(signal.SIGINT, self._signal_handler) signal.signal(signal.SIGTERM, self._signal_handler)   def  _get_all_file_submodule(self): if self.files_target: return self.files_target = [] self.for_each( lambda x: getattr(x, 'template_message', None), lambda x: self.files_target.append(x) )   def  _signal_handler(self, signum, frame): LOG.info(f"Signal {signum} received, terminating subprocess.") atexit._run_exitfuncs() sys.exit(0)   def  _set_up_caching(self): if 'GRADIO_TEMP_DIR' in os.environ: cach_path = os.environ['GRADIO_TEMP_DIR'] else: cach_path = os.path.join(lazyllm.config['temp_dir'], 'gradio_cach') os.environ['GRADIO_TEMP_DIR'] = cach_path if not os.path.exists(cach_path): os.makedirs(cach_path) return cach_path   def  init_web(self, component_descs): gr.set_static_paths(self._static_paths) with gr.Blocks(css=css, title=self.title, analytics_enabled=False) as demo: sess_data = gr.State(value={ 'sess_titles': [''], 'sess_logs': {}, 'sess_history': {}, 'sess_num': 1, 'curr_sess': '', 'frozen_query': '', }) with gr.Row(): with gr.Column(scale=3): with gr.Row(): with lazyllm.config.temp('repr_show_child', True): gr.Textbox(elem_id='module', interactive=False, show_label=True, label="模型结构", value=repr(self.m)) with gr.Row(): chat_use_context = gr.Checkbox(interactive=True, value=False, label="使用上下文") with gr.Row(): stream_output = gr.Checkbox(interactive=self.stream, value=self.stream, label="流式输出") text_mode = gr.Checkbox(interactive=(self.text_mode == WebModule.Mode.Dynamic), value=(self.text_mode != WebModule.Mode.Refresh), label="追加输出") components = [] for _, gname, name, ctype, value in component_descs: if ctype in ('Checkbox', 'Text'): components.append(getattr(gr, ctype)(interactive=True, value=value, label=f'{gname}.{name}')) elif ctype == 'Dropdown': components.append(getattr(gr, ctype)(interactive=True, choices=value, label=f'{gname}.{name}')) else: raise KeyError(f'invalid component type: {ctype}') with gr.Row(): dbg_msg = gr.Textbox(show_label=True, label='处理日志', elem_id='logging', interactive=False, max_lines=10) clear_btn = gr.Button(value="🗑️  Clear history", interactive=True) with gr.Column(scale=6): with gr.Row(): add_sess_btn = gr.Button("添加新会话") sess_drpdn = gr.Dropdown(choices=sess_data.value['sess_titles'], label="选择会话：", value='') del_sess_btn = gr.Button("删除当前会话") chatbot = gr.Chatbot(height=700) query_box = gr.MultimodalTextbox(show_label=False, placeholder='输入内容并回车!!!', interactive=True) recordor = gr.Audio(sources=["microphone"], type="filepath", visible=self.audio)   query_box.submit(self._init_session, [query_box, sess_data, recordor], [sess_drpdn, chatbot, dbg_msg, sess_data, recordor], queue=True ).then(lambda: gr.update(interactive=False), None, query_box, queue=False ).then(lambda: gr.update(interactive=False), None, add_sess_btn, queue=False ).then(lambda: gr.update(interactive=False), None, sess_drpdn, queue=False ).then(lambda: gr.update(interactive=False), None, del_sess_btn, queue=False ).then(self._prepare, [query_box, chatbot, sess_data], [query_box, chatbot], queue=True ).then(self._respond_stream, [chat_use_context, chatbot, stream_output, text_mode] + components, [chatbot, dbg_msg], queue=chatbot ).then(lambda: gr.update(interactive=True), None, query_box, queue=False ).then(lambda: gr.update(interactive=True), None, add_sess_btn, queue=False ).then(lambda: gr.update(interactive=True), None, sess_drpdn, queue=False ).then(lambda: gr.update(interactive=True), None, del_sess_btn, queue=False) clear_btn.click(self._clear_history, [sess_data], outputs=[chatbot, query_box, dbg_msg, sess_data])   sess_drpdn.change(self._change_session, [sess_drpdn, chatbot, dbg_msg, sess_data], [sess_drpdn, chatbot, query_box, dbg_msg, sess_data]) add_sess_btn.click(self._add_session, [chatbot, dbg_msg, sess_data], [sess_drpdn, chatbot, query_box, dbg_msg, sess_data]) del_sess_btn.click(self._delete_session, [sess_drpdn, sess_data], [sess_drpdn, chatbot, query_box, dbg_msg, sess_data]) recordor.change(self._sub_audio, recordor, query_box) return demo   def  _sub_audio(self, audio): if audio: return {'text': '', 'files': [audio]} else: return {}   def  _init_session(self, query, session, audio): audio = None session['frozen_query'] = query if session['curr_sess'] != '':  # remain unchanged. return gr.Dropdown(), gr.Chatbot(), gr.Textbox(), session, audio   if "text" in query and query["text"] is not None: id_name = query['text'] else: id_name = id(id_name) session['curr_sess'] = f"({session['sess_num']}) {id_name}" session['sess_num'] += 1 session['sess_titles'][0] = session['curr_sess']   session['sess_logs'][session['curr_sess']] = [] session['sess_history'][session['curr_sess']] = [] return gr.update(choices=session['sess_titles'], value=session['curr_sess']), [], '', session, audio   def  _add_session(self, chat_history, log_history, session): if session['curr_sess'] == '': LOG.warning('Cannot create new session while current session is empty.') return gr.Dropdown(), gr.Chatbot(), {}, gr.Textbox(), session   self._save_history(chat_history, log_history, session)   session['curr_sess'] = '' session['sess_titles'].insert(0, session['curr_sess']) return gr.update(choices=session['sess_titles'], value=session['curr_sess']), [], {}, '', session   def  _save_history(self, chat_history, log_history, session): if session['curr_sess'] in session['sess_titles']: session['sess_history'][session['curr_sess']] = chat_history session['sess_logs'][session['curr_sess']] = log_history   def  _change_session(self, session_title, chat_history, log_history, session): if session['curr_sess'] == '':  # new session return gr.Dropdown(), [], {}, '', session   if session_title not in session['sess_titles']: LOG.warning(f'{session_title} is not an existing session title.') return gr.Dropdown(), gr.Chatbot(), {}, gr.Textbox(), session   self._save_history(chat_history, log_history, session)   session['curr_sess'] = session_title return (gr.update(choices=session['sess_titles'], value=session['curr_sess']), session['sess_history'][session['curr_sess']], {}, session['sess_logs'][session['curr_sess']], session)   def  _delete_session(self, session_title, session): if session_title not in session['sess_titles']: LOG.warning(f'session {session_title} does not exist.') return gr.Dropdown(), session session['sess_titles'].remove(session_title)   if session_title != '': del session['sess_history'][session_title] del session['sess_logs'][session_title] session['curr_sess'] = session_title else: session['curr_sess'] = 'dummy session' # add_session and change_session cannot accept an uninitialized session. # Here we need to imitate removal of a real session so that # add_session and change_session could skip saving chat history.   if len(session['sess_titles']) == 0: return self._add_session(None, None, session) else: return self._change_session(session['sess_titles'][0], None, {}, session)   def  _prepare(self, query, chat_history, session): if not query.get('text', '') and not query.get('files', []): query = session['frozen_query'] if chat_history is None: chat_history = [] for x in query["files"]: chat_history.append([[x,], None]) if "text" in query and query["text"]: chat_history.append([query['text'], None]) return {}, chat_history   def  _respond_stream(self, use_context, chat_history, stream_output, append_text, *args):  # noqa C901 try: # TODO: move context to trainable module files = [] chat_history[-1][1], log_history = '', [] for file in chat_history[::-1]: if file[-1]: break  # not current chat if isinstance(file[0], (tuple, list)): files.append(file[0][0]) elif isinstance(file[0], str) and file[0].startswith('lazyllm_img::'):  # Just for pytest files.append(file[0][13:]) if isinstance(chat_history[-1][0], str): string = chat_history[-1][0] else: string = '' if self.files_target is None and not self.encode_files: self._get_all_file_submodule() if self.encode_files and files: string = encode_query_with_filepaths(string, files) if files and self.files_target: for module in self.files_target: assert isinstance(module, ModuleBase) if module._module_id in globals['lazyllm_files']: globals['lazyllm_files'][module._module_id].extend(files) else: globals['lazyllm_files'][module._module_id] = files string += f' ## Get attachments: {os.path.basename(files[-1])}' elif self.files_target: for module in self.files_target: assert isinstance(module, ModuleBase) globals['lazyllm_files'][module._module_id] = [] input = string history = chat_history[:-1] if use_context and len(chat_history) > 1 else list()   for k, v in zip(self.ckeys, args): if k[0] not in globals['global_parameters']: globals['global_parameters'][k[0]] = dict() globals['global_parameters'][k[0]][k[1]] = v   if use_context: for h in self.history: if h not in globals['chat_history']: globals['chat_history'][h] = list() globals['chat_history'][h] = history   if FileSystemQueue().size() > 0: FileSystemQueue().clear() kw = dict(stream_output=stream_output) if isinstance(self.m, (TrainableModule, OnlineChatModule)) else {} func_future = self.pool.submit(self.m, input, **kw) while True: if value := FileSystemQueue().dequeue(): chat_history[-1][1] += ''.join(value) if append_text else ''.join(value) if stream_output: yield chat_history, '' elif value := FileSystemQueue.get_instance('lazy_error').dequeue(): log_history.append(''.join(value)) elif value := FileSystemQueue.get_instance('lazy_trace').dequeue(): log_history.append(''.join(value)) elif func_future.done(): break time.sleep(0.01) result = func_future.result() if FileSystemQueue().size() > 0: FileSystemQueue().clear()   def  get_log_and_message(s): if isinstance(s, dict): s = s.get("message", {}).get("content", "") else: try: r = decode_query_with_filepaths(s) if isinstance(r, str): r = json.loads(r) if 'choices' in r: if "type" not in r["choices"][0] or ( "type" in r["choices"][0] and r["choices"][0]["type"] != "tool_calls"): delta = r["choices"][0]["delta"] if "content" in delta: s = delta["content"] else: s = "" elif isinstance(r, dict) and 'files' in r and 'query' in r: return r['query'], ''.join(log_history), r['files'] if len(r['files']) > 0 else None else: s = s except (ValueError, KeyError, TypeError): s = s except Exception as e: LOG.error(f"Uncaptured error `{e}` when parsing `{s}`, please contact us if you see this.") return s, "".join(log_history), None   def  contains_markdown_image(text: str): pattern = r"!\[.*?\]\((.*?)\)" return bool(re.search(pattern, text))   def  extract_img_path(text: str): pattern = r"!\[.*?\]\((.*?)\)" urls = re.findall(pattern, text) return urls   file_paths = None if isinstance(result, (str, dict)): result, log, file_paths = get_log_and_message(result) if file_paths: for i, file_path in enumerate(file_paths): suffix = os.path.splitext(file_path)[-1].lower() file = None if suffix in PIL.Image.registered_extensions().keys(): file = gr.Image(file_path) elif suffix in ('.mp3', '.wav'): file = gr.Audio(file_path) elif suffix in ('.mp4'): file = gr.Video(file_path) else: LOG.error(f'Not supported typr: {suffix}, for file: {file}') if i == 0: chat_history[-1][1] = file else: chat_history.append([None, file]) if result: chat_history.append([None, result]) else: assert isinstance(result, str), f'Result should only be str, but got {type(result)}' show_result = result if contains_markdown_image(show_result): urls = extract_img_path(show_result) for url in urls: suffix = os.path.splitext(url)[-1].lower() if suffix in PIL.Image.registered_extensions().keys() and os.path.exists(url): show_result = show_result.replace(url, "file=" + url) if result: count = (len(match.group(1)) if (match := re.search(r'(\n+)$', result)) else 0) + len(result) + 1 if not (result in chat_history[-1][1][-count:]): chat_history[-1][1] += "\n\n" + show_result elif show_result != result: chat_history[-1][1] = chat_history[-1][1].replace(result, show_result) except requests.RequestException as e: chat_history = None log = str(e) except Exception as e: chat_history = None log = f'{str(e)}\n--- traceback ---\n{traceback.format_exc()}' LOG.error(log) globals['chat_history'].clear() yield chat_history, log   def  _clear_history(self, session): session['sess_history'][session['curr_sess']] = [] session['sess_logs'][session['curr_sess']] = [] return [], {}, '', session   def  _work(self): if isinstance(self.port, (range, tuple, list)): port = self._find_can_use_network_port() else: port = self.port assert self._verify_port_access(port), f'port {port} is occupied'   self.url = f'http://127.0.0.1:{port}' self.broadcast_url = f'http://0.0.0.0:{port}'   self.demo.queue().launch(server_name="0.0.0.0", server_port=port, prevent_thread_lock=True, share=self.share) LOG.success('LazyLLM webmodule launched successfully: Running on: ' f'{self.broadcast_url}, local URL: {self.url}')   def  _update(self, *, mode=None, recursive=True): super(__class__, self)._update(mode=mode, recursive=recursive) self._work() return self   def  wait(self): self.demo.block_thread()   def  stop(self): if self.demo: self.demo.close() del self.demo self.demo, self.url = None, ''   @property def  status(self): return 'running' if self.url else 'waiting' if self.url is None else 'Cancelled'   def  __repr__(self): return lazyllm.make_repr('Module', 'Web', name=self._module_name, subs=[repr(self.m)])   def  _find_can_use_network_port(self): for port in self.port: if self._verify_port_access(port): return port raise RuntimeError( f'The ports in the range {self.port} are all occupied. ' 'Please change the port range or release the relevant ports.' )   def  _verify_port_access(self, port): with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: result = s.connect_ex(('127.0.0.1', port)) return result != 0``



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`

ToolManager是一个工具管理类，用于提供工具信息和工具调用给function call。

此管理类构造时需要传入工具名字符串列表。此处工具名可以是LazyLLM提供的，也可以是用户自定义的，如果是用户自定义的，首先需要注册进LazyLLM中才可以使用。在注册时直接使用 `fc_register` 注册器，该注册器已经建立 `tool` group，所以使用该工具管理类时，所有函数都统一注册进 `tool` 分组即可。待注册的函数需要对函数参数进行注解，并且需要对函数增加功能描述，以及参数类型和作用描述。以方便工具管理类能对函数解析传给LLM使用。

Parameters:

*   **`tools`** (`List[str]`) –

    工具名称字符串列表。


Examples:

`[](#__codelineno-0-1)>>> from  lazyllm.tools  import ToolManager, fc_register [](#__codelineno-0-2)>>> import  json [](#__codelineno-0-3)>>> from  typing  import Literal [](#__codelineno-0-4)>>> @fc_register("tool") [](#__codelineno-0-5)>>> def  get_current_weather(location: str, unit: Literal["fahrenheit", "celsius"]="fahrenheit"): [](#__codelineno-0-6)...  ''' [](#__codelineno-0-7)...     Get the current weather in a given location [](#__codelineno-0-8)... [](#__codelineno-0-9)...     Args: [](#__codelineno-0-10)...         location (str): The city and state, e.g. San Francisco, CA. [](#__codelineno-0-11)...         unit (str): The temperature unit to use. Infer this from the users location. [](#__codelineno-0-12)...     ''' [](#__codelineno-0-13)...     if 'tokyo' in location.lower(): [](#__codelineno-0-14)...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius'}) [](#__codelineno-0-15)...     elif 'san francisco' in location.lower(): [](#__codelineno-0-16)...         return json.dumps({'location': 'San Francisco', 'temperature': '72', 'unit': 'fahrenheit'}) [](#__codelineno-0-17)...     elif 'paris' in location.lower(): [](#__codelineno-0-18)...         return json.dumps({'location': 'Paris', 'temperature': '22', 'unit': 'celsius'}) [](#__codelineno-0-19)...     elif 'beijing' in location.lower(): [](#__codelineno-0-20)...         return json.dumps({'location': 'Beijing', 'temperature': '90', 'unit': 'fahrenheit'}) [](#__codelineno-0-21)...     else: [](#__codelineno-0-22)...         return json.dumps({'location': location, 'temperature': 'unknown'}) [](#__codelineno-0-23)... [](#__codelineno-0-24)>>> @fc_register("tool") [](#__codelineno-0-25)>>> def  get_n_day_weather_forecast(location: str, num_days: int, unit: Literal["celsius", "fahrenheit"]='fahrenheit'): [](#__codelineno-0-26)...  ''' [](#__codelineno-0-27)...     Get an N-day weather forecast [](#__codelineno-0-28)... [](#__codelineno-0-29)...     Args: [](#__codelineno-0-30)...         location (str): The city and state, e.g. San Francisco, CA. [](#__codelineno-0-31)...         num_days (int): The number of days to forecast. [](#__codelineno-0-32)...         unit (Literal['celsius', 'fahrenheit']): The temperature unit to use. Infer this from the users location. [](#__codelineno-0-33)...     ''' [](#__codelineno-0-34)...     if 'tokyo' in location.lower(): [](#__codelineno-0-35)...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius', "num_days": num_days}) [](#__codelineno-0-36)...     elif 'san francisco' in location.lower(): [](#__codelineno-0-37)...         return json.dumps({'location': 'San Francisco', 'temperature': '75', 'unit': 'fahrenheit', "num_days": num_days}) [](#__codelineno-0-38)...     elif 'paris' in location.lower(): [](#__codelineno-0-39)...         return json.dumps({'location': 'Paris', 'temperature': '25', 'unit': 'celsius', "num_days": num_days}) [](#__codelineno-0-40)...     elif 'beijing' in location.lower(): [](#__codelineno-0-41)...         return json.dumps({'location': 'Beijing', 'temperature': '85', 'unit': 'fahrenheit', "num_days": num_days}) [](#__codelineno-0-42)...     else: [](#__codelineno-0-43)...         return json.dumps({'location': location, 'temperature': 'unknown'}) [](#__codelineno-0-44)... [](#__codelineno-0-45)>>> tools = ["get_current_weather", "get_n_day_weather_forecast"] [](#__codelineno-0-46)>>> tm = ToolManager(tools) [](#__codelineno-0-47)>>> print(tm([{'name': 'get_n_day_weather_forecast', 'arguments': {'location': 'Beijing', 'num_days': 3}}])[0]) [](#__codelineno-0-48)'{"location": "Beijing", "temperature": "85", "unit": "fahrenheit", "num_days": 3}'`

Source code in `lazyllm/tools/agent/toolsManager.py`

|  |

``class  ToolManager(ModuleBase):
 """ToolManager是一个工具管理类，用于提供工具信息和工具调用给function call。   此管理类构造时需要传入工具名字符串列表。此处工具名可以是LazyLLM提供的，也可以是用户自定义的，如果是用户自定义的，首先需要注册进LazyLLM中才可以使用。在注册时直接使用 `fc_register` 注册器，该注册器已经建立 `tool` group，所以使用该工具管理类时，所有函数都统一注册进 `tool` 分组即可。待注册的函数需要对函数参数进行注解，并且需要对函数增加功能描述，以及参数类型和作用描述。以方便工具管理类能对函数解析传给LLM使用。   Args:
 tools (List[str]): 工具名称字符串列表。     Examples:
 >>> from lazyllm.tools import ToolManager, fc_register >>> import json >>> from typing import Literal >>> @fc_register("tool") >>> def get_current_weather(location: str, unit: Literal["fahrenheit", "celsius"]="fahrenheit"): ...     ''' ...     Get the current weather in a given location ... ...     Args: ...         location (str): The city and state, e.g. San Francisco, CA. ...         unit (str): The temperature unit to use. Infer this from the users location. ...     ''' ...     if 'tokyo' in location.lower(): ...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius'}) ...     elif 'san francisco' in location.lower(): ...         return json.dumps({'location': 'San Francisco', 'temperature': '72', 'unit': 'fahrenheit'}) ...     elif 'paris' in location.lower(): ...         return json.dumps({'location': 'Paris', 'temperature': '22', 'unit': 'celsius'}) ...     elif 'beijing' in location.lower(): ...         return json.dumps({'location': 'Beijing', 'temperature': '90', 'unit': 'fahrenheit'}) ...     else: ...         return json.dumps({'location': location, 'temperature': 'unknown'}) ... >>> @fc_register("tool") >>> def get_n_day_weather_forecast(location: str, num_days: int, unit: Literal["celsius", "fahrenheit"]='fahrenheit'): ...     ''' ...     Get an N-day weather forecast ... ...     Args: ...         location (str): The city and state, e.g. San Francisco, CA. ...         num_days (int): The number of days to forecast. ...         unit (Literal['celsius', 'fahrenheit']): The temperature unit to use. Infer this from the users location. ...     ''' ...     if 'tokyo' in location.lower(): ...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius', "num_days": num_days}) ...     elif 'san francisco' in location.lower(): ...         return json.dumps({'location': 'San Francisco', 'temperature': '75', 'unit': 'fahrenheit', "num_days": num_days}) ...     elif 'paris' in location.lower(): ...         return json.dumps({'location': 'Paris', 'temperature': '25', 'unit': 'celsius', "num_days": num_days}) ...     elif 'beijing' in location.lower(): ...         return json.dumps({'location': 'Beijing', 'temperature': '85', 'unit': 'fahrenheit', "num_days": num_days}) ...     else: ...         return json.dumps({'location': location, 'temperature': 'unknown'}) ... >>> tools = ["get_current_weather", "get_n_day_weather_forecast"] >>> tm = ToolManager(tools) >>> print(tm([{'name': 'get_n_day_weather_forecast', 'arguments': {'location': 'Beijing', 'num_days': 3}}])[0]) '{"location": "Beijing", "temperature": "85", "unit": "fahrenheit", "num_days": 3}' """ def  __init__(self, tools: List[Union[str, Callable]], return_trace: bool = False): super().__init__(return_trace=return_trace) self._tools = self._load_tools(tools) self._format_tools() self._tools_desc = self._transform_to_openai_function()   def  _load_tools(self, tools: List[Union[str, Callable]]): if "tmp_tool" not in LazyLLMRegisterMetaClass.all_clses: register.new_group('tmp_tool')   _tools = [] for element in tools: if isinstance(element, str): _tools.append(getattr(lazyllm.tool, element)()) elif isinstance(element, Callable): # just to convert `element` to the internal type in `Register` register('tmp_tool')(element) _tools.append(getattr(lazyllm.tmp_tool, element.__name__)()) lazyllm.tmp_tool.remove(element.__name__)   return _tools   @property def  all_tools(self): return self._tools   @property def  tools_description(self): return self._tools_desc   @property def  tools_info(self): return self._tool_call   def  _validate_tool(self, tool_name: str, tool_arguments: Dict[str, Any]): tool = self._tool_call.get(tool_name) if not tool: LOG.error(f'cannot find tool named [{tool_name}]') return False   return tool.validate_parameters(tool_arguments)   def  _format_tools(self): if isinstance(self._tools, List): self._tool_call = {tool.name: tool for tool in self._tools}   @staticmethod def  _gen_args_info_from_moduletool_and_docstring(tool, parsed_docstring): """ returns a dict of param names containing at least 1. `type` 2. `description` of params   for example: args = { "foo": { "enum": ["baz", "bar"], "type": "string", "description": "a string", }, "bar": { "type": "integer", "description": "an integer", } } """ tool_args = tool.args assert len(tool_args) == len(parsed_docstring.params), ("The parameter description and the actual " "number of input parameters are inconsistent.")   args_description = {} for param in parsed_docstring.params: args_description[param.arg_name] = param.description   args = {} for k, v in tool_args.items(): val = copy.deepcopy(v) val.pop("title", None) val.pop("default", None) args[k] = val if val else {"type": "string"} desc = args_description.get(k, None) if desc: args[k].update({"description": desc}) else: raise ValueError(f"The actual input parameter '{k}' is not found " f"in the parameter description of tool '{tool.name}'.") return args   def  _transform_to_openai_function(self): if not isinstance(self._tools, List): raise TypeError(f"The tools type should be List instead of {type(self._tools)}")   format_tools = [] for tool in self._tools: try: parsed_docstring = docstring_parser.parse(tool.description) args = self._gen_args_info_from_moduletool_and_docstring(tool, parsed_docstring) required_arg_list = tool.params_schema.model_json_schema().get("required", []) func = { "type": "function", "function": { "name": tool.name, "description": parsed_docstring.short_description, "parameters": { "type": "object", "properties": args, "required": required_arg_list, } } } format_tools.append(func) except Exception: typehints_template = """ def myfunc(arg1: str, arg2: Dict[str, Any], arg3: Literal["aaa", "bbb", "ccc"]="aaa"): ''' Function description ...   Args: arg1 (str): arg1 description. arg2 (Dict[str, Any]): arg2 description arg3 (Literal["aaa", "bbb", "ccc"]): arg3 description ''' """ raise TypeError("Function description must include function description and " f"parameter description, the format is as follows: {typehints_template}") return format_tools   def  forward(self, tools: Union[Dict[str, Any], List[Dict[str, Any]]], verbose: bool = False): tool_calls = [tools,] if isinstance(tools, dict) else tools tool_calls = [{"name": tool['name'], "arguments": json.loads(tool['arguments']) if isinstance(tool['arguments'], str) else tool['arguments']} for tool in tool_calls] output = [] flag_val = [True if self._validate_tool(tool['name'], tool['arguments']) else False for tool in tool_calls] tool_inputs = [tool_calls[idx]['arguments'] for idx, val in enumerate(flag_val) if val] tools = [self._tool_call[tool_calls[idx]['name']] for idx, val in enumerate(flag_val) if val] tool_diverter = lazyllm.diverter(tuple(tools)) rets = tool_diverter(tuple(tool_inputs)) res = iter(rets) rets = [next(res) if ele else None for ele in flag_val] for idx, tool in enumerate(tool_calls): if flag_val[idx]: ret = rets[idx] output.append(json.dumps(ret, ensure_ascii=False) if not isinstance(ret, str) else ret) else: output.append(f"{tool} parameters error.")   return output``



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`

FunctionCall是单轮工具调用类，如果LLM中的信息不足以回答用户的问题，必需结合外部知识来回答用户问题，则调用该类。如果LLM输出需要工具调用，则进行工具调用，并输出工具调用结果，输出结果为List类型，包含当前轮的输入、模型输出、工具输出。如果不需要工具调用，则直接输出LLM结果，输出结果为string类型。

Parameters:

*   **`llm`** (`[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`) –

    要使用的LLM可以是TrainableModule或OnlineChatModule。

*   **`tools`** (`List[Union[str, Callable]]`) –

    LLM使用的工具名称或者 Callable 列表


注意：tools 中使用的工具必须带有 `__doc__` 字段，按照 [Google Python Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) 的要求描述清楚工具的用途和参数。

Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> from  lazyllm.tools  import fc_register, FunctionCall [](#__codelineno-0-3)>>> import  json [](#__codelineno-0-4)>>> from  typing  import Literal [](#__codelineno-0-5)>>> @fc_register("tool") [](#__codelineno-0-6)>>> def  get_current_weather(location: str, unit: Literal["fahrenheit", "celsius"] = 'fahrenheit'): [](#__codelineno-0-7)...  ''' [](#__codelineno-0-8)...     Get the current weather in a given location [](#__codelineno-0-9)... [](#__codelineno-0-10)...     Args: [](#__codelineno-0-11)...         location (str): The city and state, e.g. San Francisco, CA. [](#__codelineno-0-12)...         unit (str): The temperature unit to use. Infer this from the users location. [](#__codelineno-0-13)...     ''' [](#__codelineno-0-14)...     if 'tokyo' in location.lower(): [](#__codelineno-0-15)...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius'}) [](#__codelineno-0-16)...     elif 'san francisco' in location.lower(): [](#__codelineno-0-17)...         return json.dumps({'location': 'San Francisco', 'temperature': '72', 'unit': 'fahrenheit'}) [](#__codelineno-0-18)...     elif 'paris' in location.lower(): [](#__codelineno-0-19)...         return json.dumps({'location': 'Paris', 'temperature': '22', 'unit': 'celsius'}) [](#__codelineno-0-20)...     else: [](#__codelineno-0-21)...         return json.dumps({'location': location, 'temperature': 'unknown'}) [](#__codelineno-0-22)... [](#__codelineno-0-23)>>> @fc_register("tool") [](#__codelineno-0-24)>>> def  get_n_day_weather_forecast(location: str, num_days: int, unit: Literal["celsius", "fahrenheit"] = 'fahrenheit'): [](#__codelineno-0-25)...  ''' [](#__codelineno-0-26)...     Get an N-day weather forecast [](#__codelineno-0-27)... [](#__codelineno-0-28)...     Args: [](#__codelineno-0-29)...         location (str): The city and state, e.g. San Francisco, CA. [](#__codelineno-0-30)...         num_days (int): The number of days to forecast. [](#__codelineno-0-31)...         unit (Literal['celsius', 'fahrenheit']): The temperature unit to use. Infer this from the users location. [](#__codelineno-0-32)...     ''' [](#__codelineno-0-33)...     if 'tokyo' in location.lower(): [](#__codelineno-0-34)...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius', "num_days": num_days}) [](#__codelineno-0-35)...     elif 'san francisco' in location.lower(): [](#__codelineno-0-36)...         return json.dumps({'location': 'San Francisco', 'temperature': '72', 'unit': 'fahrenheit', "num_days": num_days}) [](#__codelineno-0-37)...     elif 'paris' in location.lower(): [](#__codelineno-0-38)...         return json.dumps({'location': 'Paris', 'temperature': '22', 'unit': 'celsius', "num_days": num_days}) [](#__codelineno-0-39)...     else: [](#__codelineno-0-40)...         return json.dumps({'location': location, 'temperature': 'unknown'}) [](#__codelineno-0-41)... [](#__codelineno-0-42)>>> tools=["get_current_weather", "get_n_day_weather_forecast"] [](#__codelineno-0-43)>>> llm = lazyllm.TrainableModule("internlm2-chat-20b").start()  # or llm = lazyllm.OnlineChatModule("openai", stream=False) [](#__codelineno-0-44)>>> query = "What's the weather like today in celsius in Tokyo." [](#__codelineno-0-45)>>> fc = FunctionCall(llm, tools) [](#__codelineno-0-46)>>> ret = fc(query) [](#__codelineno-0-47)>>> print(ret) [](#__codelineno-0-48)["What's the weather like today in celsius in Tokyo.", {'role': 'assistant', 'content': ' [](#__codelineno-0-49)', 'tool_calls': [{'id': 'da19cddac0584869879deb1315356d2a', 'type': 'function', 'function': {'name': 'get_current_weather', 'arguments': {'location': 'Tokyo', 'unit': 'celsius'}}}]}, [{'role': 'tool', 'content': '{"location": "Tokyo", "temperature": "10", "unit": "celsius"}', 'tool_call_id': 'da19cddac0584869879deb1315356d2a', 'name': 'get_current_weather'}]] [](#__codelineno-0-50)>>> query = "Hello" [](#__codelineno-0-51)>>> ret = fc(query) [](#__codelineno-0-52)>>> print(ret) [](#__codelineno-0-53)'Hello! How can I assist you today?'`

Source code in `lazyllm/tools/agent/functionCall.py`

|  |

``class  FunctionCall(ModuleBase):
 """FunctionCall是单轮工具调用类，如果LLM中的信息不足以回答用户的问题，必需结合外部知识来回答用户问题，则调用该类。如果LLM输出需要工具调用，则进行工具调用，并输出工具调用结果，输出结果为List类型，包含当前轮的输入、模型输出、工具输出。如果不需要工具调用，则直接输出LLM结果，输出结果为string类型。   Args:
 llm (ModuleBase): 要使用的LLM可以是TrainableModule或OnlineChatModule。 tools (List[Union[str, Callable]]): LLM使用的工具名称或者 Callable 列表   注意：tools 中使用的工具必须带有 `__doc__` 字段，按照 [Google Python Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) 的要求描述清楚工具的用途和参数。     Examples:
 >>> import lazyllm >>> from lazyllm.tools import fc_register, FunctionCall >>> import json >>> from typing import Literal >>> @fc_register("tool") >>> def get_current_weather(location: str, unit: Literal["fahrenheit", "celsius"] = 'fahrenheit'): ...     ''' ...     Get the current weather in a given location ... ...     Args: ...         location (str): The city and state, e.g. San Francisco, CA. ...         unit (str): The temperature unit to use. Infer this from the users location. ...     ''' ...     if 'tokyo' in location.lower(): ...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius'}) ...     elif 'san francisco' in location.lower(): ...         return json.dumps({'location': 'San Francisco', 'temperature': '72', 'unit': 'fahrenheit'}) ...     elif 'paris' in location.lower(): ...         return json.dumps({'location': 'Paris', 'temperature': '22', 'unit': 'celsius'}) ...     else: ...         return json.dumps({'location': location, 'temperature': 'unknown'}) ... >>> @fc_register("tool") >>> def get_n_day_weather_forecast(location: str, num_days: int, unit: Literal["celsius", "fahrenheit"] = 'fahrenheit'): ...     ''' ...     Get an N-day weather forecast ... ...     Args: ...         location (str): The city and state, e.g. San Francisco, CA. ...         num_days (int): The number of days to forecast. ...         unit (Literal['celsius', 'fahrenheit']): The temperature unit to use. Infer this from the users location. ...     ''' ...     if 'tokyo' in location.lower(): ...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius', "num_days": num_days}) ...     elif 'san francisco' in location.lower(): ...         return json.dumps({'location': 'San Francisco', 'temperature': '72', 'unit': 'fahrenheit', "num_days": num_days}) ...     elif 'paris' in location.lower(): ...         return json.dumps({'location': 'Paris', 'temperature': '22', 'unit': 'celsius', "num_days": num_days}) ...     else: ...         return json.dumps({'location': location, 'temperature': 'unknown'}) ... >>> tools=["get_current_weather", "get_n_day_weather_forecast"] >>> llm = lazyllm.TrainableModule("internlm2-chat-20b").start()  # or llm = lazyllm.OnlineChatModule("openai", stream=False) >>> query = "What's the weather like today in celsius in Tokyo." >>> fc = FunctionCall(llm, tools) >>> ret = fc(query) >>> print(ret) ["What's the weather like today in celsius in Tokyo.", {'role': 'assistant', 'content': ' ', 'tool_calls': [{'id': 'da19cddac0584869879deb1315356d2a', 'type': 'function', 'function': {'name': 'get_current_weather', 'arguments': {'location': 'Tokyo', 'unit': 'celsius'}}}]}, [{'role': 'tool', 'content': '{"location": "Tokyo", "temperature": "10", "unit": "celsius"}', 'tool_call_id': 'da19cddac0584869879deb1315356d2a', 'name': 'get_current_weather'}]] >>> query = "Hello" >>> ret = fc(query) >>> print(ret) 'Hello! How can I assist you today?' """   def  __init__(self, llm, tools: List[Union[str, Callable]], *, return_trace: bool = False, stream: bool = False, _prompt: str = None): super().__init__(return_trace=return_trace) if isinstance(llm, OnlineChatModule) and llm.series == "QWEN" and llm._stream is True: raise ValueError("The qwen platform does not currently support stream function calls.") if _prompt is None: _prompt = FC_PROMPT_ONLINE if isinstance(llm, OnlineChatModule) else FC_PROMPT_LOCAL   self._tools_manager = ToolManager(tools, return_trace=return_trace) self._prompter = ChatPrompter(instruction=_prompt, tools=self._tools_manager.tools_description)\ .pre_hook(function_call_hook) self._llm = llm.share(prompt=self._prompter, format=FunctionCallFormatter()).used_by(self._module_id) with pipeline() as self._impl: self._impl.ins = StreamResponse('Received instruction:', prefix_color=Color.yellow, color=Color.green, stream=stream) self._impl.m1 = self._llm self._impl.m2 = self._parser self._impl.dis = StreamResponse('Decision-making or result in this round:', prefix_color=Color.yellow, color=Color.green, stream=stream) self._impl.m3 = ifs(lambda x: isinstance(x, list), pipeline(self._tools_manager, StreamResponse('Tool-Call result:', prefix_color=Color.yellow, color=Color.green, stream=stream)), lambda out: out) self._impl.m4 = self._tool_post_action | bind(input=self._impl.input, llm_output=self._impl.m1)   def  _parser(self, llm_output: Union[str, List[Dict[str, Any]]]): LOG.debug(f"llm_output: {llm_output}") if isinstance(llm_output, list): res = [] for item in llm_output: if isinstance(item, str): continue arguments = item.get('function', {}).get('arguments', '') arguments = json.loads(arguments) if isinstance(arguments, str) else arguments res.append({"name": item.get('function', {}).get('name', ''), 'arguments': arguments}) return res elif isinstance(llm_output, str): return llm_output else: raise TypeError(f"The {llm_output} type currently is only supports `list` and `str`," f" and does not support {type(llm_output)}.")   def  _tool_post_action(self, output: Union[str, List[str]], input: Union[str, List], llm_output: List[Dict[str, Any]]): if isinstance(output, list): ret = [] if isinstance(input, str): ret.append(input) elif isinstance(input, list): ret.append(input[-1]) else: raise TypeError(f"The input type currently only supports `str` and `list`, " f"and does not support {type(input)}.")   content = "".join([item for item in llm_output if isinstance(item, str)]) llm_output = [item for item in llm_output if not isinstance(item, str)] ret.append({"role": "assistant", "content": content, "tool_calls": llm_output}) ret.append([{"role": "tool", "content": out, "tool_call_id": llm_output[idx]["id"], "name": llm_output[idx]["function"]["name"]} for idx, out in enumerate(output)]) LOG.debug(f"functionCall result: {ret}") return ret elif isinstance(output, str): return output else: raise TypeError(f"The {output} type currently is only supports `list` and `str`," f" and does not support {type(output)}.")   def  forward(self, input: str, llm_chat_history: List[Dict[str, Any]] = None): globals['chat_history'].setdefault(self._llm._module_id, []) if llm_chat_history is not None: globals['chat_history'][self._llm._module_id] = llm_chat_history return self._impl(input)``



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`

FunctionCallAgent是一个使用工具调用方式进行完整工具调用的代理，即回答用户问题时，LLM如果需要通过工具获取外部知识，就会调用工具，并将工具的返回结果反馈给LLM，最后由LLM进行汇总输出。

Parameters:

*   **`llm`** (`[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`) –

    要使用的LLM，可以是TrainableModule或OnlineChatModule。

*   **`tools`** (`List[str]`) –

    LLM 使用的工具名称列表。

*   **`max_retries`** (`int`, default: `5` ) –

    工具调用迭代的最大次数。默认值为5。


Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> from  lazyllm.tools  import fc_register, FunctionCallAgent [](#__codelineno-0-3)>>> import  json [](#__codelineno-0-4)>>> from  typing  import Literal [](#__codelineno-0-5)>>> @fc_register("tool") [](#__codelineno-0-6)>>> def  get_current_weather(location: str, unit: Literal["fahrenheit", "celsius"]='fahrenheit'): [](#__codelineno-0-7)...  ''' [](#__codelineno-0-8)...     Get the current weather in a given location [](#__codelineno-0-9)... [](#__codelineno-0-10)...     Args: [](#__codelineno-0-11)...         location (str): The city and state, e.g. San Francisco, CA. [](#__codelineno-0-12)...         unit (str): The temperature unit to use. Infer this from the users location. [](#__codelineno-0-13)...     ''' [](#__codelineno-0-14)...     if 'tokyo' in location.lower(): [](#__codelineno-0-15)...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius'}) [](#__codelineno-0-16)...     elif 'san francisco' in location.lower(): [](#__codelineno-0-17)...         return json.dumps({'location': 'San Francisco', 'temperature': '72', 'unit': 'fahrenheit'}) [](#__codelineno-0-18)...     elif 'paris' in location.lower(): [](#__codelineno-0-19)...         return json.dumps({'location': 'Paris', 'temperature': '22', 'unit': 'celsius'}) [](#__codelineno-0-20)...     elif 'beijing' in location.lower(): [](#__codelineno-0-21)...         return json.dumps({'location': 'Beijing', 'temperature': '90', 'unit': 'Fahrenheit'}) [](#__codelineno-0-22)...     else: [](#__codelineno-0-23)...         return json.dumps({'location': location, 'temperature': 'unknown'}) [](#__codelineno-0-24)... [](#__codelineno-0-25)>>> @fc_register("tool") [](#__codelineno-0-26)>>> def  get_n_day_weather_forecast(location: str, num_days: int, unit: Literal["celsius", "fahrenheit"]='fahrenheit'): [](#__codelineno-0-27)...  ''' [](#__codelineno-0-28)...     Get an N-day weather forecast [](#__codelineno-0-29)... [](#__codelineno-0-30)...     Args: [](#__codelineno-0-31)...         location (str): The city and state, e.g. San Francisco, CA. [](#__codelineno-0-32)...         num_days (int): The number of days to forecast. [](#__codelineno-0-33)...         unit (Literal['celsius', 'fahrenheit']): The temperature unit to use. Infer this from the users location. [](#__codelineno-0-34)...     ''' [](#__codelineno-0-35)...     if 'tokyo' in location.lower(): [](#__codelineno-0-36)...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius', "num_days": num_days}) [](#__codelineno-0-37)...     elif 'san francisco' in location.lower(): [](#__codelineno-0-38)...         return json.dumps({'location': 'San Francisco', 'temperature': '75', 'unit': 'fahrenheit', "num_days": num_days}) [](#__codelineno-0-39)...     elif 'paris' in location.lower(): [](#__codelineno-0-40)...         return json.dumps({'location': 'Paris', 'temperature': '25', 'unit': 'celsius', "num_days": num_days}) [](#__codelineno-0-41)...     elif 'beijing' in location.lower(): [](#__codelineno-0-42)...         return json.dumps({'location': 'Beijing', 'temperature': '85', 'unit': 'fahrenheit', "num_days": num_days}) [](#__codelineno-0-43)...     else: [](#__codelineno-0-44)...         return json.dumps({'location': location, 'temperature': 'unknown'}) [](#__codelineno-0-45)... [](#__codelineno-0-46)>>> tools = ['get_current_weather', 'get_n_day_weather_forecast'] [](#__codelineno-0-47)>>> llm = lazyllm.TrainableModule("internlm2-chat-20b").start()  # or llm = lazyllm.OnlineChatModule(source="sensenova") [](#__codelineno-0-48)>>> agent = FunctionCallAgent(llm, tools) [](#__codelineno-0-49)>>> query = "What's the weather like today in celsius in Tokyo and Paris." [](#__codelineno-0-50)>>> res = agent(query) [](#__codelineno-0-51)>>> print(res) [](#__codelineno-0-52)'The current weather in Tokyo is 10 degrees Celsius, and in Paris, it is 22 degrees Celsius.' [](#__codelineno-0-53)>>> query = "Hello" [](#__codelineno-0-54)>>> res = agent(query) [](#__codelineno-0-55)>>> print(res) [](#__codelineno-0-56)'Hello! How can I assist you today?'`

Source code in `lazyllm/tools/agent/functionCall.py`

|  |

`class  FunctionCallAgent(ModuleBase):
 """FunctionCallAgent是一个使用工具调用方式进行完整工具调用的代理，即回答用户问题时，LLM如果需要通过工具获取外部知识，就会调用工具，并将工具的返回结果反馈给LLM，最后由LLM进行汇总输出。   Args:
 llm (ModuleBase): 要使用的LLM，可以是TrainableModule或OnlineChatModule。 tools (List[str]): LLM 使用的工具名称列表。 max_retries (int): 工具调用迭代的最大次数。默认值为5。     Examples:
 >>> import lazyllm >>> from lazyllm.tools import fc_register, FunctionCallAgent >>> import json >>> from typing import Literal >>> @fc_register("tool") >>> def get_current_weather(location: str, unit: Literal["fahrenheit", "celsius"]='fahrenheit'): ...     ''' ...     Get the current weather in a given location ... ...     Args: ...         location (str): The city and state, e.g. San Francisco, CA. ...         unit (str): The temperature unit to use. Infer this from the users location. ...     ''' ...     if 'tokyo' in location.lower(): ...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius'}) ...     elif 'san francisco' in location.lower(): ...         return json.dumps({'location': 'San Francisco', 'temperature': '72', 'unit': 'fahrenheit'}) ...     elif 'paris' in location.lower(): ...         return json.dumps({'location': 'Paris', 'temperature': '22', 'unit': 'celsius'}) ...     elif 'beijing' in location.lower(): ...         return json.dumps({'location': 'Beijing', 'temperature': '90', 'unit': 'Fahrenheit'}) ...     else: ...         return json.dumps({'location': location, 'temperature': 'unknown'}) ... >>> @fc_register("tool") >>> def get_n_day_weather_forecast(location: str, num_days: int, unit: Literal["celsius", "fahrenheit"]='fahrenheit'): ...     ''' ...     Get an N-day weather forecast ... ...     Args: ...         location (str): The city and state, e.g. San Francisco, CA. ...         num_days (int): The number of days to forecast. ...         unit (Literal['celsius', 'fahrenheit']): The temperature unit to use. Infer this from the users location. ...     ''' ...     if 'tokyo' in location.lower(): ...         return json.dumps({'location': 'Tokyo', 'temperature': '10', 'unit': 'celsius', "num_days": num_days}) ...     elif 'san francisco' in location.lower(): ...         return json.dumps({'location': 'San Francisco', 'temperature': '75', 'unit': 'fahrenheit', "num_days": num_days}) ...     elif 'paris' in location.lower(): ...         return json.dumps({'location': 'Paris', 'temperature': '25', 'unit': 'celsius', "num_days": num_days}) ...     elif 'beijing' in location.lower(): ...         return json.dumps({'location': 'Beijing', 'temperature': '85', 'unit': 'fahrenheit', "num_days": num_days}) ...     else: ...         return json.dumps({'location': location, 'temperature': 'unknown'}) ... >>> tools = ['get_current_weather', 'get_n_day_weather_forecast'] >>> llm = lazyllm.TrainableModule("internlm2-chat-20b").start()  # or llm = lazyllm.OnlineChatModule(source="sensenova") >>> agent = FunctionCallAgent(llm, tools) >>> query = "What's the weather like today in celsius in Tokyo and Paris." >>> res = agent(query) >>> print(res) 'The current weather in Tokyo is 10 degrees Celsius, and in Paris, it is 22 degrees Celsius.' >>> query = "Hello" >>> res = agent(query) >>> print(res) 'Hello! How can I assist you today?' """ def  __init__(self, llm, tools: List[str], max_retries: int = 5, return_trace: bool = False, stream: bool = False): super().__init__(return_trace=return_trace) self._max_retries = max_retries self._fc = FunctionCall(llm, tools, return_trace=return_trace, stream=stream) self._agent = loop(self._fc, stop_condition=lambda x: isinstance(x, str), count=self._max_retries) self._fc._llm.used_by(self._module_id)   def  forward(self, query: str, llm_chat_history: List[Dict[str, Any]] = None): ret = self._agent(query, llm_chat_history) if llm_chat_history is not None else self._agent(query) return ret if isinstance(ret, str) else (_ for _ in ()).throw( ValueError(f"After retrying {self._max_retries} times, the function call agent still " "failed to call successfully."))`



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`

ReactAgent是按照 `Thought->Action->Observation->Thought...->Finish` 的流程一步一步的通过LLM和工具调用来显示解决用户问题的步骤，以及最后给用户的答案。

Parameters:

*   **`llm`** (`[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`) –

    要使用的LLM，可以是TrainableModule或OnlineChatModule。

*   **`tools`** (`List[str]`) –

    LLM 使用的工具名称列表。

*   **`max_retries`** (`int`, default: `5` ) –

    工具调用迭代的最大次数。默认值为5。


Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> from  lazyllm.tools  import fc_register, ReactAgent [](#__codelineno-0-3)>>> @fc_register("tool") [](#__codelineno-0-4)>>> def  multiply_tool(a: int, b: int) -> int: [](#__codelineno-0-5)...  ''' [](#__codelineno-0-6)...     Multiply two integers and return the result integer [](#__codelineno-0-7)... [](#__codelineno-0-8)...     Args: [](#__codelineno-0-9)...         a (int): multiplier [](#__codelineno-0-10)...         b (int): multiplier [](#__codelineno-0-11)...     ''' [](#__codelineno-0-12)...     return a * b [](#__codelineno-0-13)... [](#__codelineno-0-14)>>> @fc_register("tool") [](#__codelineno-0-15)>>> def  add_tool(a: int, b: int): [](#__codelineno-0-16)...  ''' [](#__codelineno-0-17)...     Add two integers and returns the result integer [](#__codelineno-0-18)... [](#__codelineno-0-19)...     Args: [](#__codelineno-0-20)...         a (int): addend [](#__codelineno-0-21)...         b (int): addend [](#__codelineno-0-22)...     ''' [](#__codelineno-0-23)...     return a + b [](#__codelineno-0-24)... [](#__codelineno-0-25)>>> tools = ["multiply_tool", "add_tool"] [](#__codelineno-0-26)>>> llm = lazyllm.TrainableModule("internlm2-chat-20b").start()   # or llm = lazyllm.OnlineChatModule(source="sensenova") [](#__codelineno-0-27)>>> agent = ReactAgent(llm, tools) [](#__codelineno-0-28)>>> query = "What is 20+(2*4)? Calculate step by step." [](#__codelineno-0-29)>>> res = agent(query) [](#__codelineno-0-30)>>> print(res) [](#__codelineno-0-31)'Answer: The result of 20+(2*4) is 28.'`

Source code in `lazyllm/tools/agent/reactAgent.py`

|  |

``class  ReactAgent(ModuleBase):
 """ReactAgent是按照 `Thought->Action->Observation->Thought...->Finish` 的流程一步一步的通过LLM和工具调用来显示解决用户问题的步骤，以及最后给用户的答案。   Args:
 llm (ModuleBase): 要使用的LLM，可以是TrainableModule或OnlineChatModule。 tools (List[str]): LLM 使用的工具名称列表。 max_retries (int): 工具调用迭代的最大次数。默认值为5。     Examples:
 >>> import lazyllm >>> from lazyllm.tools import fc_register, ReactAgent >>> @fc_register("tool") >>> def multiply_tool(a: int, b: int) -> int: ...     ''' ...     Multiply two integers and return the result integer ... ...     Args: ...         a (int): multiplier ...         b (int): multiplier ...     ''' ...     return a * b ... >>> @fc_register("tool") >>> def add_tool(a: int, b: int): ...     ''' ...     Add two integers and returns the result integer ... ...     Args: ...         a (int): addend ...         b (int): addend ...     ''' ...     return a + b ... >>> tools = ["multiply_tool", "add_tool"] >>> llm = lazyllm.TrainableModule("internlm2-chat-20b").start()   # or llm = lazyllm.OnlineChatModule(source="sensenova") >>> agent = ReactAgent(llm, tools) >>> query = "What is 20+(2*4)? Calculate step by step." >>> res = agent(query) >>> print(res) 'Answer: The result of 20+(2*4) is 28.' """ def  __init__(self, llm, tools: List[str], max_retries: int = 5, return_trace: bool = False, prompt: str = None, stream: bool = False): super().__init__(return_trace=return_trace) self._max_retries = max_retries assert llm and tools, "llm and tools cannot be empty."   if not prompt: prompt = INSTRUCTION.replace("{TOKENIZED_PROMPT}", WITHOUT_TOKEN_PROMPT if isinstance(llm, OnlineChatModule) else WITH_TOKEN_PROMPT) prompt = prompt.replace("{tool_names}", json.dumps([t.__name__ if callable(t) else t for t in tools], ensure_ascii=False)) self._agent = loop(FunctionCall(llm, tools, _prompt=prompt, return_trace=return_trace, stream=stream), stop_condition=lambda x: isinstance(x, str), count=self._max_retries)   def  forward(self, query: str, llm_chat_history: List[Dict[str, Any]] = None): ret = self._agent(query, llm_chat_history) if llm_chat_history is not None else self._agent(query) return ret if isinstance(ret, str) else (_ for _ in ()).throw(ValueError(f"After retrying \ {self._max_retries} times, the function call agent still failes to call successfully."))``



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`

PlanAndSolveAgent由两个组件组成，首先，由planner将整个任务分解为更小的子任务，然后由solver根据计划执行这些子任务，其中可能会涉及到工具调用，最后将答案返回给用户。

Parameters:

*   **`llm`** (`[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`, default: `None` ) –

    要使用的LLM，可以是TrainableModule或OnlineChatModule。和plan\_llm、solve\_llm互斥，要么设置llm(planner和solver公用一个LLM)，要么设置plan\_llm和solve\_llm，或者只指定llm(用来设置planner)和solve\_llm，其它情况均认为是无效的。

*   **`tools`** (`List[str]`, default: `[]` ) –

    LLM使用的工具名称列表。

*   **`plan_llm`** (`[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`, default: `None` ) –

    planner要使用的LLM，可以是TrainableModule或OnlineChatModule。

*   **`solve_llm`** (`[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`, default: `None` ) –

    solver要使用的LLM，可以是TrainableModule或OnlineChatModule。

*   **`max_retries`** (`int`, default: `5` ) –

    工具调用迭代的最大次数。默认值为5。


Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> from  lazyllm.tools  import fc_register, PlanAndSolveAgent [](#__codelineno-0-3)>>> @fc_register("tool") [](#__codelineno-0-4)>>> def  multiply(a: int, b: int) -> int: [](#__codelineno-0-5)...  ''' [](#__codelineno-0-6)...     Multiply two integers and return the result integer [](#__codelineno-0-7)... [](#__codelineno-0-8)...     Args: [](#__codelineno-0-9)...         a (int): multiplier [](#__codelineno-0-10)...         b (int): multiplier [](#__codelineno-0-11)...     ''' [](#__codelineno-0-12)...     return a * b [](#__codelineno-0-13)... [](#__codelineno-0-14)>>> @fc_register("tool") [](#__codelineno-0-15)>>> def  add(a: int, b: int): [](#__codelineno-0-16)...  ''' [](#__codelineno-0-17)...     Add two integers and returns the result integer [](#__codelineno-0-18)... [](#__codelineno-0-19)...     Args: [](#__codelineno-0-20)...         a (int): addend [](#__codelineno-0-21)...         b (int): addend [](#__codelineno-0-22)...     ''' [](#__codelineno-0-23)...     return a + b [](#__codelineno-0-24)... [](#__codelineno-0-25)>>> tools = ["multiply", "add"] [](#__codelineno-0-26)>>> llm = lazyllm.TrainableModule("internlm2-chat-20b").start()  # or llm = lazyllm.OnlineChatModule(source="sensenova") [](#__codelineno-0-27)>>> agent = PlanAndSolveAgent(llm, tools) [](#__codelineno-0-28)>>> query = "What is 20+(2*4)? Calculate step by step." [](#__codelineno-0-29)>>> res = agent(query) [](#__codelineno-0-30)>>> print(res) [](#__codelineno-0-31)'The final answer is 28.'`

Source code in `lazyllm/tools/agent/planAndSolveAgent.py`

|  |

`class  PlanAndSolveAgent(ModuleBase):
 """PlanAndSolveAgent由两个组件组成，首先，由planner将整个任务分解为更小的子任务，然后由solver根据计划执行这些子任务，其中可能会涉及到工具调用，最后将答案返回给用户。   Args:
 llm (ModuleBase): 要使用的LLM，可以是TrainableModule或OnlineChatModule。和plan_llm、solve_llm互斥，要么设置llm(planner和solver公用一个LLM)，要么设置plan_llm和solve_llm，或者只指定llm(用来设置planner)和solve_llm，其它情况均认为是无效的。 tools (List[str]): LLM使用的工具名称列表。 plan_llm (ModuleBase): planner要使用的LLM，可以是TrainableModule或OnlineChatModule。 solve_llm (ModuleBase): solver要使用的LLM，可以是TrainableModule或OnlineChatModule。 max_retries (int): 工具调用迭代的最大次数。默认值为5。     Examples:
 >>> import lazyllm >>> from lazyllm.tools import fc_register, PlanAndSolveAgent >>> @fc_register("tool") >>> def multiply(a: int, b: int) -> int: ...     ''' ...     Multiply two integers and return the result integer ... ...     Args: ...         a (int): multiplier ...         b (int): multiplier ...     ''' ...     return a * b ... >>> @fc_register("tool") >>> def add(a: int, b: int): ...     ''' ...     Add two integers and returns the result integer ... ...     Args: ...         a (int): addend ...         b (int): addend ...     ''' ...     return a + b ... >>> tools = ["multiply", "add"] >>> llm = lazyllm.TrainableModule("internlm2-chat-20b").start()  # or llm = lazyllm.OnlineChatModule(source="sensenova") >>> agent = PlanAndSolveAgent(llm, tools) >>> query = "What is 20+(2*4)? Calculate step by step." >>> res = agent(query) >>> print(res) 'The final answer is 28.' """ def  __init__(self, llm: Union[ModuleBase, None] = None, tools: List[str] = [], *, plan_llm: Union[ModuleBase, None] = None, solve_llm: Union[ModuleBase, None] = None, max_retries: int = 5, return_trace: bool = False, stream: bool = False): super().__init__(return_trace=return_trace) self._max_retries = max_retries assert (llm is None and plan_llm and solve_llm) or (llm and plan_llm is None), 'Either specify only llm \ without specify plan and solve, or specify only plan and solve without specifying llm, or specify \ both llm and solve. Other situations are not allowed.' assert tools, "tools cannot be empty." s = dict(prefix='I will give a plan first:\n', prefix_color=Color.blue, color=Color.green) if stream else False self._plan_llm = ((plan_llm or llm).share(prompt=ChatPrompter(instruction=PLANNER_PROMPT), stream=s).used_by(self._module_id)) self._solve_llm = (solve_llm or llm).share().used_by(self._module_id) self._tools = tools with pipeline() as self._agent: self._agent.plan = self._plan_llm self._agent.parse = (lambda text, query: package([], '', [v for v in re.split("\n\\s*\\d+\\. ", text)[1:]], query)) | bind(query=self._agent.input) with loop(stop_condition=lambda pre, res, steps, query: len(steps) == 0) as self._agent.lp: self._agent.lp.pre_action = self._pre_action self._agent.lp.solve = FunctionCallAgent(self._solve_llm, tools=self._tools, return_trace=return_trace, stream=stream) self._agent.lp.post_action = self._post_action | bind(self._agent.lp.input[0][0], _0, self._agent.lp.input[0][2], self._agent.lp.input[0][3])   self._agent.post_action = lambda pre, res, steps, query: res   def  _pre_action(self, pre_steps, response, steps, query): result = package(SOLVER_PROMPT.format(previous_steps="\n".join(pre_steps), current_step=steps[0], objective=query) + "input: " + response + "\n" + steps[0], []) return result   def  _post_action(self, pre_steps: List[str], response: str, steps: List[str], query: str): LOG.debug(f"current step: {steps[0]}, response: {response}") pre_steps.append(steps.pop(0)) return package(pre_steps, response, steps, query)   def  forward(self, query: str): return self._agent(query)`



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`

ReWOOAgent包含三个部分：Planner、Worker和Solver。其中，Planner使用可预见推理能力为复杂任务创建解决方案蓝图；Worker通过工具调用来与环境交互，并将实际证据或观察结果填充到指令中；Solver处理所有计划和证据以制定原始任务或问题的解决方案。

Parameters:

*   **`llm`** (`[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`, default: `None` ) –

    要使用的LLM，可以是TrainableModule或OnlineChatModule。和plan\_llm、solve\_llm互斥，要么设置llm(planner和solver公用一个LLM)，要么设置plan\_llm和solve\_llm，或者只指定llm(用来设置planner)和solve\_llm，其它情况均认为是无效的。

*   **`tools`** (`List[str]`, default: `[]` ) –

    LLM使用的工具名称列表。

*   **`plan_llm`** (`[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`, default: `None` ) –

    planner要使用的LLM，可以是TrainableModule或OnlineChatModule。

*   **`solve_llm`** (`[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`, default: `None` ) –

    solver要使用的LLM，可以是TrainableModule或OnlineChatModule。

*   **`max_retries`** (`int`) –

    工具调用迭代的最大次数。默认值为5。


Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> import  wikipedia [](#__codelineno-0-3)>>> from  lazyllm.tools  import fc_register, ReWOOAgent [](#__codelineno-0-4)>>> @fc_register("tool") [](#__codelineno-0-5)>>> def  WikipediaWorker(input: str): [](#__codelineno-0-6)...  ''' [](#__codelineno-0-7)...     Worker that search for similar page contents from Wikipedia. Useful when you need to get holistic knowledge about people, places, companies, historical events, or other subjects. The response are long and might contain some irrelevant information. Input should be a search query. [](#__codelineno-0-8)... [](#__codelineno-0-9)...     Args: [](#__codelineno-0-10)...         input (str): search query. [](#__codelineno-0-11)...     ''' [](#__codelineno-0-12)...     try: [](#__codelineno-0-13)...         evidence = wikipedia.page(input).content [](#__codelineno-0-14)...         evidence = evidence.split("\n\n")[0] [](#__codelineno-0-15)...     except wikipedia.PageError: [](#__codelineno-0-16)...         evidence = f"Could not find [{input}]. Similar: {wikipedia.search(input)}" [](#__codelineno-0-17)...     except wikipedia.DisambiguationError: [](#__codelineno-0-18)...         evidence = f"Could not find [{input}]. Similar: {wikipedia.search(input)}" [](#__codelineno-0-19)...     return evidence [](#__codelineno-0-20)... [](#__codelineno-0-21)>>> @fc_register("tool") [](#__codelineno-0-22)>>> def  LLMWorker(input: str): [](#__codelineno-0-23)...  ''' [](#__codelineno-0-24)...     A pretrained LLM like yourself. Useful when you need to act with general world knowledge and common sense. Prioritize it when you are confident in solving the problem yourself. Input can be any instruction. [](#__codelineno-0-25)... [](#__codelineno-0-26)...     Args: [](#__codelineno-0-27)...         input (str): instruction [](#__codelineno-0-28)...     ''' [](#__codelineno-0-29)...     llm = lazyllm.OnlineChatModule(source="glm") [](#__codelineno-0-30)...     query = f"Respond in short directly with no extra words.\n\n{input}" [](#__codelineno-0-31)...     response = llm(query, llm_chat_history=[]) [](#__codelineno-0-32)...     return response [](#__codelineno-0-33)... [](#__codelineno-0-34)>>> tools = ["WikipediaWorker", "LLMWorker"] [](#__codelineno-0-35)>>> llm = lazyllm.TrainableModule("GLM-4-9B-Chat").deploy_method(lazyllm.deploy.vllm).start()  # or llm = lazyllm.OnlineChatModule(source="sensenova") [](#__codelineno-0-36)>>> agent = ReWOOAgent(llm, tools) [](#__codelineno-0-37)>>> query = "What is the name of the cognac house that makes the main ingredient in The Hennchata?" [](#__codelineno-0-38)>>> res = agent(query) [](#__codelineno-0-39)>>> print(res) [](#__codelineno-0-40)' [](#__codelineno-0-41)Hennessy '`

Source code in `lazyllm/tools/agent/rewooAgent.py`

|  |

`class  ReWOOAgent(ModuleBase):
 """ReWOOAgent包含三个部分：Planner、Worker和Solver。其中，Planner使用可预见推理能力为复杂任务创建解决方案蓝图；Worker通过工具调用来与环境交互，并将实际证据或观察结果填充到指令中；Solver处理所有计划和证据以制定原始任务或问题的解决方案。   Args:
 llm (ModuleBase): 要使用的LLM，可以是TrainableModule或OnlineChatModule。和plan_llm、solve_llm互斥，要么设置llm(planner和solver公用一个LLM)，要么设置plan_llm和solve_llm，或者只指定llm(用来设置planner)和solve_llm，其它情况均认为是无效的。 tools (List[str]): LLM使用的工具名称列表。 plan_llm (ModuleBase): planner要使用的LLM，可以是TrainableModule或OnlineChatModule。 solve_llm (ModuleBase): solver要使用的LLM，可以是TrainableModule或OnlineChatModule。 max_retries (int): 工具调用迭代的最大次数。默认值为5。     Examples:
 >>> import lazyllm >>> import wikipedia >>> from lazyllm.tools import fc_register, ReWOOAgent >>> @fc_register("tool") >>> def WikipediaWorker(input: str): ...     ''' ...     Worker that search for similar page contents from Wikipedia. Useful when you need to get holistic knowledge about people, places, companies, historical events, or other subjects. The response are long and might contain some irrelevant information. Input should be a search query. ... ...     Args: ...         input (str): search query. ...     ''' ...     try: ...         evidence = wikipedia.page(input).content ...         evidence = evidence.split("\\n\\n")[0] ...     except wikipedia.PageError: ...         evidence = f"Could not find [{input}]. Similar: {wikipedia.search(input)}" ...     except wikipedia.DisambiguationError: ...         evidence = f"Could not find [{input}]. Similar: {wikipedia.search(input)}" ...     return evidence ... >>> @fc_register("tool") >>> def LLMWorker(input: str): ...     ''' ...     A pretrained LLM like yourself. Useful when you need to act with general world knowledge and common sense. Prioritize it when you are confident in solving the problem yourself. Input can be any instruction. ... ...     Args: ...         input (str): instruction ...     ''' ...     llm = lazyllm.OnlineChatModule(source="glm") ...     query = f"Respond in short directly with no extra words.\\n\\n{input}" ...     response = llm(query, llm_chat_history=[]) ...     return response ... >>> tools = ["WikipediaWorker", "LLMWorker"] >>> llm = lazyllm.TrainableModule("GLM-4-9B-Chat").deploy_method(lazyllm.deploy.vllm).start()  # or llm = lazyllm.OnlineChatModule(source="sensenova") >>> agent = ReWOOAgent(llm, tools) >>> query = "What is the name of the cognac house that makes the main ingredient in The Hennchata?" >>> res = agent(query) >>> print(res) ' Hennessy ' """ def  __init__(self, llm: Union[ModuleBase, None] = None, tools: List[Union[str, Callable]] = [], *, plan_llm: Union[ModuleBase, None] = None, solve_llm: Union[ModuleBase, None] = None, return_trace: bool = False, stream: bool = False): super().__init__(return_trace=return_trace) assert (llm is None and plan_llm and solve_llm) or (llm and plan_llm is None), 'Either specify only llm \ without specify plan and solve, or specify only plan and solve without specifying llm, or specify \ both llm and solve. Other situations are not allowed.' assert tools, "tools cannot be empty." self._planner = (plan_llm or llm).share(stream=dict( prefix='\nI will give a plan first:\n', prefix_color=Color.blue, color=Color.green) if stream else False) self._solver = (solve_llm or llm).share(stream=dict( prefix='\nI will solve the problem:\n', prefix_color=Color.blue, color=Color.green) if stream else False) self._name2tool = ToolManager(tools, return_trace=return_trace).tools_info with pipeline() as self._agent: self._agent.planner_pre_action = self._build_planner_prompt self._agent.planner = self._planner self._agent.parse_plan = self._parse_plan self._agent.woker = self._get_worker_evidences self._agent.solver_pre_action = self._build_solver_prompt | bind(input=self._agent.input) self._agent.solver = self._solver   def  _build_planner_prompt(self, input: str): prompt = P_PROMPT_PREFIX + "Tools can be one of the following:\n" for name, tool in self._name2tool.items(): prompt += f"{name}[search query]: {tool.description}\n" prompt += P_FEWSHOT + "\n" + P_PROMPT_SUFFIX + input + "\n" globals['chat_history'][self._planner._module_id] = [] return prompt   def  _parse_plan(self, response: str): LOG.debug(f"planner plans: {response}") plans = [] evidence = {} for line in response.splitlines(): if line.startswith("Plan"): plans.append(line) elif line.startswith("#") and line[1] == "E" and line[2].isdigit(): e, tool_call = line.split("=", 1) e, tool_call = e.strip(), tool_call.strip() if len(e) == 3: evidence[e] = tool_call else: evidence[e] = "No evidence found" return package(plans, evidence)   def  _get_worker_evidences(self, plans: List[str], evidence: Dict[str, str]): worker_evidences = {} for e, tool_call in evidence.items(): if "[" not in tool_call: worker_evidences[e] = tool_call continue tool, tool_input = tool_call.split("[", 1) tool_input = tool_input[:-1].strip("'").strip('"') # find variables in input and replace with previous evidences for var in re.findall(r"#E\d+", tool_input): if var in worker_evidences: tool_input = tool_input.replace(var, "[" + worker_evidences[var] + "]") tool_instance = self._name2tool.get(tool) if tool_instance: worker_evidences[e] = tool_instance(tool_input) else: worker_evidences[e] = "No evidence found"   worker_log = "" for idx, plan in enumerate(plans): e = f"#E{idx+1}" worker_log += f"{plan}\nEvidence:\n{worker_evidences[e]}\n" LOG.debug(f"worker_log: {worker_log}") return worker_log   def  _build_solver_prompt(self, worker_log, input): prompt = S_PROMPT_PREFIX + input + "\n" + worker_log + S_PROMPT_SUFFIX + input + "\n" globals['chat_history'][self._solver._module_id] = [] return prompt   def  forward(self, query: str): return self._agent(query)`



 |

Bases: `[ModuleBase](https://docs.lazyllm.ai/zh-cn/latest/API%20Reference/module/#lazyllm.module.ModuleBase "            lazyllm.module.ModuleBase")`

IntentClassifier 是一个基于语言模型的意图识别器，用于根据用户提供的输入文本及对话上下文识别预定义的意图，并通过预处理和后处理步骤确保准确识别意图。

Parameters:

*   **`llm`** –

    用于意图识别的语言模型对象，OnlineChatModule或TrainableModule类型

*   **`intent_list`** (`list`, default: `None` ) –

    包含所有可能意图的字符串列表。可以包含中文或英文的意图。

*   **`prompt`** (`str`, default: `''` ) –

    用户附加的提示词。

*   **`constrain`** (`str`, default: `''` ) –

    用户附加的限制。

*   **`examples`** (`list[list]`, default: `[]` ) –

    额外的示例，格式为 `[[query, intent], [query, intent], ...]` 。

*   **`return_trace`** (`(bool, 可选)`, default: `False` ) –

    如果设置为 True，则将结果记录在trace中。默认为 False。


Examples:

`[](#__codelineno-0-1)>>> import  lazyllm [](#__codelineno-0-2)>>> from  lazyllm.tools  import IntentClassifier [](#__codelineno-0-3)>>> classifier_llm = lazyllm.OnlineChatModule(source="openai") [](#__codelineno-0-4)>>> chatflow_intent_list = ["Chat", "Financial Knowledge Q&A", "Employee Information Query", "Weather Query"] [](#__codelineno-0-5)>>> classifier = IntentClassifier(classifier_llm, intent_list=chatflow_intent_list) [](#__codelineno-0-6)>>> classifier.start() [](#__codelineno-0-7)>>> print(classifier('What is the weather today')) [](#__codelineno-0-8)Weather Query [](#__codelineno-0-9)>>> [](#__codelineno-0-10)>>> with IntentClassifier(classifier_llm) as ic: [](#__codelineno-0-11)>>>     ic.case['Weather Query', lambda x: '38.5°C'] [](#__codelineno-0-12)>>>     ic.case['Chat', lambda x: 'permission denied'] [](#__codelineno-0-13)>>>     ic.case['Financial Knowledge Q&A', lambda x: 'Calling Financial RAG'] [](#__codelineno-0-14)>>>     ic.case['Employee Information Query', lambda x: 'Beijing'] [](#__codelineno-0-15)... [](#__codelineno-0-16)>>> ic.start() [](#__codelineno-0-17)>>> print(ic('What is the weather today')) [](#__codelineno-0-18)38.5°C`

Source code in `lazyllm/tools/classifier/intent_classifier.py`

|  |

``class  IntentClassifier(ModuleBase):
 """IntentClassifier 是一个基于语言模型的意图识别器，用于根据用户提供的输入文本及对话上下文识别预定义的意图，并通过预处理和后处理步骤确保准确识别意图。   Arguments:
 llm: 用于意图识别的语言模型对象，OnlineChatModule或TrainableModule类型 intent_list (list): 包含所有可能意图的字符串列表。可以包含中文或英文的意图。 prompt (str): 用户附加的提示词。 constrain (str): 用户附加的限制。 examples (list[list]): 额外的示例，格式为 `[[query, intent], [query, intent], ...]` 。 return_trace (bool, 可选): 如果设置为 True，则将结果记录在trace中。默认为 False。     Examples:
 >>> import lazyllm >>> from lazyllm.tools import IntentClassifier >>> classifier_llm = lazyllm.OnlineChatModule(source="openai") >>> chatflow_intent_list = ["Chat", "Financial Knowledge Q&A", "Employee Information Query", "Weather Query"] >>> classifier = IntentClassifier(classifier_llm, intent_list=chatflow_intent_list) >>> classifier.start() >>> print(classifier('What is the weather today')) Weather Query >>> >>> with IntentClassifier(classifier_llm) as ic: >>>     ic.case['Weather Query', lambda x: '38.5°C'] >>>     ic.case['Chat', lambda x: 'permission denied'] >>>     ic.case['Financial Knowledge Q&A', lambda x: 'Calling Financial RAG'] >>>     ic.case['Employee Information Query', lambda x: 'Beijing'] ... >>> ic.start() >>> print(ic('What is the weather today')) 38.5°C """ def  __init__(self, llm, intent_list: list = None, *, prompt: str = '', constrain: str = '', attention: str = '', examples: list[list[str, str]] = [], return_trace: bool = False) -> None: super().__init__(return_trace=return_trace) self._intent_list = intent_list or [] self._llm = llm self._prompt, self._constrain, self._attention, self._examples = prompt, constrain, attention, examples if self._intent_list: self._init()   def  _init(self): def  choose_prompt(): # Use chinese prompt if intent elements have chinese character, otherwise use english version for ele in self._intent_list: for ch in ele: # chinese unicode range if "\u4e00" <= ch <= "\u9fff": return ch_prompt_classifier_template return en_prompt_classifier_template   example_template = '\nUser: {{{{"human_input": "{inp}", "intent_list": {intent}}}}}\nAssistant: {label}\n' examples = ''.join([example_template.format( inp=input, intent=self._intent_list, label=label) for input, label in self._examples]) prompt = choose_prompt().replace( '{user_prompt}', f' {self._prompt}').replace('{attention}', self._attention).replace( '{user_constrains}', f' {self._constrain}').replace('{user_examples}', f' {examples}') self._llm = self._llm.share(prompt=AlpacaPrompter(dict(system=prompt, user='${input}') ).pre_hook(self.intent_promt_hook)).used_by(self._module_id) self._impl = pipeline(self._llm, self.post_process_result)   def  intent_promt_hook( self, input: Union[str, List, Dict[str, str], None] = None, history: List[Union[List[str], Dict[str, Any]]] = [], tools: Union[List[Dict[str, Any]], None] = None, label: Union[str, None] = None, ): input_json = {} if isinstance(input, str): input_json = {"human_input": input, "intent_list": self._intent_list} else: raise ValueError(f"Unexpected type for input: {type(input)}")   history_info = chat_history_to_str(history) history = [] input_text = json.dumps(input_json, ensure_ascii=False) return dict(history_info=history_info, input=input_text), history, tools, label   def  post_process_result(self, input): input = input.strip() return input if input in self._intent_list else self._intent_list[0]   def  forward(self, input: str, llm_chat_history: List[Dict[str, Any]] = None): if llm_chat_history is not None and self._llm._module_id not in globals["chat_history"]: globals["chat_history"][self._llm._module_id] = llm_chat_history return self._impl(input)   def  __enter__(self): assert not self._intent_list, 'Intent list is already set' self._sw = switch() self._sw.__enter__() return self   @property def  case(self): return switch.Case(self)   @property def  submodules(self): submodule = [] if isinstance(self._impl, switch): self._impl.for_each(lambda x: isinstance(x, ModuleBase), lambda x: submodule.append(x)) return super().submodules + submodule   # used by switch.Case def  _add_case(self, cond, func): assert isinstance(cond, str), 'intent must be string' self._intent_list.append(cond) self._sw.case[cond, func]   def  __exit__(self, exc_type, exc_val, exc_tb): self._sw.__exit__(exc_type, exc_val, exc_tb) self._init() self._sw._set_conversion(self._impl) self._impl = self._sw``



 |