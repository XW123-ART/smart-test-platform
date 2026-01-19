#!/usr/bin/env python3
"""
临时脚本：更新数据库表结构，添加ai_config表的缺少字段
"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # 获取数据库连接
    with db.engine.begin() as conn:
        # 检查ai_config表是否存在
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_config'"))
        if result.fetchone():
            print("ai_config表存在，开始更新字段...")
            
            # 检查并添加provider字段
            try:
                conn.execute(text("ALTER TABLE ai_config ADD COLUMN provider TEXT DEFAULT 'openai'")
                )
                print("✓ 已添加provider字段")
            except Exception as e:
                print(f"provider字段可能已存在：{e}")
            
            # 检查并添加api_key字段
            try:
                conn.execute(text("ALTER TABLE ai_config ADD COLUMN api_key TEXT")
                )
                print("✓ 已添加api_key字段")
            except Exception as e:
                print(f"api_key字段可能已存在：{e}")
            
            # 将openai_api_key的数据迁移到api_key字段
            try:
                conn.execute(text("UPDATE ai_config SET api_key = openai_api_key WHERE api_key IS NULL AND openai_api_key IS NOT NULL")
                )
                print("✓ 已迁移openai_api_key数据到api_key字段")
            except Exception as e:
                print(f"迁移数据时出错：{e}")
        
    print("数据库更新完成！")