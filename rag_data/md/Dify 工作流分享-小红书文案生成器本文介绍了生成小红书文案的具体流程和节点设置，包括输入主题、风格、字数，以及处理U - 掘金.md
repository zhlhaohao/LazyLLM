[Dify 工作流分享-小红书文案生成器本文介绍了生成小红书文案的具体流程和节点设置，包括输入主题、风格、字数，以及处理U - 掘金](https://juejin.cn/post/7435545913899434021) 

 小伙伴们大家好，我是三金～

最近在媳妇儿的影响下，我也下载了一个小红书，每天闲暇时间会打开它，刷刷帅哥美女以及一些炸裂的帖子（真的炸裂）。偶尔也会自己发一下生活状态，比如分享自己超级喜欢的咖啡店～

奈何第一次发笔记就陷入了僵局，配好图之后陷入了长达快一个小时的沉思：

*   我应该配什么文案？
*   加什么 emoji 图标？
*   怎么才够吸流？

在反复的修修改改之下，我选择走捷径：使用 AI 帮我快速生成！

还是熟悉的配方，还是熟悉的味道，本次还是使用 Dify 来完成小红书文案生成器工作流～

> 还不知道 Dify 是什么的小伙伴快去看这篇入门《[37.4k 的 Dify，一款小白也可以轻松上手的大模型开发平台（一）：部署及基础使用](https://link.juejin.cn/?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzUyODkwNTg3MA%3D%3D%26mid%3D2247485019%26idx%3D1%26sn%3D572e8f94c6d082183d80788a53cc6f55%26chksm%3Dfa6865bacd1fecac6f3ed04454f5751444c7cf7849490d8991faf9e9c2296f565ac05140aa58%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=MzUyODkwNTg3MA==&mid=2247485019&idx=1&sn=572e8f94c6d082183d80788a53cc6f55&chksm=fa6865bacd1fecac6f3ed04454f5751444c7cf7849490d8991faf9e9c2296f565ac05140aa58&scene=21#wechat_redirect")》

### 生成文案需要什么？

在学生时代，大家一定都写过作文，而作文题目一般都会有以下几条要求：

*   中心思想，或者说主题
*   文章风格
*   文章字数

适用到小红书上也是如此，我们只要定义好这三个点，再设定好合适的提示词（prompts），模型上选择 ChatGPT 或者 Claude 3.5 来打打最强辅助，很快就能生成一个贴近你想法的文案出来！

延伸一下，假如看到一篇比较好的文章或者资讯，是否也可以用 AI 总结并生成一篇小红书风格的文案呢？

> ⚠️注意！要实现这一点，虽然比较容易，但要提前获取原文授权

大致的实现思路有了，接下来让我们一起看看具体实现。

### 要用哪些节点？

*   开始节点：用来输入要生成文案的中心思想（或者 URL 链接）、风格及字数；
*   问题分类器：因为我们输入的中心思想不只是文字，还可能有 URL 链接，所以这里需要通过问题分类器来进行分类；
*   网页爬虫 + 爬虫生成文章：如果是网页 URL，那么会走到网页爬虫这个节点进行内容爬取。爬取之后得到的内容会传递给 LLM 节点，我们给这个 LLM 节点起名叫「爬虫生成文章」。没错，它的作用就是通过预设的 prompts 来生成符合我们预期的小红书文案；
*   主题生成文章：如果我们只是输入一个主题，那会直接到「主题生成文章」的 LLM，最终生成一个符合预期的文案
*   变量聚合器：不管是「爬虫生成文章」还是「主题生成文章」，最终的结果都会汇聚到变量聚合器节点
*   结束：最终输出

### 实现细节

首先对于开始节点来说，我们需要三个输入字段：

*   key：主题或者 URL 链接
*   style：文案风格
*   length：文案的长度

设置好之后将内容传递给问题分类器，分类器这里会自动判断我们输入的只是一个主题还是一个 URL：

*   如果是 URL：会将其传递给网页爬虫节点，这个节点是一个内置工具，我们直接在工具中搜索「网页爬虫」即可。网页爬虫会将网页内容直接输出到下一个 LLM 节点；
*   如果是主题：直接将主题传递给 LLM 节点。

然后，不管是「爬虫生成文章」还是「主题生成文章」，它们都会按照我们设定好的提示词生成对应的文案，并输出到变量聚合器中。

最终通过结束节点进行输出。

![](https://note.ihsxu.com/api/imgs/1731225336528.webp)

### 上手试试

测试方向有两个：

*   直接输入想生成的文章主题或者说中心思想
*   输入想要转换的文章 URL

#### 文章 URL

前段时间三金在研究 AI 爬虫的时候有找一些资料，其中在 Medium 上有看到一篇《[From Manual to Automated: The Future of Web Scraping with LLM](https://link.juejin.cn/?target=https%3A%2F%2Fmedium.com%2F%40mohammed97ashraf%2Ffrom-manual-to-automated-the-future-of-web-scraping-with-llm-97b04ce93476 "https://medium.com/@mohammed97ashraf/from-manual-to-automated-the-future-of-web-scraping-with-llm-97b04ce93476")》，其中主要讲的是 AI 爬虫工具的介绍，我们以这篇文章为例进行测试：

![](https://note.ihsxu.com/api/imgs/1731226284307.webp)

> 虽然是英文文章，但是由于提示词的原因，它最终输出的是中文，很 nice～

#### 文章主题

已经入冬了，我们以冬天作为主题来生成一个小红书文案：

![](https://note.ihsxu.com/api/imgs/1731226558263.webp)

看起来还 OK，不过内容上还有些僵硬，这主要取决于 prompt 和 AI 模型，大家感兴趣的话可以在后台留言「小红书文案生成器」获取对应的 DSL 文件，然后自行修改 prompt 来达到你想要的效果～

关于提示词工程，大家可以参考：

*   [18.2k 的 fabric，一款超强 AI _Prompt_ 辅助](https://link.juejin.cn/?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzUyODkwNTg3MA%3D%3D%26mid%3D2247484954%26idx%3D1%26sn%3D0f42d0ab0b43f980ebaeab31ba5757dc%26chksm%3Dfa6865fbcd1feced867bacfd07cdcb0f19fa2621b8e84d8c4e97a2f52672682566d0979597e3%23rd "https://mp.weixin.qq.com/s?__biz=MzUyODkwNTg3MA==&mid=2247484954&idx=1&sn=0f42d0ab0b43f980ebaeab31ba5757dc&chksm=fa6865fbcd1feced867bacfd07cdcb0f19fa2621b8e84d8c4e97a2f52672682566d0979597e3#rd")
*   [OpenAI 官方推出的 AI _Prompt_ 提示词编写公式](https://link.juejin.cn/?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzUyODkwNTg3MA%3D%3D%26mid%3D2247484754%26idx%3D1%26sn%3D4bacc9b5009f9c1618b4fd3468ce99ac%26chksm%3Dfa6866b3cd1fefa5f57fc9f7f1d24bfeb5c4ce2838b364d303708e70933049f748aa3818d052%23rd "https://mp.weixin.qq.com/s?__biz=MzUyODkwNTg3MA==&mid=2247484754&idx=1&sn=4bacc9b5009f9c1618b4fd3468ce99ac&chksm=fa6866b3cd1fefa5f57fc9f7f1d24bfeb5c4ce2838b364d303708e70933049f748aa3818d052#rd")
*   [让 AI 更懂你的 _Prompt_ 提示词宝藏网站-FlowGPT](https://link.juejin.cn/?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzUyODkwNTg3MA%3D%3D%26mid%3D2247484626%26idx%3D1%26sn%3D53c0d832d9947f4289018e5bc67ae6c9%26chksm%3Dfa686733cd1fee2535bdcabc8fa8a18eedfad68b1b7cfbf42262bff56550c97295712c6b7c61%23rd "https://mp.weixin.qq.com/s?__biz=MzUyODkwNTg3MA==&mid=2247484626&idx=1&sn=53c0d832d9947f4289018e5bc67ae6c9&chksm=fa686733cd1fee2535bdcabc8fa8a18eedfad68b1b7cfbf42262bff56550c97295712c6b7c61#rd")

> 觉得文章对您有用的 `jym` 请轻抬小书 `点赞`、`收藏` 加 `关注`~