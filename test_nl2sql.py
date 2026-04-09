"""
测试 py-nl2sql 项目基本功能
"""
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from py_nl2sql import LLM, DBInstance, NL2SQLWorkflow

# 初始化 LLM（会自动从 .env 读取 OPENAI_API_KEY 和 OPENAI_BASE_URL）
print("正在初始化 LLM...")
llm = LLM()

print("✓ LLM 初始化成功")
print(f"  API Key: {llm.api_key[:20]}...")
print(f"  Base URL: {llm.base_url}\n")

# 数据库配置
db_config = {
    "db_type": "mysql",
    "db_name": "classicmodels",
    "db_user": "root",
    "db_password": "1280736352Fu.",
    "db_host": "127.0.0.1",
    "db_port": "3306",
    "need_sql_sample": True,
}

print("正在初始化数据库实例...")
print("  这将连接数据库并构建 embedding 向量库（可能需要几分钟）...")
print("  注意：如果数据库为空，此步骤可能会失败\n")

try:
    instance = DBInstance(llm=llm, **db_config)
    print("✓ 数据库实例初始化成功\n")
    
    # 测试查询
    query = "what is price of 1968 Ford Mustang"
    print(f"测试查询: {query}\n")
    
    print("正在生成 SQL 并执行查询...")
    service = NL2SQLWorkflow(instance, query, llm)
    res = service.get_response()
    
    print("\n" + "="*50)
    print("查询结果:")
    print("="*50)
    print(res)
    print("="*50)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    print("\n提示: 如果数据库为空或没有表，需要先导入示例数据")


