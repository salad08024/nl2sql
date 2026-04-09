"""
修复 OpenRouter 兼容性问题的测试脚本
逐步测试每个修复点
"""
import os
from dotenv import load_dotenv, find_dotenv

# 强制从 .env 文件加载，覆盖已存在的环境变量
env_path = find_dotenv()
print(f"加载 .env 文件: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

print("=" * 70)
print("问题诊断和修复方案")
print("=" * 70)
print(f"\n当前配置:")
print(f"  API Key: {api_key[:30] if api_key else 'None'}...")
print(f"  Base URL: {base_url}\n")

print("=" * 70)
print("问题 1: OpenAIEmbeddings 默认模型")
print("=" * 70)

from langchain_openai import OpenAIEmbeddings

# 测试不同的 embedding 模型格式
embedding_models_to_test = [
    "text-embedding-ada-002",  # 默认
    "openai/text-embedding-ada-002",  # OpenRouter 格式
    "openai/text-embedding-3-small",  # OpenRouter 格式
    "openai/text-embedding-3-large",  # OpenRouter 格式
]

working_embedding_model = None

for model in embedding_models_to_test:
    try:
        print(f"\n测试模型: {model}")
        emb = OpenAIEmbeddings(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        result = emb.embed_query("test")
        print(f"  ✓ 成功！维度: {len(result)}")
        working_embedding_model = model
        break
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "deactivated" in error_msg:
            print(f"  ✗ 认证错误（可能是 base_url 问题）")
        else:
            print(f"  ✗ 失败: {error_msg[:100]}")

if working_embedding_model:
    print(f"\n✓ 找到可用的 embedding 模型: {working_embedding_model}")
else:
    print("\n⚠ 未找到可用的 embedding 模型")

print("\n" + "=" * 70)
print("问题 2: Chat Completions API 和模型名称")
print("=" * 70)

from openai import OpenAI

# OpenRouter 需要 HTTP Referer 和 X-Title headers (可选，但某些情况下需要)
# 但主要是确保 API key 正确传递
print(f"\n使用 API Key: {api_key[:20] if api_key else 'None'}...")
print(f"使用 Base URL: {base_url}")

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    # OpenRouter 可能需要额外的 headers
    default_headers={
        "HTTP-Referer": "https://github.com/pillarliang/py-nl2sql",  # 可选，用于分析
        "X-Title": "py-nl2sql"  # 可选
    }
)

# 测试不同的模型名称格式
chat_models_to_test = [
    "gpt-4o-mini",  # 默认
    "openai/gpt-4o-mini",  # OpenRouter 格式
]

working_chat_model = None

for model in chat_models_to_test:
    try:
        print(f"\n测试模型: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print(f"  ✓ 成功！响应: {response.choices[0].message.content}")
        working_chat_model = model
        break
    except Exception as e:
        print(f"  ✗ 失败: {str(e)[:150]}")

if working_chat_model:
    print(f"\n✓ 找到可用的 chat 模型: {working_chat_model}")
else:
    print("\n⚠ 未找到可用的 chat 模型")

print("\n" + "=" * 70)
print("问题 3: Structured Output (beta API)")
print("=" * 70)

# OpenRouter 可能不支持 beta API，需要测试
from pydantic import BaseModel

class TestResponse(BaseModel):
    answer: str

beta_api_works = False

try:
    print("\n测试 beta.chat.completions.parse API...")
    response = client.beta.chat.completions.parse(
        model=working_chat_model or "gpt-4o-mini",
        messages=[{"role": "user", "content": 'Respond with {"answer": "hello"}'}],
        response_format=TestResponse,
    )
    print(f"  ✓ Beta API 可用！")
    beta_api_works = True
except Exception as e:
    print(f"  ✗ Beta API 不可用: {str(e)[:150]}")
    print(f"  → 需要使用普通 API + JSON 解析替代")

print("\n" + "=" * 70)
print("修复建议总结")
print("=" * 70)

print("\n需要修改的文件和内容:")
print("\n1. py_nl2sql/models/llm.py")
print("   - embedding_model: 指定模型为 openai/text-embedding-ada-002 或兼容模型")
print("   - get_structured_response: 如果 beta API 不支持，改用普通 API + JSON 解析")
print("   - 模型名称: 可能需要添加 openai/ 前缀")

print("\n2. .env 文件确认")
print(f"   - OPENAI_BASE_URL={base_url} ✓" if base_url == "https://openrouter.ai/api/v1" else f"   - OPENAI_BASE_URL 需要设置为: https://openrouter.ai/api/v1")

print("\n3. py_nl2sql/constants/type.py")
print("   - LLMModel.Default 可能需要改为 openai/gpt-4o-mini")

print("\n推荐的 embedding 模型:", working_embedding_model or "需要手动测试")
print("推荐的 chat 模型:", working_chat_model or "需要手动测试")
print("Beta API 是否可用:", "是" if beta_api_works else "否（需要修改代码）")

