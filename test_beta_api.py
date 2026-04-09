"""
测试 OpenRouter 是否支持 beta API (structured output)
"""
import os
import json
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel

load_dotenv(find_dotenv(), override=True)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

from openai import OpenAI

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    default_headers={
        "HTTP-Referer": "https://github.com/pillarliang/py-nl2sql",
        "X-Title": "py-nl2sql"
    }
)

class TestResponse(BaseModel):
    answer: str

print("=" * 70)
print("测试 1: Beta API (structured output)")
print("=" * 70)

try:
    response = client.beta.chat.completions.parse(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": 'Respond with JSON: {"answer": "hello"}'}],
        response_format=TestResponse,
    )
    print("✓ Beta API 可用！")
    print(f"  响应: {response.choices[0].message.content}")
    beta_api_works = True
except Exception as e:
    print(f"✗ Beta API 不可用: {e}")
    beta_api_works = False

print("\n" + "=" * 70)
print("测试 2: 普通 API + JSON 解析（替代方案）")
print("=" * 70)

try:
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that responds only with valid JSON."
            },
            {
                "role": "user",
                "content": 'Respond with JSON only in this format: {"answer": "hello"}'
            }
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    content = response.choices[0].message.content
    print("✓ 普通 API + JSON 格式可用！")
    print(f"  响应: {content}")
    # 尝试解析
    data = json.loads(content)
    test_resp = TestResponse(**data)
    print(f"  解析成功: {test_resp}")
    json_mode_works = True
except Exception as e:
    print(f"✗ 失败: {e}")
    json_mode_works = False

print("\n" + "=" * 70)
print("推荐方案")
print("=" * 70)
if beta_api_works:
    print("✓ 使用 Beta API (client.beta.chat.completions.parse)")
else:
    print("✗ Beta API 不可用，使用普通 API + JSON 模式")
    if json_mode_works:
        print("  → 推荐使用: response_format={'type': 'json_object'} + JSON 解析")


