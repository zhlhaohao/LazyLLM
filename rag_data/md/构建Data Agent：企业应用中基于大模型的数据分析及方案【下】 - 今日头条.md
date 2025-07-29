[构建Data Agent：企业应用中基于大模型的数据分析及方案【下】 - 今日头条](https://www.toutiao.com/article/7307604998014485029/?log_from=b4e0dbb69df94_1735222666648) 

 **专注LLM深度应用，关注我不迷路**

本文我们继续探讨在企业应用中基于LLM的交互式数据分析的另外一种基础技术方案 - Code Interpreter，也就是Text2Code。

很多人都使用过ChatGPT的一个在线工具Code Interpreter，现在已经作为其GPTs Builder构建私有GPT最重要的一个工具存在。这个工具的基本原理说起来很简单：**借助于大模型的代码生成能力，在理解客户自然语言描述的问题基础上，通过输出代码（常见的是Python）并自动迭代执行与调整，最终完成客户任务。** 由于其非常擅长处理数据分析任务（但不限于此），因此在ChatGPT中该工具后来改名为高级数据分析。简单的说，这就是一种文本转代码（**Text2Code**）的自动化方案。

![](https://p3-sign.toutiaoimg.com/tos-cn-i-axegupay5k/08a2b8e3b7a34e8793d9c24b5f9890db~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827466&x-signature=h7afEOcmB3SJwPDASsbDgEgdmg0%3D)

在完成数据分析任务时，通常你可以上传一个数据文件给他，然后要求Code Interpreter完成相关任务，其任务能力主要包括：

*   **加载与读取文件内容，数据结构识别（Data Profiling）**
*   **数据质量检查，比如一致性、缺失值处理等**
*   **数据建模，如构建BI常见的多维星型模型**
*   **数据分析与洞察，如给出常见的KPI或回归分析**
*   **数据可视化，通过合适的图表对分析结果做展示**

以Python语言代码为例，Code Interpreter一般会借助于其强大的数据分析组件numpy，pandas，matplotlib等进行自动化编程，并在服务器端安全执行后输出结果。

所以，在企业的数据分析场景中，是否也可以借助LLM的代码生成能力，实现自动化的数据分析应用呢？我们不妨设想这样一种用例：

**针对合适的场景与分析主题，从企业数据仓库/数据库提取与同步数据到临时的数据分析存储区（如文件），借助于LLM的能力向决策者提供交互式数据分析与洞察能力。** 

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/b0d48052356b41bbad277ed3ab3798e2~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827466&x-signature=2zaINWsKoD5moGKHH%2BJ9a0SuDik%3D)

当然，基于目前Code Interpreter展示的能力，我们认为：

*   基于代码解释器的数据分析与现有的BI工具不是取代而是互补，这和我们前面对基于LLM的数据分析的定位是一致的
*   代码解释器适合的工作层为经过汇总、建模与抽象过的数据层，物理形式最好是文件
*   与Text2SQL输出针对数据库的代码（SQL也是代码的一种）不一样，代码解释器并不直接针对数据库：**从海量的数据中快速检索与操作数据是SQL而非代码解释器的强项。** 
*   建议代码解释器针对的应用场景限制为：

*   较小或者中等规模的数据集
*   有着灵活、交互式数据查询分析需求的主题
*   相对规范与简单的数据模型，比如星型模型
*   涉及较复杂的数据挖掘算法与模型，如回归分析

我们探讨两种用于数据分析的代码解释器方案：

*   **借助Assistants API实现**
*   **基于Open Interpreter+LLM实现**

Assistants API是OpenAI面向Agents领域的一次重要更新，通过该API，你可以**在线创建具备自主规划、工具使用与记忆能力的AI数据分析助手**，通过自然语言输入问题与上传文件，实现自主的交互式数据分析。Assistants API实现的基本架构如下（来自OpenAI官方文档）：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/f0def2bed83844ad9055ad81fd72d7ae~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827466&x-signature=YsPyRY4GOVGD4LnJ%2FpmbfEwMASQ%3D)

创建Assistant，设定其能够使用的工具，然后就可以通过自然语言与其对话，上传需要分析的数据，输入你的分析需求，获得返回结果。与普通的ChatGPT对话不一样的是，**Assistant具有记忆能力，你无需在每次交互都输入完整的对话历史以实现对上下文的理解**。目前Assistants API支持的工具包括：

*   **Code Interpreter：** 官方代码解释器
*   **Function Calling：** 理解输入的自然语言，返回函数调用请求
*   **Web Browsing：** 获取实时互联网信息

如何实现交互式分析过程中的数据输入呢？可以考虑两种方式：

*   **文件输入**：通过Assistants API在消息中上传文件。
*   **借助Function Calling：** 可以在Assistant的工作过程中，根据Assistant的响应，按需调用本地API获得数据（如访问企业数据库），并将数据再反馈进入Assistant，进而获得分析结果。当然，你需要在创建Assistant时设定允许使用Function Calling工具，并且提供自定义的数据获取函数（API）说明。

> 比如，输入“对今年与去年全年的销售数据做对比，并用图表展示比对结果“，那么Assistant可以在运行时识别你的请求，并首先要求你调用数据获取API获得“去年与今年的销售数据”；在获得你的再次输入之前，Assistant将等待你的数据。

所以，构建一个基于Assistants API的数据分析助手的大致过程如下：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/161d46b60a994554836fbed76c36272b~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827466&x-signature=TmLWxl9si2I3Eu4yx%2BNchsCcENA%3D)

总的来说，基于Assistants API实现一个简单的数据分析助手是比较简单的，后续我们会出一个具体的演示样例。

借助于OpenAI的Code Interpreter做本地数据分析，存在一些显而易见的问题：

*   **由于是一个运行于ChatGPT之上的一个在线闭源工具，因此你必须联网使用（且目前并不向中国用户直接开放）**
*   **数据的交互方式只能是上传下载，对于敏感的企业用户来说，数据安全性将成为一个顾虑**
*   **由于工具自身被OpenAI托管，你无法对其功能进行拓展，任务完成的能力受限于其自身安装的软件包**
*   **除非借助于OpenAI的Web Browsing工具，无法进行互联网联网处理，这也会限制你的任务能力**

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/0b8d180e2d8142d1a5f45efce58d89a0~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827466&x-signature=jdRwgSux8b4GBf8f2pm0Bv%2BSEhM%3D)

因此，我们需要一个能够脱离ChatGPT环境运行的代码解释器，能够借助任意大语言模型（比如ChatGPT或者CodeLlama）的代码生成能力来完成个性化的任务。这对于面向企业的有着较高数据安全性要求的自动化任务场景，有积极的意义。

**一种替代的方法是自行实现Code Interpreter。** 

因为从原理上讲Code Interpreter无非也是借助大模型自身的理解与推理能力输出代码，因此借助提示工程实现Code Interpreter也是可能的。当然，如果需要设计一个完善的Code Interpreter，至少需要解决如下关键问题：

*   **需要精心设计与调试你的Prompt。** 比如针对的编码语言、代码安全性、如何注入数据信息、模型推理模式、参考代码样例等等。
*   **代码的本地执行过程控制。** 比如是在宿主机直接运行还是在本地“沙箱”（比如一个容器）中运行，如何处理代码的输入输出等。
*   **自我反省、纠错与优化过程。** 即根据生成代码的执行结果自我审查与纠正，比如发现未安装的软件包能够自动下载安装；或者尝试自动切换不同的工具来完成任务等，并能控制迭代次数，减少token的过度消耗。

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/410fdf55791c40128a630c20574a65d4~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827466&x-signature=5u%2B06zUWyl%2Fvzfu2YDM%2B7acIJqM%3D)

OpenAgents中基于Python的自动数据分析插件

**另外一种替代也是推荐的方法是借助于开源项目：Open Interpreter。** 

Open Interpreter是一个非常接近OpenAI的原代码解释器的一个开源实现。具有很好的代码生成、自我审查纠错、代码执行能力，并能够接入非OpenAI模型，并且可以独立运行在本地，具备极好的扩展能力，你可以根据需要进行更多的个性化的设置与修改。

**Open Interpreter提供用于开发的python软件包。因此我们在开发自己的数据分析Data Agent时，可利用开发包进行更多的本地化设置。比如设定一些默认的本地环境、需要接入的LLM模型、默认的工作空间目录、甚至默认的本地数据库连接信息等。** 

基于Open Interpreter构建一个本地的交互式数据分析架构如下，这里：

*   LLM：需要接入的大模型，默认为OpenAI
*   SandBox：执行生成代码的沙箱环境，当然也可选择本地执行，但要小心环境污染问题
*   WorkSpace：设置代码解释器默认的工作目录，对于数据分析来说，用于从该目录读取需要输入数据文件，生成输出的分析结果、中间文件等

![](https://p26-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/fdfbb1ff6b294cbdafc883d0e1ed4497~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827466&x-signature=srm3A5rPwgklZrPEWt%2FLcAtNeS8%3D)

开源的代码解释器主要解决了以下问题：

*   **可以在本地运行和处理。** 这大大扩充了使用场景，你无需把文件传输给ChatGPT来完成任务，完全可以部署在桌面端或者服务器端，直接访问企业私有数据。
*   **可以直接连接互联网。** 由于本质上是自动编写代码，所以理论上可以借助API对接各种互联网平台，比如搜索引擎、云计算、各类工具API，比如你可以要求它处理完成自动上传到你的云端存储，甚至发送邮件给老板邮箱。
*   **预装软件包可以无限扩充。** AI在编写代码的过程中如果发现包缺失，会自动选择安装；如果代码运行错误，甚至会自动切换其他实现方式，直到成功完成任务为止。
*   **不依赖于某个大模型，比如ChatGPT。** 经过测试和微调，你完全可以选择自己认为最优秀的代码生成大模型来作为底层模型，比如你可以选择CodeLlama。

当然，我们在测试中也发现一些尚待解决或者需要进一步完善的问题：

*   **代码解释器严重依赖于底层大模型的代码输出能力。** 即使是ChatGPT3.5和chatGPT4也有本质的区别，这需要我们在交付使用之前做更加详细的测试来确保任务结果的正确性。
*   **大语言模型天然的输出不确定性，会导致某些任务“结果”的不确定性**。比如有的任务这次完成，下次未必能成功完成。
*   **自我检查与自动纠错能力需要进一步完善。** 有时候会导致无限迭代，始终无法完成任务，这在实际应用中会造成大量tokens的浪费，因此对于异常情况下可能需要更谨慎的处理。
*   **代码解释器对tokens消耗较大。** 因此如果你使用GPT-4这样比较昂贵的大语言模型，你可能需要非常小心的控制使用，尽管在实际测试中GPT-4明显有着更高的任务完成率。

至此，我们对在企业数据分析场景中引入基于LLM的交互式分析的几种基础技术方案做了探讨。我们也测试与推荐了一些相关的工具项目，客观来说，尽管大模型的技术与能力日新月异，但是在ToB领域，在对安全性、可靠性、准确性要求更高的场景下，当前LLM创意有余而准确性不足的问题会被进一步放大，离真正的实用性还有一定差距。我们不妨对几种方案做简单总结：

*   **Text2API：一种相对“浅层”的应用方案。** 具备更好的安全性，毕竟真正的分析过程由API来实现。这也导致其问题是灵活性严重受限，也就无法体现出LLM的真正价值。
*   **Text2SQL：一种更“直接”的数据分析方案。** 用数据库的“语言”直接与数据库“对话”，实现真正的交互式分析。其最大问题来自于LLM输出SQL的精确率不足，这可能导致潜在的错误分析结果。
*   **Text2Code：更加适合脱机数据分析的一种方案。** 强项是可以借助于编程语言本身强大的工具包与算法来进行数据分析挖掘类任务。其缺点一方面来自对LLM能力的依赖，另一方在面对企业级的巨量数据任务时能力受限。  
      
    

幸好，我们有着类似DB-GPT、Open Interpreter、DAIN-SQL等这样的开源研究项目及其背后的贡献者，相信在经过大量的学术研究与实验性项目后，在不久的将来，我们与数据“对话”的方式将真正的被大模型重新定义与改变。