[Vanna：10分钟快速构建基于大模型与RAG的SQL数据库对话机器人 - 今日头条](https://www.toutiao.com/article/7345444210763563539/?log_from=fb46630d4f6ff_1735222369464) 

 **专注LLM深度应用，关注我不迷路**

在之前的文章中曾经详细介绍过基于大模型（LLM）的交互式数据分析的一种常见技术-Text2SQL，即把自然语言借助LLM转换SQL语言并自动执行以获得输出结果；而LLM自身的不确定性带来的准确率不足的问题，需要从模型与Prompt两种主要的优化方向入手，也了解了一些初期的技术研究成果（原文参考：[构建Data Agent：企业应用中基于大模型的数据分析及方案【中】](https://www.toutiao.com/i7305742482497864192/?group_id=7305742482497864192)）。

今天我们来重点研究与实测一个开源的Text2SQL优化框架 -- **Vanna：** 

*   **基本概念**
*   **技术架构与原理**
*   **扩展与定制化**
*   **实测：基于Vanna快速构建数据库对话机器人**

![](https://p3-sign.toutiaoimg.com/tos-cn-i-axegupay5k/0e12b9f8765447fd8b3d85cab46f7205~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=wf5L%2FViuFmW92klphR0ypLbbEhk%3D)

简单的说，**Vanna是一个开源的、基于Python的、用于SQL自动生成与相关功能的RAG（检索增强生成）框架**。基本特点：

*   **开放源代码（**Github上搜索Vanna可进入该项目，MIT license）
*   **基于Python语言。** 可通过PyPi包vanna在自己项目中直接使用
*   **RAG框架。** 很多人了解RAG最典型的应用是私有知识库问答，通过Prompt注入私有知识以提高LLM回答的准确性。但RAG本身是一种Prompt增强方案，完全可以用于其他LLM应用场景。比如之前我们介绍过的在构建Tools Agent时，利用RAG方案可以减少注入到Prompt中的APIs信息的数量，以减少上下文窗口的占用，节约Tokens。**Vanna则是通过RAG方案对输入LLM的Prompt进行优化，以最大限度提高自然语言转换SQL的准确率，提高数据分析结果的可信度。** 

我们知道，借助LLM实现一个最简单的、基于Text2SQL的数据库对话机器人本身原理是比较简单的：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/a2e3c5ac5f3d4e5a98181b942d68f9f1~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=Zm2fmdKlkJjMcRab%2BWACSOUwM48%3D)

这里的关键在于：如果不在大模型层进行优化（比如针对SQL进行微调），那么唯一的优化手段只有Prompt，在之前文章中提到的一些技术研究报告很多都是基于Prompt优化，但都相对较复杂。**Vanna则是借助了相对简单也更易理解的RAG方法，通过检索增强来构建Prompt，以提高SQL生成的准确率：** 

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/db91bd77a97d4ffe83eb31eb26974d66~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=CubcSWxfmaCSzXikK7jXgIJUx%2Fg%3D)

来源：Vanna.ai官方图片

从这张图可以了解到，Vanna的关键原理为：

**借助数据库的DDL语句、元数据（数据库内关于自身数据的描述信息）、相关文档说明、参考样例SQL等训练一个RAG的“模型”（embedding+向量库）；并在收到用户自然语言描述的问题时，从RAG模型中通过语义检索出相关的内容，进而组装进入Prompt，然后交给LLM生成SQL。** 

因此，使用Vanna的基本步骤分为两步：

**第一步：在你的数据上训练一个RAG“模型”**

把DDL/Schemas描述、文档、参考SQL等交给Vanna训练一个用于RAG检索的“模型”（向量库）。

> Vanna的RAG模型训练，支持以下几种方式：
> 
> 1\. DDL语句
> 
> DDL有助于Vanna了解你的数据库表结构信息。
> 
> vn.train(ddl="CREATE TABLE my\_table (id INT, name TEXT)")
> 
> 2\. 文档内容
> 
> 可以是你的企业、应用、数据库相关的任何文档内容，只要有助于Vanna正确生成SQL即可，比如对你行业特有名词的解释、特殊指标的计算方式等。
> 
> vn.train(documentation="Our business defines XYZ as ABC")
> 
> 3\. SQL或者SQL问答对
> 
> 即SQL的样例，这显然有助于大模型学习针对您数据库的知识，特别是有助于理解提出问题的上下文，可以大大提高sql生成正确性。
> 
> vn.train(question="What is the average age of our customers?",sql="SELECT AVG(age) FROM customers")
> 
> 4\. 训练计划（plan）
> 
> 这是vanna提供的一种针对大型数据库自动训练的简易方法。借助RDBMS本身的数据库内元数据信息来训练RAG model，从而了解到库内的表结构、列名、关系、备注等有用信息。
> 
> df\_information\_schema=vn.run\_sql("SELECT \* FROM INFORMATION\_SCHEMA.COLUMNS")
> 
> plan=vn.get\_training\_plan\_generic(df\_information\_schema)
> 
> vn.train(plan=plan)

**第二步：提出“问题”，获得回答**

RAG模型训练完成后，可以用自然语言直接提问。Vanna会利用RAG与LLM生成SQL，并自动运行后返回结果。

从上述的vanna原理介绍可以知道，其相关的三个主要基础设施为：

*   **Database**，即需要进行查询的关系型数据库
*   **VectorDB**，即需要存放RAG“模型”的向量库
*   **LLM**，即需要使用的大语言模型，用来执行Text2SQL任务

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/e34daa32243c438c9a9e9c1cc2317e76~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=Wp7daOBQCSPcMfpDvzzASw7KHWI%3D)

Vanna的设计具备了很好的扩展性与个性化能力，能够支持任意数据库、向量数据库与大模型。

**【自定义LLM与向量库】** 

默认情况下，Vanna支持使用其在线LLM服务（对接OpenAI）与向量库，可以无需对这两个进行任何设置，即可使用。因此使用Vanna最简单的原型只需要五行代码：

```
import vanna
from vanna.remote import VannaDefault
vn = VannaDefault(model='model_name', api_key='api_key')
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
vn.ask("What are the top 10 albums by sales?")
```

注意使用Vanna.AI的在线LLM与向量库服务，需要首先到https://vanna.ai/ 去申请账号，具体请参考下一部分实测。

**如果需要使用自己本地的LLM或者向量库，比如使用自己的OpenAI账号与ChromaDB向量库，则可以扩展出自己的Vanna对象，并传入个性化配置即可。** 

```
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
def __init__(self, config=None):
ChromaDB_VectorStore.__init__(self, config=config)
OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4-...'})
```

当然这里的OpenAI\_Chat和ChromaDB\_VectorStore是Vanna已经内置支持的LLM和VectorDB。**如果你需要支持没有内置支持的LLM和vectorDB，则需要首先扩展出自己的LLM类与VectorDB类，实现必要的方法（具体可参考官方文档），然后再扩展出自己的Vanna对象**：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/72e382348a084079b48da079b4f4bf87~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=F3O8yUsD6XbN%2F5a0VVk54kRlKQ4%3D)

**【自定义关系型数据库】** 

Vanna默认支持Postgres，SQL Server，Duck DB，SQLite等关系型数据库，可直接对这一类数据库进行自动访问，实现数据对话机器人。但**如果需要连接自己企业的其他数据库，比如企业内部的Mysql或者Oracle，自需要定义一个个性化的run\_sql方法，并返回一个Pandas Dataframe即可。** 具体可参考下方的实测代码。

这里我们使用Vanna快速构建一个与数据库对话的AI智能体，直观的感受Vanna的工作过程与效果。

**【0 - 选择基础环境】** 

*   **LLM（大模型）**

选择Vanna.AI在线提供的OpenAI服务，真实环境中建议使用自己的LLM。

*   **VectorDB（向量数据库）**

选择Vanna.AI在线提供的VectorDB服务，真实环境中可根据条件灵活选择。

*   **RDBMS（关系型数据库）**

我们选择本地测试环境中的一个MySQL数据库，其中存放了一些测试的销售订单及相关实体数据：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/221a4dd02f704119a3562ddd144c1a4c~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=VYpd8qjAHOMGbg05s7Abyr3FVAo%3D)

**【1 - 申请Vanna账号】** 

由于我们使用了Vanna.AI的在线LLM与vectorDB服务。因此首先在Vanna.AI申请一个账号，并获得API-key：

![](https://p26-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/a60eea48d3b345b9990d314687f3de9e~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=SKNrOSrmB7fBlemtJ3mqNDJ%2Fxw8%3D)

设置一个Model name，用于在线的RAG model：

![](https://p26-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/61321500625546c58bce96ac62ee9b1b~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=mNis9234VOCNHzE7UEdqjiHqURI%3D)

**【2 - 构建Vanna对象】** 

使用pip安装vanna库后，首先使用如下代码创建默认的Vanna对象：

```
import vanna
from vanna.remote import VannaDefault
api_key = '上面获得的API-key'
vanna_model_name = '上面设置的model-name'
vn = VannaDefault(model=vanna_model_name, api_key=api_key)
```

由于我们需要使用自己的本地Mysql数据库，需要定义一个run\_sql方法：

```
import pandas as pd
import mysql.connector

def run_sql(sql: str) -> pd.DataFrame:
cnx = mysql.connector.connect(user='',password='',host='',database='')
cursor = cnx.cursor()
cursor.execute(sql)
result = cursor.fetchall()
columns = cursor.column_names
df = pd.DataFrame(result, columns=columns)
return df
```

将自定义的方法设置到上面创建的Vanna对象：

```
vn.run_sql = run_sql
vn.run_sql_is_set = True
```

**【3 - 训练RAG Model】** 

这里我们采用Vanna提供的一种更简单的方式：通过数据库的元数据信息构建训练计划(plan），然后交给Vanna生成RAG model：

```
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS where table_schema = 'chatdata'")
plan = vn.get_training_plan_generic(df_information_schema)
vn.train(plan=plan)
```

**【4 - 测试：与数据库对话】** 

以上的准备工作完成后，就可以与你的关系型数据库对话了：

```
vn.ask('按产品统计销售订单数量，需要有产品名称')
```

控制台可以看到输出的结果，包含了SQL和执行结果：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/cc4ad6354a354ed5aecfd440210df07f~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=U7z%2BeKYnbyNToSUa2FWUmu3CBaE%3D)

**【5 - 前端Web APP测试】** 

Vanna提供了一个内置的基于Flask框架的Web APP，可以直接运行后，通过更直观的界面与你的数据库对话，并且具有图表可视化的效果，还内置了简单的RAG Model数据的管理功能。通过这种方式启动web App：

```
from vanna.flask import VannaFlaskApp
app = VannaFlaskApp(vn)
app.run()
```

通过默认的端口访问，即可与你的数据库对话，界面如下：

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/44ade1d8e27144b9b2feec3116918641~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=cDu8Q%2BlcbCHS%2FD66Q%2BLSzgVruqY%3D)

Vanna内置了借助LLM生成可视化代码并创建图表的功能（**该功能借助了Python的一款交互式的开源可视化图表库plotly）:**

![](https://p3-sign.toutiaoimg.com/tos-cn-i-6w9my0ksvp/1761c3f8dee7452ca2c4b5c028626462~tplv-tt-origin-web:gif.jpeg?_iz=58558&from=article.pc_detail&lk3s=953192f4&x-expires=1735827169&x-signature=K%2Fv15111UOfkBAmTuTf3mUvv2hU%3D)

以上，我们深入了解了Vanna这样一个基于Python与RAG的Text2SQL交互式数据分析框架。**借助这样的框架，我们无需太多关心Prompt的构建、组装与优化，就可以快速实现一个基于Text2SQL方案的交互式数据库对话机器人**，且具备更高的正确率。此外，Vanna也提供了一些有用的关联功能：

*   RAG model数据的查询与管理API
*   基于Plotly的结果可视化API
*   前端Web APP的简单参考实现

在实际测试中，我们也发现Vanna仍然存在一些问题，但大部分问题和我们交给Vanna训练RAG model的信息不足有关；Vanna在使用的简易性上、运行速度、结果的准确性上的表现都令人印象深刻。

根据Vanna.ai官方的未来愿景规划，**Vanna旨在成为未来创建AI数据分析师的首选工具**。并在**准确性**（Text2SQL的最大挑战）、**交互能力**（能够实现交互协作，比如要人类做进一步澄清、解释答案、甚至提出后续问题），与**自主性**（主动访问必要的系统和数据甚至触发工作流程等）三个方面更加接近人类数据分析师，我们希望Vanna未来能够展示更强大的能力。

**END**

**私信“交流”**

**一起探讨AI大模型的应用实践**