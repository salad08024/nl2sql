"""
最终测试 OpenRouter，强制使用 .env 文件中的值
"""
import os
import re

# 直接从 .env 文件读取，不依赖环境变量
print("=" * 70)
print("步骤 1: 直接从 .env 文件读取配置")
print("=" * 70)

with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

# 解析 .env 文件（更健壮的方式）
api_key = None
base_url = None

for line in content.splitlines():
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    if 'OPENAI_API_KEY=' in line:
        api_key = line.split('OPENAI_API_KEY=', 1)[1].strip()
    elif 'OPENAI_BASE_URL=' in line:
        base_url = line.split('OPENAI_BASE_URL=', 1)[1].strip()

# 如果还是 None，尝试正则表达式
if not api_key or not base_url:
    import re
    api_key_match = re.search(r'OPENAI_API_KEY=(.+)', content)
    base_url_match = re.search(r'OPENAI_BASE_URL=(.+)', content)
    if api_key_match:
        api_key = api_key_match.group(1).strip()
    if base_url_match:
        base_url = base_url_match.group(1).strip()

print(f"API Key (从文件读取): {api_key[:30] if api_key else 'None'}...")
print(f"Base URL (从文件读取): {base_url}")
print(f"API Key 长度: {len(api_key) if api_key else 0}")
print()

# 清除环境变量，确保使用文件中的值
os.environ['OPENAI_API_KEY'] = api_key
os.environ['OPENAI_BASE_URL'] = base_url

print("=" * 70)
print("步骤 2: 测试 OpenRouter Chat API")
print("=" * 70)

from openai import OpenAI

try:
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": "https://github.com/pillarliang/py-nl2sql",
            "X-Title": "py-nl2sql"
        }
    )
    
    print("尝试调用 openai/gpt-4o-mini...")
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    print(f"✓ Chat API 成功！")
    print(f"  响应: {response.choices[0].message.content}")
    chat_model_works = True
except Exception as e:
    print(f"✗ Chat API 失败: {e}")
    chat_model_works = False

print("\n" + "=" * 70)
print("步骤 3: 测试 OpenRouter Embedding API")
print("=" * 70)

from langchain_openai import OpenAIEmbeddings

embedding_models = [
    "openai/text-embedding-ada-002",
    "text-embedding-ada-002",
]

embedding_works = False
working_embedding_model = None

for model in embedding_models:
    try:
        print(f"尝试模型: {model}...")
        embeddings = OpenAIEmbeddings(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        result = embeddings.embed_query("test")
        print(f"✓ Embedding API 成功！")
        print(f"  模型: {model}")
        print(f"  维度: {len(result)}")
        embedding_works = True
        working_embedding_model = model
        break
    except Exception as e:
        print(f"✗ {model} 失败: {str(e)[:100]}")

print("\n" + "=" * 70)
print("测试结果总结")
print("=" * 70)
print(f"Chat API: {'✓ 可用' if chat_model_works else '✗ 不可用'}")
print(f"Embedding API: {'✓ 可用' if embedding_works else '✗ 不可用'}")
if working_embedding_model:
    print(f"可用的 Embedding 模型: {working_embedding_model}")

