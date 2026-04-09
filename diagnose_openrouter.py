"""
诊断 OpenRouter 兼容性问题
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("步骤 1: 检查 .env 文件配置")
print("=" * 60)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

print(f"OPENAI_API_KEY: {api_key[:30] if api_key else 'None'}...")
print(f"OPENAI_BASE_URL: {base_url}")
print()

print("=" * 60)
print("步骤 2: 检查 langchain_openai OpenAIEmbeddings 默认模型")
print("=" * 60)

from langchain_openai import OpenAIEmbeddings

# 检查默认模型
embeddings = OpenAIEmbeddings(api_key=api_key, base_url=base_url)
print(f"OpenAIEmbeddings 默认 model 参数: {getattr(embeddings, 'model', '未设置（使用默认 text-embedding-ada-002）')}")
print()

print("=" * 60)
print("步骤 3: 测试 OpenRouter Embedding API 调用")
print("=" * 60)

try:
    # 测试默认模型
    print("尝试使用默认模型调用 OpenRouter...")
    result = embeddings.embed_query("test query")
    print(f"✓ 成功！Embedding 维度: {len(result)}")
except Exception as e:
    print(f"✗ 失败: {e}")
    print()
    print("尝试使用 OpenRouter 支持的模型...")
    
    # OpenRouter 支持的常见 embedding 模型
    test_models = [
        "text-embedding-ada-002",
        "text-embedding-3-small",
        "text-embedding-3-large",
        "openai/text-embedding-ada-002",
        "openai/text-embedding-3-small",
    ]
    
    for model in test_models:
        try:
            print(f"  测试模型: {model}")
            test_emb = OpenAIEmbeddings(
                api_key=api_key,
                base_url=base_url,
                model=model
            )
            result = test_emb.embed_query("test")
            print(f"  ✓ {model} 可用！维度: {len(result)}")
            break
        except Exception as e:
            print(f"  ✗ {model} 不可用: {str(e)[:100]}")
            continue

print()
print("=" * 60)
print("步骤 4: 检查 LLM 调用")
print("=" * 60)

from openai import OpenAI

client = OpenAI(api_key=api_key, base_url=base_url)

try:
    print("测试 Chat Completions API...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print(f"✓ Chat API 调用成功！")
    print(f"  模型: {response.model}")
    print(f"  响应: {response.choices[0].message.content[:50]}")
except Exception as e:
    print(f"✗ Chat API 调用失败: {e}")

print()
print("=" * 60)
print("步骤 5: 检查结构化输出 API")
print("=" * 60)

try:
    print("测试 structured output (beta) API...")
    # 注意：OpenRouter 可能不支持 beta API
    from pydantic import BaseModel
    
    class TestResponse(BaseModel):
        answer: str
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello"}],
        response_format=TestResponse,
    )
    print(f"✓ Structured output API 可用")
except Exception as e:
    print(f"✗ Structured output API 可能不支持: {e}")
    print("  提示: OpenRouter 可能不支持 beta API，需要改用普通 API + JSON 解析")


