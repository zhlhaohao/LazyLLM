
### AlpacaPrompter带一个槽位示例
```python
p = lazyllm.AlpacaPrompter('请完成加法运算, 输入为{instruction}')
p.generate_prompt('a+b')

"""得到
You are an AI-Agent developed by LazyLLM.
Below is an instruction that describes a task, paired with extra messages such as input that provides further context if possible. Write a response that appropriately completes the request.

### Instruction:
请完成加法运算, 输入为a+b

### Response:
"""
```


### AlpacaPrompter带多个槽位示例
```python
instruction = '你是一个由LazyLLM开发的知识问答助手，你的任务是根据提供的上下文信息来回答用户的问题。上下文信息是{context}，用户的问题是{input}, 现在请你做出回答。'
prompter = lazyllm.AlpacaPrompter({"user": instruction})
module = lazyllm.OnlineChatModule('openai').prompt(prompter)
module(dict(context='广州今天气温10-30度', input='今天广州天气如何'))

"""得到
Below is an instruction that describes a task, paired with extra messages such as input that provides further context if possible. Write a response that appropriately completes the request.

### Instruction:
 你是一个由LazyLLM开发的知识问答助手，你的任务是根据提供的上下文信息来回答用户的问题。上下文信息是广州今天气温10-30度，"
"用户的问题是今天广州天气如何, 现在请你做出回答。

### Response:

"""
```

### AlpacaPrompter带extra_keys 示例
```python
tools=[dict(type='function', function=dict(name='example'))]

prompter = lazyllm.AlpacaPrompter('你是一个工具调用的Agent，我会给你提供一些工具，请根据用户输入，帮我选择最合适的工具并使用', extra_keys='input', tools=tools)
prompter.generate_prompt('帮我查询一下今天的天气')

"""得到
You are an AI-Agent developed by LazyLLM.
Below is an instruction that describes a task, paired with extra messages such as input that provides further context if possible. Write a response that appropriately completes the request.

### Instruction:
你是一个工具调用的Agent，我会给你提供一些工具，请根据用户输入，帮我选择最合适的工具并使用

Here are some extra messages you can referred to:

### input:
帮我查询一下今天的天气

### Function-call Tools. 

[{"type": "function", "function": {"name": "example"}}]

### Response:
"""
```

### ChatPrompter 带槽位示例
```python
p = lazyllm.ChatPrompter('请完成加法运算，输入为{input}')
p.generate_prompt('a+b')

"""得到
<|start_system|>You are an AI-Agent developed by LazyLLM.请完成加法运算，输入为a+b

<|end_system|>


<|Human|>:

<|Assistant|>:
"""
```

### ChatPrompter无槽位示例
```python
# 创建一个ChatPrompter, 输入字串作为system prompt
prompter = lazyllm.ChatPrompter('你是一个工具调用的Agent，我会给你提供一些工具，请根据用户输入，帮我选择最合适的工具并使用', tools=tools)

# 生成prompt: 输入的字串作为用户query
prompter.generate_prompt('帮我查询一下今天的天气')

"""得到：
<|start_system|>
You are an AI-Agent developed by LazyLLM.你是一个工具调用的Agent，我会给你提供一些工具，请根据用户输入，帮我选择最合适的工具并使用

### Function-call Tools. 

[{"type": "function", "function": {"name": "example"}}]

<|end_system|>


<|Human|>:
帮我查询一下今天的天气
<|Assistant|>:

"""
```


### ChatPrompter带history示例
```python
prompter = lazyllm.ChatPrompter('你是一个对话机器人，现在你要和用户进行友好的对话')
prompter.generate_prompt('我们聊会儿天吧', history=[['你好', '你好，我是一个对话机器人，有什么能为您服务的']])

"""得到
<|start_system|>
You are an AI-Agent developed by LazyLLM.你是一个对话机器人，现在你要和用户进行友好的对话
<|end_system|>

<|Human|>:你好<|Assistant|>:你好，我是一个对话机器人，有什么能为您服务的
<|Human|>:
我们聊会儿天吧
<|Assistant|>:

"""

prompter.generate_prompt('我们聊会儿天吧', history=[['你好', '你好，我是一个对话机器人，有什么能为您服务的']], return_dict=True)
"""得到
{'messages': [{'role': 'system', 'content': 'You are an AI-Agent developed by LazyLLM.
你是一个对话机器人，现在你要和用户进行友好的对话'}, {'role': 'user', 'content': '你好'}, {'role': 'assistant', 'content': '你好，我是一个对话机器人，有什么能为您服务的'}, {'role': 'user', 'content': '我们聊会儿天吧'}]}
"""

prompter.generate_prompt('我们聊会儿天吧', history=[dict(role='user', content='你好'), dict(role='assistant', content='你好，我是一个对话机器人，有什么能为您服务的')], return_dict=True)

"""得到
{'messages': [{'role': 'system', 'content': 'You are an AI-Agent developed by LazyLLM.
你是一个对话机器人，现在你要和用户进行友好的对话'}, {'role': 'user', 'content': '你好'}, {'role': 'assistant', 'content': '你好，我是一个对话机器人，有什么能为您服务的'}, {'role': 'user', 'content': '我们聊会儿天吧'}]}
"""
```





