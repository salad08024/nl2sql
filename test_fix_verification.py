"""
验证 OpenRouter 修复是否成功
"""
import os
import sys
from dotenv import load_dotenv, find_dotenv

# 确保加载 .env
load_dotenv(find_dotenv(), override=True)

print("=" * 70)
print("步骤 1: 验证环境变量")
print("=" * 70)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

print(f"OPENAI_API_KEY: {api_key[:30] if api_key else 'None'}...")
print(f"OPENAI_BASE_URL: {base_url}")
print()

if not api_key or not base_url:
    print("❌ 环境变量未正确加载！")
    sys.exit(1)

if base_url != "https://openrouter.ai/api/v1":
    print(f"⚠️ 警告: Base URL 不是 OpenRouter 地址: {base_url}")

print("✓ 环境变量检查通过\n")

print("=" * 70)
print("步骤 2: 测试 LLM 类初始化")
print("=" * 70)

try:
    from py_nl2sql.models.llm import LLM
    
    llm = LLM()
    print(f"✓ LLM 初始化成功")
    print(f"  API Key: {llm.api_key[:30]}...")
    print(f"  Base URL: {llm.base_url}")
    
    # 检查 embedding 模型
    print("\n步骤 3: 测试 Embedding 模型")
    emb_model = llm.embedding_model
    print(f"✓ Embedding 模型初始化成功")
    print(f"  模型名称: {getattr(emb_model, 'model', '未设置')}")
    
    # 快速测试 embedding（只测试一个短文本）
    try:
        test_emb = emb_model.embed_query("test")
        print(f"✓ Embedding 测试成功，维度: {len(test_emb)}")
    except Exception as e:
        print(f"✗ Embedding 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n步骤 4: 测试 Chat API")
    try:
        response = llm.get_response("Say hello in one word")
        print(f"✓ Chat API 测试成功")
        print(f"  响应: {response}")
    except Exception as e:
        print(f"✗ Chat API 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n步骤 5: 测试 Structured Response (自动 fallback)")
    try:
        from py_nl2sql.constants.type import DecomposeQueryResponse
        
        test_response = llm.get_structured_response(
            "Decompose this query: what is the price of products",
            DecomposeQueryResponse
        )
        print(f"✓ Structured Response 测试成功")
        print(f"  响应类型: {type(test_response)}")
        print(f"  响应内容: {test_response}")
    except Exception as e:
        print(f"✗ Structured Response 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ 所有基础测试通过！")
    print("=" * 70)
    print("\n现在可以尝试运行完整的测试:")
    print("  python test_nl2sql.py")
    
except Exception as e:
    print(f"✗ LLM 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


