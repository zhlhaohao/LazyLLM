[构建Data Agent：企业应用中基于大模型的数据分析及方案【中】 - 今日头条](https://www.toutiao.com/article/7305742482497864192/?log_from=1714d1365217b_1735222476571) 

 **专注LLM深度应用，关注我不迷路**

在上篇中，我们探讨了在企业应用中基于自然语言的交互式数据分析的业务驱动力与场景：作为现有数据分析类应用或商业BI工具的一个更简单、友好、且易于交互（特别是针对业务决策人员）的工具（Data-Agent），与现有应用形成有效互补。针对这样的场景，提出了当前基于大模型实现的三种基础方案设想：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-axegupay5k/7a08f9da8ba2492bb0fbd15337c28e78~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=xTmNldhaZtcCxaY4P%2FKIAY8gy68%3D)

今天我们一起来深入text2SQL的方案，也可以称作NL2SQL（自然语言转SQL，SQL又称作结构化查询语言，是数据库交互的一种标准化语言，几乎存在于所有以数据为中心的企业应用中）。

**Text2SQL**，简单的说，就是把你说的自然语言转化为数据库能够听懂的SQL，然后通过数据库的“语言”与它对话，获得数据查询或统计结果。

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/2810aa77478d496387f3308993ac8373~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=DM5k6XwB2V%2F60T8ak%2FObj4azPms%3D)

> text2SQL并不是一个在大模型以后才出现的话题。早在大语言模型横空出世之前已经有大量专注于此的机器学习研究项目，只是随着大语言模型的出现，其强大的自然语言理解推理能力让text2SQL得到大力的推进。

从图中可以看出，text2SQL的实现原理非常简单，其核心就在于**如何把自然语言组装成Prompt，并交给LLM转化成SQL。** 我们不妨看一下OpenAI公司在官网给出的一个标准的chatGPT做自然语言转SQL的例子：

```
System


Given the following SQL tables, your job is to write queries given a user’s request.

CREATE TABLE Orders (
OrderID int,
CustomerID int,
OrderDate datetime,
OrderTime varchar(8),
PRIMARY KEY (OrderID)
);

...此处省略其他表...


Write a SQL query which computes the average total order value for all orders on 2023-04-01.
```

没错，看上去就是一个简单的“咒语”，就可以完成这个貌似复杂的工作。当然，在实际使用中，可能需要根据你所使用的大模型来做适当调整。但不管组织的形式如何，text2SQL的Prompt基本上就是几个部分组成：

*   **指令（Instruction）**：比如，“你是一个SQL生成专家。请参考如下的表格结构，直接输出SQL语句，不要多余的解释。”
*   **数据结构（Table Schema）**：类似于语言翻译中的“词汇表”。即需要使用的数据库表结构，由于大模型无法直接访问数据库，你需要把数据的结构组装进入Prompt，这通常包括表名、列名、列的类型、列的含义、主外键信息。
*   **用户问题（Questions）**：自然语言表达的问题，比如，“统计上个月的平均订单额”。
*   **参考样例（Few-shot）**：这是一个可选项，当然也是提示工程的常见技巧。即指导大模型生成本次SQL的参考样例。
*   **其他提示（Tips）：** 其他你认为有必要的指示。比如要求生成的SQL中不允许出现的表达式，或者要求列名必须用“table.column"的形式等。

实现一个text2SQL的原型非常简单，但是在实际应用时它可能并不会像你期待的那样表现良好，因为它首先有一个关键的问题：**当前****AI模型输出SQL的准确性还远无法达到人类工程师的输出精度。** 深度学习的AI模型预测本身就有置信度的问题，无法确保绝对可靠性，这一点在大语言模型依然存在。当然，**输出的不确定性也是目前限制大模型在关键企业系统应用最大的障碍。** 

> 除了模型自身的知识能力以外，还有一些客观原因：
> 
> \* 自然语言表达本身的歧义性，而SQL是一种精确编程语言。因此在实际应用中，可能会出现无法理解，或者错误理解的情况。比如，“谁是这个月最厉害的销售”，那么AI是理解成订单数量最多，还是订单金额最大呢？
> 
> \* 尽管你可以通过Prompt输入数据结构信息帮助AI模型来理解，但有时候AI可能会由于缺乏外部行业知识导致错误。比如，“分析去年的整体客户流失率？”，那么如果AI缺乏对“客户流失率”的理解，自然就会出错或者编造。

**Text2SQL的方案在企业应用中还会面临两个严重的挑战**：

*   **可能会出现正常运行的“假象”**

即**正常的完成了任务，但实际结果是错误的**。由于text2SQL是直接输出用于数据库访问的语句，理论上来说，只要不存在基本的语法错误，就可以执行成功，即使转换的SQL在语义上是错误的！这与text2API的区别在于：API由于有很严格的结构化输入输出规范与校验，因此如果模型转换错误，很大概率会导致API调用的异常，使用者能够获得错误反馈（当然也存在“假象”的可能）。

比如这样一个问题，LLM的两个输出都可以正常执行，但是第二个显然是错误的。而且这样的错误对于使用者来说，很可能是难以察觉的：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/d650ba1883c14764a14efc9c69500e42~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=IubsA4HxtKAiE5gUHIEo8iiiJXs%3D)

**所**以，这个问题其实来自于text2SQL输出正确性的评估困难。这种text2SQL输出语义准确性衡量的复杂性本质上来自于这样一个事实：**判断AI输出的一段代码是否正确，要比判断一个选择题答案是否正确，或者一段字符串的相似度要复杂的多**。

下面这个来自于text2SQL模型的输出评估工具TestSuiteEval中的例子：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/8aec29543d1b4cde9c14c3726fd78d64~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=D1yRiUWaNnGdYmcCQg1Rw8n6Teg%3D)

其中Gold代表正确答案，predicted1和2代表模型的两个输出，这里正确的是predicted2，错误的是predicted1，我们来看两种评估方法：

*   如果用SQL执行结果来判断：Predicted1的结果和正确SQL的结果很可能一样，但实际上Predicted1的SQL是错误的。
*   如果直接对比输出的SQL：由于Predicted2和正确的SQL不完全一致，你可能判断它是错误的，但其实Predicted2的SQL在这个场景下是正确的。

这就是评估text2SQL模型输出正确性的复杂所在：**你既不能用输出SQL的执行结果来判断，也不能简单的把输出SQL与标准答案对比来判断。** 

*   **企业应用的特点会加大错误输出的概率**

我们在上篇中曾经总结过企业应用分析场景的一些特点：

*   真实企业应用数据库的结构要远比测试应用复杂。
*   真实企业应用的分析逻辑会更复杂。在企业应用即使有几百行的一个SQL统计语句为了生成一个报表也不用奇怪。
*   真实企业应用不仅有正确性的要求，还有效率即响应性能的要求，特别对于大型的数据仓库。

那么大语言模型在应对这些问题时是否有很好的解决方案呢？遗憾的是，**从当前的一些模型测试结果看，让大语言模型能够在这些场景下完全胜任，达到人类工程师的精度是不现实的**。但是我们可以在几个方面考虑其优化，以实现在部分场景下的优先可用。

*   **选择或者微调合适的大模型**
*   **提示词工程优化**
*   **应用场景的限制与设计**

大模型自身的优化无非是两种选择：选用最强大的通用模型（比如GPT-4）或者通过SFT（高效微调）训练出更适合自身下游任务的模型。那么如何来衡量text2SQL模型呢？前文我们已经说过，评估输出SQL是否正确是一个复杂的工程，好在已经有较多的研究项目有现成的评估结果可以参考。

**【Spider基准测试】** 

Spider是一个被广泛用于评估text2SQL模型与任务的数据集。你可以在官方网站直接下载这个数据集，然后用来评估你选择或者训练的模型。这个数据集包含了1万多个自然语言的问题和相关的SQL语句，以及用来运行这些SQL的200多个数据库，横跨了100多个应用领域。你甚至可以把模型和测试代码提交给官方，官方会在一个不公开的测试集上测试你的模型，并公开结果排名。

目前Spider公开的官方最新测试结果，注意Model部分不仅列出了大模型，也包括可能的提示工程技术（比如DAIL-SQL，参考下一部分）：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/85604601621e4da7b9ffbb8dcf07b584~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=77YxAmyInAtVNaaXhKesB0dD%2BV0%3D)

图片来自Spider官网

**【BIRD基准测试】** 

BIRD是阿里达摩院联合香港大学一起推出的针对text2SQL的测试数据集。其作用与Spider类似，但是相对于Spider更专注于学术研究，BIRD则更加考虑了真实应用中的数据库中信息的复杂性，且考虑了模型生成的SQL运行效率。BIRD也包含了约12000多个自然语言与SQL，涵盖了约37个专业领域的90多个数据库。与Spider类似，你也可以提交测试代码与模型给官方获得官方测试结果。最新排名如下：

**注意到，在这个相对复杂的测试数据集下，大模型的最高分也只有60.71，离人类能力的92.96分还有相当的距离！**

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/fc573fc1cece4ced9b55bf12edbe4514~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=5AYfS4QS7uIC5DO4LFIThF9aOz8%3D)

来自BIRD官网

**从以上两个测试结果看，在通用大模型领域，GPT-4仍然是“遥遥领先”。** 

**【微调模型】** 

在实际企业应用中由于数据安全或者网络安全的限制，你可能面临必须使用私有大模型的挑战。测试结果表明，如果直接使用当前开源的各类大语言模型，在text2SQL的任务上表现并不佳，所以SFT（高效微调）就成为常见的手段。在这里我们主要推荐两个开源的text2SQL微调项目做参考。

**DB-GPT-Hub**

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/136fadccbaf64a1ab019fcf525d8f8b1~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=5%2F05PjuIBJWFDrxImRiNbZPzxak%3D)

https://github.com/eosphoros-ai/DB-GPT-Hub/tree/main

这是一个专注于LLM在text2SQL应用任务上微调的实验性项目，提供了大量的公开数据集、不同的微调工具与方法，支持当前主流的开源模型上的text2SQL任务的微调与结果评估。你可以在其基础上使用公开或者私有的数据集进行微调并评估效果。根据该项目的公开结果，当前已经完成微调的模型在Spider数据集的测试结果对比如下，**可以看到meta的开源代码模型CodeLlama-13b有不错的表现**。

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/05a2b2c3b919435ab745094b16efc611~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=22NPOFhh9kwykgzAZfh3HbHcELk%3D)

图片来自DB-GPT Github项目

**SQLCoder**

这也是一个基于CodeLlama微调的text2SQL任务大模型，根据其公开的测试结果，具有与GPT-4不相上下的表现。

![](https://p26-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/5feed3b03a774fd7834f2cf97c8ae8fa~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=Pvff202aTrF8cRXtcEbwsSwCTnc%3D)

https://github.com/defog-ai/sqlcoder

官方公布的其内部评估框架上的测试结果为：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/c8c9f1f6d3e14efabf3e7bddf8965576~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=0tsI%2FMezGeaJBTY41CJ6l8b86WA%3D)

图片来自SQLCoder Github项目

**从以上项目的测试结果看，当前codeLlama-13b与SQLCoder-34b可能是开源领域比较合适的text2SQL的模型选择。** 

在上面的基准测试中，我们也可以看到，大部分的测试结果都结合了类似DAIN-SQL,DIN-SQL,C3-SQL这样的说明，这其实表示的是在模型测试时采用的一种生成SQL的Prompt工程方案，因此优化的提示工程与优秀的大模型结合是能够获得最高测试结果的方法。我们这里介绍两种提示工程的方案。

**DAIN-SQL**

阿里推出的一种针对LLM在text2SQL应用的一种提示工程优化技术。在Spider基准测试中取得当时的最高分86.6分，在更高难度的BIRD数据集测试中也取得了57.41分。其优化方法本质上是：**在传统的text2SQL的提示中通过注入一些相似的样例，利用LLM的上下文学习能力，以提高输出SQL的精度。** 

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/33d6283872124ba683426231e23e02cd~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=VOCHv1iQR3AjjXRlgvYP8BDsOsY%3D)

那么具体如何选择样例呢？其介绍的原理是通过用户的提问“骨架”找到相似的问句；再通过预生成的SQL“骨架”找到相似的SQL，进而通过算法进行相似度排序，取出最相似的样例（包括提问与SQL），组装到Prompt。

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/02a8c00faa2747f09f7af6ee2ebb8f01~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=OrVroU0rwXL83BWWehnvCvROleM%3D)

图片来自魔搭社区

当然，这种方法在实际企业应用中可能会存在一个问题：大量的备选样例从哪里来？利用现有的一些测试数据集可能是一个方法；另外一种可能是如果企业针对text2SQL场景进行模型微调，那么需要准备大量的训练数据集也可以用来作为备选案例。总的来说，这种方法的门槛还是偏高。

**C3-SQL**

浙江大学推出一种针对text2SQL场景的提示工程优化方法，与DAIL-SQL不同的是，这是一种zero-shot的提示方法（零样例），即不在prompt增加样例，而是通过三个方面的提示或优化来提升输出的质量：

**Clear Prompting**：通过对Prompt提供更清晰的层次，并只嵌入必要的数据结构信息，来优化提示。一个重要的思想是，在构建Prompt之前，先通过大语言模型来分析本次输入最可能相关的数据实体(table)及其列(column)信息，即仅召回本次最可能用到的table和column，然后组装到Prompt，而不是把整个数据库的结构全部组装进入。

**Claibration Bias Prompting：** 通过在上下文信息中嵌入一些偏差提示，可以简单的理解为指示大模型在一些场景下需要遵循的一些规则或者“注意点”。

**Consistent Output:** 这是一种输出处理方式，也是解决大模型输出不确定性的一种方案。可以解释为：**让大模型输出多次SQL，然后根据输出的SQL执行结果进行“投票”。** 比如让LLM输出四次SQL，其中三个的执行结果都是一致的，另一个结果不一致，那么就认为这三次的输出是正确的。

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/7afeba610b6f452380a2cf1ca5c57564~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827276&x-signature=JgNu1L6yQsDTzQ8etXGSRGGJ638%3D)

图片来自C3-SQL论文

具体到实际的企业应用中，前面两个C相对更实用，即通过精简注入的数据结构与增加更多的“注意点”来优化提示，可以让有效输出的概率更高。针对最后一点，可以在数据量较少的场景下使用，由于需要多次执行SQL，并根据结果来投票“选举”最佳结果，可能会造成大量的无用性能损耗。

由于大语言模型的输出的不确定性与一些自然语言交互的客观原因，在text2SQL任务上存在一定的失败或者错误概率。一些测试结果也表明，即使是最先进的模型结合优化的提示技术，其表现也离人类有较大差距。因此除了在模型自身以及交互的提示词方面优化外，我们在实际应用中也可以针对自身的情况在应用场景与设计等方面做一定的考虑：

*   **优先应用在特定场景。** 比如企业BI中的即席查询，尝试引入text2SQL的实现方案，由于即席查询的特点是条件自由变化，而相关的数据结构并不会太复杂，因此非常适合用自然语言来灵活生成查询语句。
*   **配合使用其他的交互式分析方案。** 比如无法通过单次SQL交互即可完成的统计分析任务，正如我们在上篇所说，如果有着复杂的中间数据处理逻辑，可以考虑采用text2API的方式来实现。
*   **从较小的分析主题开始。** 如果企业应用底层数据实体的数量过多，可能会导致Prompt过大并超出最大context大小，这需要在组装Prompt时进行设计，即“按需”注入相关数据实体的schema信息。这可以参考数据仓库的按主题分析的方法，并选择较小的分析主题开始实践。

**总的来说，text2SQL是一种看上去最简单也最直接的大模型在数据分析的应用技术方案。但是在真实应用场景中，由于企业应用的数据复杂性以及对可靠性的更高要求，需要有大量的模型优化工作与针对性的设计，否则可能很难达到预期的效果。** 

参考：

*   https://arxiv.org/pdf/1809.08887.pdf
*   https://arxiv.org/pdf/2308.15363.pdf
*   https://arxiv.org/pdf/2307.07306.pdf
*   https://arxiv.org/pdf/2305.03111.pdf
*   https://bird-bench.github.io/?spm=a2c6h.12873639.article-detail.8.8dac7c40VkErOU
*   https://github.com/defog-ai/sqlcoder
*   https://arxiv.org/abs/2010.02840

**私信“交流”**

**一起探讨AI大模型的应用实践**