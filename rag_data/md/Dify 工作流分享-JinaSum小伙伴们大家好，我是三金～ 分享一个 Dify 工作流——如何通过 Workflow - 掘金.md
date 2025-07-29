[Dify 工作流分享-JinaSum小伙伴们大家好，我是三金～ 分享一个 Dify 工作流——如何通过 Workflow - 掘金](https://juejin.cn/post/7419225430433234996) 

 小伙伴们大家好，我是三金～

今天要分享的 JinaSum 其实在之前的文章《[使用 dify-on-wechat 中的插件搭建私人助理](https://juejin.cn/post/7409147273736339508 "https://juejin.cn/post/7409147273736339508")》中已经有介绍过，不过它是以 dify-on-wechat 中插件的身份出现的，其主要作用就是捕获分享到微信聊天中的 url，然后爬取网页内容进行总结。

今天我们通过工作流的方式来实现一下。

打开 Dify 并新建一个空白工作流（起名就叫 JinaSum 好了），在这个工作流中我们需要四个节点：

*   **开始节点**：接收一个网页链接；
*   **HTTP 请求节点**：这里可以通过之前我们部署的本地 firecrawl 服务来实现，也可以选择使用 jina 来实现，主要作用是爬取网页内容并将其转为 Markdown 格式；
*   **LLM 节点**：接收上一步传递过来的内容，并对其进行总结整理；
*   **结束节点**：将总结的内容进行输出即可；

![](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/662c69c62bc94551ac44a4ffdbaff9b9~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5LiJ6YeR5b6X6ZGr:q75.awebp?rk3s=f64ab15b&x-expires=1734866999&x-signature=3ypqxsRWS%2BMsXumowFrc5ZtHwMA%3D)

具体实现：

*   在开始节点中，定义一个字段 url，这个字段主要用来接收用户想要进行总结的网页链接；
*   HTTP 请求，我们需要将网页链接地址发送给爬虫服务，让这个服务进行内容爬取并将其转换为 Markdown 格式，之后再将结果输出给下个节点。对于爬虫服务来说这里有两种选择：

一种是使用线上服务，推荐 jina AI：`https://r.jina.ai/`，我们只需要在这个链接后面拼接上开始节点输入的 url 链接即可。

![](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/8e74049f492a413d9275e6c47139e32f~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5LiJ6YeR5b6X6ZGr:q75.awebp?rk3s=f64ab15b&x-expires=1734866999&x-signature=U1%2F5MUWaTO6WR9y%2BT9AC33S0jyo%3D)

另外一种是使用之前的文章中《[本地部署 Firecrawl 爬虫让 AI 知识库更丰满](https://juejin.cn/post/7413964058788216869 "https://juejin.cn/post/7413964058788216869")》介绍的，使用 firecrawl 的服务：

![](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/1aa8671038da4905b2e2d73e5c182c47~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5LiJ6YeR5b6X6ZGr:q75.awebp?rk3s=f64ab15b&x-expires=1734866999&x-signature=APODlYOIAD0DAZZN0ibTQDVoK78%3D)

> 相较之下 jina 会更简洁方便一点，但 firecrawl 的话可以根据自己的需求进行一些参数配置，定制化强一点。
> 
> 比如可以通过设置 onlyMainContent 参数来限制返回的内容是否为主要内容，设置该参数为 true，则仅返回页面的主要内容，不包括页眉、导航、页脚等。

*   将爬取到的网页内容输出到 LLM 中，在 LLM 中预设好提示词即可：

![](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/a4e24768b5f84e0db544c93f60beedbd~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5LiJ6YeR5b6X6ZGr:q75.awebp?rk3s=f64ab15b&x-expires=1734866999&x-signature=fLXrmfj9amvbBLtauchatpZR7cE%3D)

> 提示词：
> 
> 我需要对下面的文本进行总结，总结输出包括以下三个部分：
> 
> 📖 一句话总结
> 
> 🔑 关键要点,用数字序号列出3-5个文章的核心内容
> 
> 🏷 标签: #xx #xx
> 
> 请使用emoji让你的表达更生动。
> 
> \`\`\`markdown
> 
> <这里记得接收上个节点输出的数据>
> 
> \`\`\`

*   最后通过结束节点输出总结好的内容

我们来测试一下：

![](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/6ba7217ce6524a528682e01438062ae2~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5LiJ6YeR5b6X6ZGr:q75.awebp?rk3s=f64ab15b&x-expires=1734866999&x-signature=n4M9b7WYVqkosmF2Iz9VQHIPHN0%3D)
 ![](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/28176175aa9c4b97952006ef91c9bbb3~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5LiJ6YeR5b6X6ZGr:q75.awebp?rk3s=f64ab15b&x-expires=1734866999&x-signature=xea0gD7UBNrwSIMov96KY8czXAE%3D)

使用 Jina （图一）和 firecrawl （图二）都是可行的。

在完成该工作流之后，我们还可以通过右上角的发布按钮，将其发布为工具，这样的话既可以在 Agent 中使用，也可以将该工具再集成到别的工作流中循环利用。

> 觉得有用的大佬，轻抬小手 `点赞`、`收藏` 加 `关注`