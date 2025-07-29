[最新扣子(Coze)实战案例：爆款金句图文生成器，完全免费教程 - 大模型知识库|大模型训练|开箱即用的企业大模型应用平台|智能体开发|53AI](https://temp53ai.uweb.net.cn/news/coze/2024101093651.html) 

 **先来看一下生成的效果图：** 

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDAwNjFia0dRQWliQ3VBaWJpYzlUeW5Da1dWSTNOb0xyaFdWNUlZaDRVa3NFNE9vbWduejJNQ2lhemRBWUZnM2N4eERCTFg0VWtQdmljbkdjZy82NDA/d3hfZm10PXBuZyZhbXA=;from=appmsg)

话不多说，拿起键盘，开始教学 ~

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDJtN2U4MGliWjBjM0d6YXRuTXZZV0pPcTJJbzNDYzBGQUJoUjZpYzU0b3hCOFN0N0ttUzVmbmx2NTJ6TFgwbEJnZUZzdW1vMHdseWRJQS82NDA/d3hfZm10PXBuZyZhbXA=;from=appmsg)

**设计目标：** **搭建一个工作流，根据用户提供的主题，生成一套金句图文。** 

**关键知识点：** **大模型、工作流、图像流、代码节点、卡片使用**

**一、搭建工作流**

********1、新建工作流********

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JINldINXZyQkVrWWRCcmliWHpsUlVjeXhLYXJ1WlpRMm15V0M3Mko0SjdXNDV2ekFvcm42MmliQS82NDA/d3hfZm10PXBuZyZhbXA=;from=appmsg)

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JWR1padmVLbGtZRkEwenI2ck90Y1E2RTdnWjFhYTRhaWF0VjNpYWlibDdpYzh6OUt6MFUyVmdwZmJnLzY0MD93eF9mbXQ9cG5nJmFtcA==;from=appmsg)

********2、开始节点********

参数只有一个输入，是当前会话用户输入的包含视频链接的内容。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2J3MVBINGJHQ1RvTWI0VDJEaHFUQmpLN1hqOU9PNGJxd2liNExzbHNuQzBpY0xmNFljUWx6UURydy82NDA/d3hfZm10PXBuZyZhbXA=;from=appmsg)

**3、大模型****提取参数****节点**  

开始节点后面连接一个大模型节点，用来从输入内容中提取视频链接。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDNHazU0WkZwb2liRUJSZVdyQmVURUpFY1ZmRmFWeVlWNDFOTDdTdWFIN2hQMG54SmN4TVI0b2RuYVFtRWRhUGljbEtpY1dDOGxid3VQQ0EvNjQwP3d4X2ZtdD1wbmc=)

这里输入的对话内容的模版格式如下：

主题：超人

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JCVHZiRW1tT3VZVmRpYk81UXBpYnZhNnlYYTNWWnkxdUtFUlJaazNqaWJBdW0zaEJzQ0NLWWZGaHcvNjQwP3d4X2ZtdD1wbmcmYW1w;from=appmsg)

  

**4、 大模型****撰写金句****节点**

提取到主题参数后，我们就可以根据这个主题参数开始撰写金句了。撰写金句主要就是提示词的写法。  

同样，大家可以根据自己的需求写提示，也可以在我的**「团队空间」**里进行查看。**（团队空间加入方法请见文章结尾）**

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JxREdpYWR1UWljb2FEcUxOaEJZakxYUFhGRU9ZZnlpYzBYdmVyZDZCTFJ1RnA5TkViOVNoOGV3MHcvNjQwP3d4X2ZtdD1wbmcmYW1w;from=appmsg)

**5、大模型****标题描述****节点**

撰写完金句内容以后，我们就可以根据金句的内容来**生成标题和描述**了。要想生成好一个符合金句内容的标题和描述，关键的也是**提示词**的写法。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2I0YW0zSXR2dWljTEk3THBTbHRYVFRPZkQ1ckJ6SzRRemljUlZkaWJ2MXVqZFMyd28za1VpYThKZVZ3LzY0MD93eF9mbXQ9cG5nJmFtcA==;from=appmsg)

**6、 大模型****图像提示词****节点**

这个节点很主要，生成的内容需要传给图像流，用来生成图像。图像生成的是否符合文案与否，完全取由这个提示词决定，大家可以根据自己的需要编写，也可以加入我的**「团队空间」**，使用我的提示词。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JaTVF2V2hMTTQwWHJ1eW1zSUFvSnFSRlRTTkg3TEpNWERLVk0yekhvbDN0YzhnR2VKclBnSmcvNjQwP3d4X2ZtdD1wbmcmYW1w;from=appmsg)

**7、 引入图像流**

有了对图像流的描述，这里我们就可以引入图像流节点了，这个**图****像流节点会我们生成具体的图片**，图像流我们在下面的流程里讲解。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JpYmJRbThlVWdZNFRUMU1PS1V5dGRna3dSdDBrT3RvVnNacjl0TGZNOUNqTWp6MGxWQ2ZtU0Z3LzY0MD93eF9mbXQ9cG5nJmFtcA==;from=appmsg)

**8、代码节点**

在这里使用了一个代码节点，**主要是用来把上面图像流生成的图片转换为一个数组，只有绑定为数组**，才能让BOT的卡片节点进行调用。卡片可以让图片渲染到前端的对话框窗口，布局更美观。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDNHazU0WkZwb2liRUJSZVdyQmVURUpFTTR5Uk1ET0VaNlNSUkFGRzdKWEZCOEdHS3BKYk5tam5iaWJxaWNSOGh1WFlQV0E2TVNCcHdsTFEvNjQwP3d4X2ZtdD1wbmc=)

**备注：斜杠君为大家准备了详细的代码，关注公众号回复："金句图文" 获取完整代码和详细飞书文档教程。** 

**9、结束节点**

代码节点连接到工作流的结束节点，可以看到，在这里我们返回了**三个参数**，图片的列表**（在前面代码中生成的）**，还有在前面大模型中生成的标题和描述。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JXRlIxTFlpY0VuT29aUGliSHdIdmRjbWhVaE5mWERQdWdUdUVLZnpEZUNxWjZzTXh6eDNQZGdlZy82NDA/d3hfZm10PXBuZyZhbXA=;from=appmsg)

**二、搭建图像流**

**1、新建图像流**

**这个图像流是整个工作流中的关键**，作用是生成金句图文件，最主要的生图工作就是用这个图像流完成的。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JKaDdHMjU5WUkyQjhQYnVjQTRZUmliU3dxcXJpYWlhbzhIRkYwcnRDRm9iaFNzMFhrVzdnN3U1c0EvNjQwP3d4X2ZtdD1wbmcmYW1w;from=appmsg)

******2、开始节点******

开始节点用来接收参数。这个参数来源就是上面工作流中传递过来的。图像流接收了两个参数，一个参数是**金句的内容**，还有一个参数是**生成图像的提示词**。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2J4TlFtUjV3VWNlS0xacVhjWGdXczFjSTh3RVBldVRQdFZ1MmFIYk1tUnlGZzNVY1Y3UTl6REEvNjQwP3d4X2ZtdD1wbmcmYW1w;from=appmsg)

**********3、提示词优化**********

在生成图片之前，我们使用图像流中的**提示词优化节点**对提示词进行一下优化，能使图片生成的效果更好。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JOaWExaWFEVnRQZVJJWlNYNDZBNGlhdkxlamRiaWFyNzY2QlB2VlhlOWRBeUJscnZuNDNQdjcxZk9nLzY0MD93eF9mbXQ9cG5nJmFtcA==;from=appmsg)

******4、图像生成节点******

关键的节点来了，我们主要的生图工作就是由这个节点完成的了。我们前面做的一系列工作就是为这个节点准备生成图像的提示词参数。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JQc0tOSU81dUlwUDJxNDJLOFg4aDlZRExYanQ2bDF6UldmaWE5aWNNV3JlbnEwZkhaNk9USjFpYXcvNjQwP3d4X2ZtdD1wbmcmYW1w;from=appmsg)

**5、画板节点**

图片生成好，接下来我们就要排版布局最终的需要生成的效果图了，看一下我们期望的效果的图样子。就是我们在前面展示的：

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JTeVJNV1JqWlNuOFRPa014TGJWU0RpYUdHNWJVQllVZzVYcFJ4NG9pYjE5N3Z0bUEzWG5FS1JjQS82NDA/d3hfZm10PXBuZyZhbXA=;from=appmsg)

最终的效果图需要一个图片，一个金句，可以看到我们的画板中接收到的正是这两个参数：

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JXMXlPM0dvdUFxcDdkT2ljZWliR3VMN09hbzM2YjJvRmVISU02Qm1TU2ZVVmZza29hcHlabW9sZy82NDA/d3hfZm10PXBuZyZhbXA=;from=appmsg)

**6、结束节点**
----------

生成好以后，我们对这个图片进行一个输出就可以被工作流调用了。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JBNjg4SHQ3VGVWR0ZmUGdwN0toeG1HaWNteUVtbktUYjV0alBuaE1VMjVMV3FxZEhSQjFRVWJRLzY0MD93eF9mbXQ9cG5nJmFtcA==;from=appmsg)

****二、创建BOT****

**1、新建一个BOT**

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JNRU5lNExjVHlWdWRHV3NNWnd5R1luNExXaWM5QWtSTU5YaWM4S1pST2J0WEZVQ1JlMXF1VTRuQS82NDA/d3hfZm10PXBuZyZhbXA=;from=appmsg)

**2、引入工作流**

把工作流模式设置为**单Agent模式**，单Agent模式让工作流更稳定。同时引入我们之前创建好的工作流。

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2J6SXhyelB5Mmlid1JDd29xQ2w5aWNkUGNHYVIzZU53eHpjOWZoOUFOWWxiV081QTFGdmdpY1NtMWcvNjQwP3d4X2ZtdD1wbmcmYW1w;from=appmsg)

**3、引导开场白**
-----------

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JSNWR3dXRYVVpJTElNak1FQTJkelJuNFJwSmZpYWxGaWM2WFpsdmdFRzlIUTl6OVNGWmFScGlidmcvNjQwP3d4X2ZtdD1wbmcmYW1w;from=appmsg)

**三、使用演示**

**1、点击预置问题**
------------

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2I5ck1VV082clRoSThjSUNualRrY0ZKODBJRlhnMDhMZGtmTURldWNEZWRtdEJYbkJoQ256UHcvNjQwP3d4X2ZtdD1wbmcmYW1w;from=appmsg)

**2、图文效果**
----------

![](https://api.ibos.cn/v4/weapparticle/accesswximg?aid=90538&url=aHR0cHM6Ly9tbWJpei5xcGljLmNuL3N6X21tYml6X3BuZy95cnVxOVJpYndINDFjSHU0dVgyNjN3NXUxQXV3WnI3T2JFR1RTa0J2dHQwa1NUSEtucDliSTBvbEtrTTJvc3hWQ2FCczNPeXlCdVphanV4Smc2YjlSelEvNjQwP3d4X2ZtdD1wbmcmYW1w;from=appmsg)

好了，到这里搭建**「爆款金句图文生成器」**的教程就为大家讲解到这里，大家快动手试试吧 ~ ![](https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.3.10/assets/newemoji/Addoil.png)