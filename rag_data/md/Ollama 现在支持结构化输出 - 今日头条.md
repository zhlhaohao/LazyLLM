[Ollama 现在支持结构化输出 - 今日头条](https://www.toutiao.com/article/7445551705720144393/?log_from=dbabb820c3953_1735128796774) 

 2024年12月6日，Ollama推出了结构化输出的新功能，允许用户通过JSON模式来定义模型输出的格式。这一更新使得我们在进行数据提取和图像处理时，能够获得更高的可靠性和一致性。

结构化输出就是让模型的回答按照我们预先设定的格式来组织，比如用JSON格式。这种方式可以规定模型的输出必须包含哪些字段（比如“name”、“capital”、“languages”），而且每个字段的类型和格式也要符合要求。

简单来说，就是先告诉模型“答案长什么样”，它就会按照这个模版去填内容。

通过结构化输出，模型的响应变得更加可控，从而**减少了后续数据处理的复杂度**。相较于传统的JSON模式，结构化输出在准确性和一致性上有了更大的提升。

结构化输出提供了更强的可靠性和一致性，尤其适用于以下几种场景：

*   **从文档中解析数据**：例如，提取合同中的关键信息（如公司名、合同金额、签订日期等）。
*   **从图像中提取数据**：如图像中的物体识别，模型返回各物体的名称、置信度、位置等信息。
*   **构建语言模型的响应**：通过结构化输出，可以将语言模型的回答限制在特定格式内，提高结果的可靠性。
*   **提供比JSON模式更一致的输出**：相比传统的自由文本输出，结构化输出能够保证返回的数据格式和内容的稳定性。

首先，我们来看看如何使用cURL发送一个结构化输出的请求。假设我们请求模型提供关于加拿大的信息，并要求输出的内容遵循一个特定的JSON架构：

```
curl -X POST http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{  "model": "llama3.1",  "messages": [{"role": "user", "content": "Tell me about Canada."}],  "stream": false,  "format": {    "type": "object",    "properties": {      "name": { "type": "string" },      "capital": { "type": "string" },      "languages": { "type": "array", "items": { "type": "string" } }    },    "required": ["name", "capital", "languages"]  }}'
```

输出将会是：

```
{  "capital": "Ottawa",  "languages": [    "English",    "French"  ],  "name": "Canada"}
```

在Python中，我们可以使用Ollama Python库结合Pydantic来进行结构化输出的处理。下面的代码演示了如何定义一个模型架构，并将其传递给Ollama进行响应处理：

```
from ollama import chatfrom pydantic import BaseModelclass Country(BaseModel):    name: str    capital: str    languages: list[str]response = chat(    messages=[{'role': 'user', 'content': 'Tell me about Canada.'}],    model='llama3.1',    format=Country.model_json_schema(),)country = Country.model_validate_json(response.message.content)print(country)
```

输出将会是：

```
name='Canada' capital='Ottawa' languages=['English', 'French']
```

在JavaScript中，我们可以通过Ollama的JavaScript库和Zod库来处理结构化输出。

以下是一个使用Zod定义数据结构并调用Ollama API的示例：

```
import ollama from 'ollama';import { z } from 'zod';import { zodToJsonSchema } from 'zod-to-json-schema';const Country = z.object({    name: z.string(),    capital: z.string(),    languages: z.array(z.string()),});const response = await ollama.chat({    model: 'llama3.1',    messages: [{ role: 'user', content: 'Tell me about Canada.' }],    format: zodToJsonSchema(Country),});const country = Country.parse(JSON.parse(response.message.content));console.log(country);
```

输出为：

```
{  name: "Canada",  capital: "Ottawa",  languages: ["English", "French"]}
```

假设我们有一段描述宠物的信息，模型将会根据我们定义的架构提取出结构化的数据：

```
from ollama import chatfrom pydantic import BaseModelclass Pet(BaseModel):    name: str    animal: str    age: int    color: str | None    favorite_toy: str | Noneclass PetList(BaseModel):    pets: list[Pet]response = chat(    messages=[{'role': 'user', 'content': '''        I have two pets.        A cat named Luna who is 5 years old and loves playing with yarn. She has grey fur.        I also have a 2 year old black cat named Loki who loves tennis balls.    '''}],    model='llama3.1',    format=PetList.model_json_schema(),)pets = PetList.model_validate_json(response.message.content)print(pets)
```

输出：

```
pets=[  Pet(name='Luna', animal='cat', age=5, color='grey', favorite_toy='yarn'),   Pet(name='Loki', animal='cat', age=2, color='black', favorite_toy='tennis balls')]
```

结构化输出不仅适用于文本数据，还可以与视觉模型结合使用。比如，我们可以让模型分析一张图片，并返回包含物体、颜色和场景等信息的结构化输出：

```
from ollama import chatfrom pydantic import BaseModelclass Object(BaseModel):    name: str    confidence: float    attributes: strclass ImageDescription(BaseModel):    summary: str    objects: list[Object]    scene: str    colors: list[str]    time_of_day: str    setting: str    text_content: str | Nonepath = 'path/to/image.jpg'response = chat(    model='llama3.2-vision',    format=ImageDescription.model_json_schema(),    messages=[{'role': 'user', 'content': 'Analyze this image and describe what you see, including any objects, the scene, colors and any text you can detect.', 'images': [path]}],    options={'temperature': 0},)image_description = ImageDescription.model_validate_json(response.message.content)print(image_description)
```

输出示例：

```
summary='A palm tree on a sandy beach with blue water and sky.'objects=[Object(name='tree', confidence=0.9, attributes='palm tree'), Object(name='beach', confidence=1.0, attributes='sand')]scene='beach'colors=['blue', 'green', 'white']time_of_day='Afternoon'setting='Outdoor'text_content=None
```

Ollama的结构化输出为数据提取和图像分析提供了强大的支持。通过定义清晰的输出结构，用户可以确保模型的输出更可靠、一致且易于解析。这一特性特别适合需要精确控制输出格式的场景，如从文档或图像中提取数据。

> 更多参考：https://ollama.com/blog/structured-outputs