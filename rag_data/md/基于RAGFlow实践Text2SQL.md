[基于RAGFlow实践Text2SQL](https://mp.weixin.qq.com/s/woWG5r9mEGjfX00XWjAAFg) 

 RAGFlow 0.10 版本发布，应广大社区用户要求，引入了Text2SQL特性。传统上Text2SQL依赖于对模型微调，而在企业场景中，经常会面临RAG/Agent 搭配 Text2SQL 的场景，这时如果再部署一个微调的大模型，势必会影响部署和维护成本。因此 RAGFlow 基于 RAG 也推出了 Text2SQL 功能，这样可以仅依赖现有的大模型即可提供 Text2SQL 能力，方便让Text2SQL 搭配其他RAG/Agent算子共同工作。

那么如何基于 RAG 来提供 Text2SQL 能力呢？工作流程可以参见下图：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPIibyAOr6ias4Dib1FrE9HAPHVFMp3YwtYrtF9aAMXGw6DKmcOMDQcZOR4u5dO0LOqlanViazibMeEQZYvg/640?wx_fmt=png&from=appmsg)

我们需要准备一个专门用于生成 Text2SQL 提示词的知识库，该知识库包含各类自然语言到 SQL 的样例数据。当用户向 RAGFlow 发起一个Text2SQL提问时，先到该知识库中进行搜索，找到相似结果后拼接成生成SQL的提示词，再把该提示词发给大模型，让大模型生成最终的SQL。该 SQL 可以直接用来查询数据库，如果返回结果出现错误，证明产生的 SQL 不对，那么需要继续调用大模型让它产生一个正确的SQL直到错误次数超过上限。

因此，Text2SQL依赖于Agent框架来实现多次交互任务的编排，在0.10.0 版本的RAGFlow中，Text2SQL被固化为内置的Agent算子，方便参与到整个用户侧的工作流中。在后续版本中，当返回结果出错后，以上的工作流程会做进一步调整，就是让人工介入输入正确的SQL，该SQL会被更新到知识库当中，方便未来的提问生成正确的SQL，如上图的虚线箭头所示意。

下边是在 RAGFlow 中使用 Text2SQL 的操作指南：

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/tfic1yF9PPIibyAOr6ias4Dib1FrE9HAPHVFTxJ7IXvibkUHS84DBziczT9XOpuRglcfPJHgT0R0lUZM487UShDibibw0Q/640?wx_fmt=gif&from=appmsg)

**如何在RAGFlow中使用Text2SQL**

1.  在RAGFlow Agent中创建DB Assistant 模板
    --------------------------------
    

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPIibyAOr6ias4Dib1FrE9HAPHVF64uAdGYjS5ZL5dEiaqVEiboB6X0DEtCrTskdHXyBayGPIhca1VZuSgsw/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPIibyAOr6ias4Dib1FrE9HAPHVFicVIPWXxCSgZOOvB5kE61DX0rDRo7GIIUyiaP1bFV1QuhTPPDicYDFYVw/640?wx_fmt=png&from=appmsg)

2.  配置Text2SQL 知识库
    --------------
    

在RAGFlow中需要提供三种知识库来确保Text2SQL结果的质量，分别是:DDL知识库 ，Q->SQL知识库，DB Description知识库。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPIibyAOr6ias4Dib1FrE9HAPHVFEWzJ1s0Zn28TdsyhJlMIlrWzOT9ibJWEjVHxf9ZLvbMMNxic7QkasOYQ/640?wx_fmt=png&from=appmsg)

DDL知识库：大语言模型生成SQL语句需要准确的数据库DDL数据，包含但不限于表结构，表字段信息等等，因此在DDL知识库中需要提供准确的所查询数据库的DDL数据，DDL知识库解析配置建议设置为如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPIibyAOr6ias4Dib1FrE9HAPHVFSPeG78a0eDWeXSZHf4ibPEFXeX5kQN8fqndJbGByvAyElibbyAzDWzXw/640?wx_fmt=png&from=appmsg)

DDL知识库数据参考：https://huggingface.co/datasets/InfiniFlow/text2sql/tree/main。

Q->SQL知识库：在Text2SQL生成过程中，对大语言模型提供samples往往能提高生成的SQL语句的质量，因此在Q->SQL知识库中需要提供自然语言->对应的SQL语句的samples，如果能够提供所查询的数据库Q->SQL的samples，则Text2SQL结果质量更高。Q->SQL知识库解析配置建议设置如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPIibyAOr6ias4Dib1FrE9HAPHVFO9HwzTHLQFWwE2n1XpMiavMP3Zwt6E8s5NUveGMLiaYGvTGTiaZV0EWjw/640?wx_fmt=png&from=appmsg)

Q->SQL知识库数据参考：https://huggingface.co/datasets/InfiniFlow/text2sql/tree/main

DB Description知识库：该知识库包含准确的所查询数据库的相关信息，包括但不限于数据库表的含义，数据库表中不同字段所代表的含义，依据详细的数据库各项描述信息，大语言模型能够更加精准的将用户的问题转换为SQL语句。DB Description知识库解析配置建议设置如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPIibyAOr6ias4Dib1FrE9HAPHVF75iaf0aa3d8jJlQsO5SNj2TDyJ8DFiasjQXyYY9oFu8ZKsbpCjXT8wZA/640?wx_fmt=png&from=appmsg)

DB Description知识库数据参考：

https://huggingface.co/datasets/InfiniFlow/text2sql/tree/main

3.  配置数据库
    -----
    

将所需查询的数据库各项参数在Execute SQL中进行配置，包括：

1)数据库的类型(目前支持Mysql，PostgresDB和MariaDB)

2)数据库名称

3)数据库用户名

4)数据库IP地址

5)数据库端口号

6)数据库密码

**配置完成后可以点击Test按钮来测试是否连接成功****。** 

Loop参数：RAGFlow中Text2SQL具备自动反思迭代的能力。针对用户的问题，如果大语言模型生成的SQL查询成功则会直接将结果进行返回。如果大语言模型生成的SQL查询失败，则RAGFlow Text2SQL则会针对数据库查询返回的错误信息和SQL语句进行自动更正进行再次查询，该过程(查询失败->更正SQL语句->再次查询)最大迭代次数则为Loop参数的值，如果迭代次数超过Loop值，查询结果仍然失败，则程序自动结束Text2SQL过程，请优化用户问题或知识库数据再次尝试。

TopN参数：数据库查询中往往包含大量的记录，该参数用于限制所返回的记录数量。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPIibyAOr6ias4Dib1FrE9HAPHVFDicvOVdv4YibAULnQcrh8fxmy9prSnzvuDTFhC6UvxNAFBlKGJFG88xQ/640?wx_fmt=png&from=appmsg)

4.  Go
    --
    

接下来点击Run就可以执行了。

**常见问题**

1.  Database Connection Failed!
    ---------------------------
    

数据库连接失败，需要检查Execute SQL组件中数据库各项参数是否正确，确保部署RAGFlow的机器按照所填的信息是能够连接到数据库的，点击test进行测试数据库是否能够连接成功。

2.  SQL statement not found!
    ------------------------
    

这意味着Text2SQL不能将用户问题转化为SQL语句，对于LLM来说可能所需要的咨询太少或不完整，可丰富上面提到的三个知识库。

3.  No record in the database!
    --------------------------
    

表示该SQL查询从数据库表中查询到的记录数为0，有可能过滤条件过为严苛，或数据库该表为空表。

4.  Maximum loop time exceeds. Can't query the correct data via SQL statement.
    --------------------------------------------------------------------------
    

该问题表示Text2SQL对用户问题转化之后对应的SQL语句不能正确的从数据库中进行查询，请检查数据库中是否包含该查询对应的内容，用户问题是否合适，Generate SQL Statement LLM 组件和Fix SQL Statement LLM组件生成的SQL语句是否正确。