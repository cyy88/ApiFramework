import os
from pathlib import Path
from openai import OpenAI
from ai.config import DASHSCOPE_API_KEY

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
file_object = client.files.create(file=Path("百炼系列手机产品介绍.docx"), purpose="file-extract")
completion = client.chat.completions.create(
    model="qwen-long",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[
        {'role': 'system', 'content': f'fileid://{file_object.id}'},
        {'role': 'user', 'content': '这篇文章讲了什么？'}
    ]
)
print(completion.model_dump_json())

if __name__ == '__main__':
    print(completion.model_dump_json())