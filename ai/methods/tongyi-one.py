from openai import OpenAI

# 导入配置文件
from ai.config import DASHSCOPE_API_KEY

client = OpenAI(
    # 从配置文件读取API密钥
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"},
    ],
    # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
    # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
    # extra_body={"enable_thinking": False},
)
print(completion.model_dump_json())

if __name__ == "__main__":
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "你是谁？"}],
    )
    print(completion.model_dump_json())
