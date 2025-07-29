[RAGFlow Agent 实践——构建 AI 资讯推送助手](https://mp.weixin.qq.com/s/oa4M7pXIqG2wkrKCCg9D8Q) 

 对于热爱 AI 行业的你，在查阅行业新闻时往往消耗了大量时间。今天将给大家介绍如何利用 RAGFlow 的 Agent 功能，创建一个 AI 资讯推送助手。这个助手能提取网络资讯并进行总结概括，让你轻松掌握行业动态。

RAGFlow 是一款基于深度文档理解构建的开源 RAG（Retrieval-Augmented Generation）引擎。RAGFlow 可以为不同规模的企业及个人提供一套精简的 RAG 工作流程，结合大语言模型（LLM）针对用户各类不同的复杂格式数据提供可靠的问答以及有理有据的引用。Agent 功能是利用一系列节点设计标准工作流程，实现稳定输出，提升系统的可解释性和容错率。

AI资讯推送助手介绍：支持分步抓取资讯的时间、标题和内容，并以总结概括的形式返回。在初始阶段，该助手将指导用户进行提问。接收到用户提问后，助手会对问题进行分类处理：若问题属于AI相关领域，助手将提取问题中的关键词并启动网络搜索；若问题不属于AI领域的范畴，助手将提醒用户进行AI范围内的提问。助手在进行网络搜索后，会分步提取发布时间、标题和内容，并进行内容的总结概括。随后，助手将利用模板转换模块将内容按照固定格式进行输出。本助手旨在帮助用户查询AI行业的相关资讯，并通过总结概括将关键内容推送给用户，减少用户的阅读成本。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXFJBDHWxVF5NHpGKwLVgLytnYvtCIhJ80XR298Od900oAExlFsezvibg/640?wx_fmt=png&from=appmsg)

先展示一下本次搭建将会用到的节点：

| 

生成回答

 | 

利用大模型生成内容，可以引用变量，可以通过调整相关参数来调试效果。

 |
| 

对话

 | 

承担两个作用，既可输出上一节点的内容在用户对话面板上，同时也接收用户的反馈作为新变量加入后续的运算。

 |
| 

问题分类

 | 

此节点主要应用大模型的理解能力进行意图识别，可以设置名称、描述和示例。

 |
| 

关键词

 | 

从输入变量中抽取关键词并输出，可以用Top N指定关键词数量。

 |
| 

网络搜索

 | 

从相应网站获取搜索结果。Top N 指定您需要调整的搜索结果数量。

 |
| 

模板转换

 | 

可用于排版各种组件的输出。

 |
| 

集线器

 | 

可用于连接多个下游组件。它接收来自上游组件的输入并将其传递给每个下游组件。

 |

正式开始搭建：

1\. 首先需要引入一个开始节点，通常按需求设置用户刚连接时推送助手的欢迎词，可以设置引导提问；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXDzLmYQEhbk5QBictWAKxiao5Ew3YiaiaJoP0cv6LSf0CSnpah9YaxvAWow/640?wx_fmt=png&from=appmsg)

2\. 使用对话节点给出开场白，同时等待用户回复，获取用户的问题，我们把这个节点设置为”人机交互“，方便后续调用；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbX2HwWN3GwEFVMMQibFPedCiaHOtsI5Pv9AQywomkcJQfKbaQUbdYRjl9g/640?wx_fmt=png&from=appmsg)

在 RAGFlow 的 Agent 编排中，对话节点起到控制对话流程的作用，既可以把之前 Agent 的运算结果输出到聊天面板，同时也可以获取用户的反馈作为新变量加入后续的运算；

3\. 使用问题分类节点，设置两种情况：a. AI相关问题，b. 其他问题；加入描述和示例，选择好大模型，并设置输入为前节点“人机交互”；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXoxqqQFPjjuzQWiasICkqok2ubdnYymcRDSGHvYctP4XVCKpwF86VP7Q/640?wx_fmt=png&from=appmsg)

4 开始编排 a 情况“AI相关问题”的后续路径：

4.1 为了提高后续网络搜索的效果，可以引入一个关键词抽取节点，这里采用关键词节点完成该功能，它负责利用大模型从用户问题中抽取关键词。使用这个节点，可以用 Top N 指定关键词数量，让大模型从用户的问题中抽取关键词；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbX6dnAZF4eo91ice2ib84bVJeRf36RjH9ovuibuHmabRQOYBicst7yEbzUwg/640?wx_fmt=png&from=appmsg)

4.2 在这里我们选取百度作为搜索网站，可通过调节 Top N 指定您需要调整的搜索结果数量；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXKyMoqTAIOYcYz5ic0y092sdtyQEuUhFtoickziaWLkw7jjoAy1jpg31bg/640?wx_fmt=png&from=appmsg)

RAGFlow 内部也提供了其他搜索网站模块，可以根据自身使用情况来调整搜索网站类型；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXz09iaaGN3rplvtN6ps4DcDquE3ibibWXFZY0dib7dJudeFEbhtf16Ih1Lw/640?wx_fmt=png&from=appmsg)

4.3 为了提高网络的检索效果，接下来我们采取分步提取，分别提取资讯的时间，标题，内容。在这里我们使用了集线器节点，它可以连接多个下游组件。它接收来自上游组件的输入并将其传递给每个下游组件；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbX6SVY92Ms385k1rubzKH4EUicmfqMVDh8u5AoJCEfblicO1uIJ8P4TiaYA/640?wx_fmt=png&from=appmsg)

4.3.1 引入一个发布时间提取节点，这里采用生成回答节点完成该功能，它负责利用大模型从资讯中抽取时间信息。使用这个节点，我们需要先设置引用变量，引用“资讯发布时间”这个节点的输出作为变量，因为需要其作为提示词的一部分输入给大模型，更利于大模型总结推送内容，我们把引用的变量命名为 time，然后设置好提示词。请注意，变量名需要被{}包裹；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXqicmDPGEV2ibIovCvw4YrDIPlNTdC4V41PMVubhdAic2XjLA0VI3vB5bQ/640?wx_fmt=png&from=appmsg)

4.3.2 接下来，我们引入一个标题提取节点，这里依旧采用生成回答节点完成该功能，它负责利用大模型从资讯中抽取标题内容。在这里，我们设置“标题内容”这个节点的输出作为变量，我们把引用的变量命名为 title，变量名依旧需要被{}包裹；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbX5GxSV3lONN2YibJibjwxGRn5u1wu3fR2hO38tmmK5BK6oLMcX4SbojWg/640?wx_fmt=png&from=appmsg)

4.3.3 与上面两步相同，我们引入一个具体内容提取节点。在这里，我们设置”内容“这个节点的输出作为变量，我们把引用的变量命名为content，设置提示词时，可以要求大模型对具体内容进行概括；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXu5d5ohiaVZCcvXPaXenIdZMIK0CdrJ6IbCYg4KoeutbVwRv4WgWbAqw/640?wx_fmt=png&from=appmsg)

4.4 需要让大模型生成回答，因此添加一个生成回答节点：选择大模型之后，添加三个变量：{time}来源于“时间提取”节点，{title}来源于“标题提取”节点，{content}来源于”内容提取“节点。然后编写提示词，让大模型结合三个变量进行回答；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXmibyXQI17Vp9EafuRNnwXy1KPNkADCEowj5wSLwibLj1lwpeOd715Vww/640?wx_fmt=png&from=appmsg)

4.5 为方便阅读，我们还需要规范资讯推送的格式，在这里我们引入“模板转换”节点来完成该功能。我们将{time}{title}{content}三个变量添加，并在内容里规定智能体的输出模板格式；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXn8IsY8icsCWbicXKfxAxHxUtXvrywvcfnp37Mdw2a5nPybLibLLEpNiaAA/640?wx_fmt=png&from=appmsg)

注意：在使用模板转换时，内容中直接将变量格式输入即可，不要添加其他内容，如“按以上格式输出”等；

到此，a 情况的第一轮对话完成。由于 RAGFlow 的 Agent 是支持循环路径的，因此可以直接连接开始的“人机交互”节点，并等待下一轮的问题；

4.6 资讯推送效果展示

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXW9wYqkN5KAkpqNOFS1icibDuF8Zup5hHibHCsdh6cRTrtFR1yEBwIK19g/640?wx_fmt=png&from=appmsg)

5 接下来我们开始编排 b 情况“无关问题”的后续路径：

5.1 我们引入一个问题引导节点，采用生成回答节点完成该功能。在这里，我们设置提示词，使其可以回复用户的不相关问题，同时引导用户回到AI相关问题的询问中；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXokFCWVZqOjkEszrzDqngaibRehulGic1emksoym3xYfvTTL09bYzTrwQ/640?wx_fmt=png&from=appmsg)

5.2 RAGFlow 的 Agent 是支持循环路径，我们将问题引导的节点连接到开始的“人机交互”节点，等待下一轮问题；

5.3 问题引导效果展示

![](https://mmbiz.qpic.cn/sz_mmbiz_png/tfic1yF9PPI9AtMJfPrLXyd4rs8sIBsbXh1C14g8GiariawPgfI5bD1mXYo8oAVN2IgIq1H9mNALSvicxNleSicFs8w/640?wx_fmt=png&from=appmsg)

总结：今天和大家一起学习了如何使用 RAGFlow 的 Agent 功能搭建一个资讯推送助手，其中介绍了生成回答，问题分类，网络搜索等7种节点的使用方法，掌握网络搜索节点的使用，能帮助你提升信息提取的能力；善用模板转换节点，您可以将内容格式化输出。RAGFlow 还有更多的功能等待您来挖掘，后续我们也会不断更新相关文章，带领大家一起学习和探索 RAGFlow 的更多可能性。欢迎大家持续关注 RAGFlow https://github.com/infiniflow/ragflow，在 GitHub 上给我们点亮⭐️。