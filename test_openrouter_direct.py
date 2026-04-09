"""
直接测试 OpenRouter API 调用
"""
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

print(f"API Key: {api_key[:30] if api_key else 'None'}...")
print(f"Base URL: {base_url}\n")

from openai import OpenAI

# 测试 1: Chat API with openai/ 前缀
print("=" * 60)
print("测试 1: Chat API - openai/gpt-4o-mini")
print("=" * 60)

try:
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": "https://github.com/pillarliang/py-nl2sql",
            "X-Title": "py-nl2sql"
        }
    )
    
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello in one word"}],
        max_tokens=10
    )
    print(f"✓ 成功！")
    print(f"  模型: {response.model}")
    print(f"  响应: {response.choices[0].message.content}")
    print(f"  使用的模型名称: openai/gpt-4o-mini")
except Exception as e:
    print(f"✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 2: Embedding API
print("\n" + "=" * 60)
print("测试 2: Embedding API - openai/text-embedding-ada-002")
print("=" * 60)

from langchain_openai import OpenAIEmbeddings

try:
    embeddings = OpenAIEmbeddings(
        api_key=api_key,
        base_url=base_url,
        model="openai/text-embedding-ada-002"
    )
    result = embeddings.embed_query("test")
    print(f"✓ 成功！")
    print(f"  Embedding 维度: {len(result)}")
    print(f"  使用的模型名称: openai/text-embedding-ada-002")
except Exception as e:
    print(f"✗ 失败: {e}")
    import traceback
    traceback.print_exc()


