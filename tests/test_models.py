import pytest
from app.models import User, Bug, TestCase, AIConfig


def test_user_model():
    """测试User模型"""
    # 创建测试用户
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    
    # 测试密码验证
    assert user.check_password('password123') is True
    assert user.check_password('wrongpassword') is False
    
    # 测试密码哈希值不直接等于原始密码
    assert user.password_hash != 'password123'
    
    # 测试用户表示
    assert repr(user) == '<User testuser>'
    
    # 测试数据转换为字典
    user_dict = user.to_dict()
    assert isinstance(user_dict, dict)
    assert 'id' in user_dict
    assert 'username' in user_dict
    assert 'email' in user_dict
    assert 'created_at' in user_dict


def test_bug_model():
    """测试Bug模型"""
    # 创建测试用户
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    
    # 创建测试缺陷
    bug = Bug(
        title='测试缺陷',
        description='这是一个测试缺陷',
        severity='medium',
        priority='p2',
        bug_type='functional',
        environment='test',
        created_by=user.id
    )
    
    # 测试缺陷表示
    assert repr(bug) == '<Bug None: 测试缺陷>'
    
    # 测试状态显示
    bug.status = 'new'
    assert bug.get_status_display() == '新建'
    bug.status = 'in_progress'
    assert bug.get_status_display() == '处理中'
    bug.status = 'fixed'
    assert bug.get_status_display() == '已修复'
    bug.status = 'closed'
    assert bug.get_status_display() == '已关闭'
    bug.status = 'reopened'
    assert bug.get_status_display() == '重新打开'
    
    # 测试严重程度显示
    bug.severity = 'critical'
    assert bug.get_severity_display() == '致命'
    bug.severity = 'high'
    assert bug.get_severity_display() == '严重'
    bug.severity = 'medium'
    assert bug.get_severity_display() == '一般'
    bug.severity = 'low'
    assert bug.get_severity_display() == '轻微'
    
    # 测试优先级显示
    bug.priority = 'p0'
    assert bug.get_priority_display() == 'P0（最高）'
    bug.priority = 'p1'
    assert bug.get_priority_display() == 'P1（高）'
    bug.priority = 'p2'
    assert bug.get_priority_display() == 'P2（中）'
    bug.priority = 'p3'
    assert bug.get_priority_display() == 'P3（低）'
    
    # 测试数据转换为字典
    bug_dict = bug.to_dict()
    assert isinstance(bug_dict, dict)
    assert 'id' in bug_dict
    assert 'title' in bug_dict
    assert 'description' in bug_dict
    assert 'status' in bug_dict
    assert 'severity' in bug_dict
    assert 'priority' in bug_dict


def test_test_case_model():
    """测试TestCase模型"""
    # 创建测试用户
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    
    # 创建测试用例
    test_case = TestCase(
        title='测试用例',
        description='这是一个测试用例',
        steps='1. 打开页面\n2. 点击按钮\n3. 验证结果',
        expected_result='页面显示成功',
        priority='p2',
        test_type='functional',
        module='登录模块',
        status='not_run',
        created_by=user.id
    )
    
    # 测试测试用例表示
    assert repr(test_case) == '<TestCase None: 测试用例>'
    
    # 测试状态显示
    test_case.status = 'not_run'
    assert test_case.get_status_display() == '未执行'
    test_case.status = 'passed'
    assert test_case.get_status_display() == '通过'
    test_case.status = 'failed'
    assert test_case.get_status_display() == '失败'
    test_case.status = 'blocked'
    assert test_case.get_status_display() == '阻塞'
    
    # 测试状态CSS类
    test_case.status = 'not_run'
    assert test_case.get_status_class() == 'secondary'
    test_case.status = 'passed'
    assert test_case.get_status_class() == 'success'
    test_case.status = 'failed'
    assert test_case.get_status_class() == 'danger'
    test_case.status = 'blocked'
    assert test_case.get_status_class() == 'warning'
    
    # 测试优先级显示
    test_case.priority = 'p0'
    assert test_case.get_priority_display() == 'P0（最高）'
    test_case.priority = 'p1'
    assert test_case.get_priority_display() == 'P1（高）'
    test_case.priority = 'p2'
    assert test_case.get_priority_display() == 'P2（中）'
    test_case.priority = 'p3'
    assert test_case.get_priority_display() == 'P3（低）'
    
    # 测试数据转换为字典
    test_case_dict = test_case.to_dict()
    assert isinstance(test_case_dict, dict)
    assert 'id' in test_case_dict
    assert 'title' in test_case_dict
    assert 'description' in test_case_dict
    assert 'steps' in test_case_dict
    assert 'expected_result' in test_case_dict
    assert 'status' in test_case_dict
    assert 'priority' in test_case_dict
    assert 'test_type' in test_case_dict
    assert 'module' in test_case_dict
    assert 'preconditions' in test_case_dict
    
    # 测试缺陷数量（初始为0）
    assert test_case.bug_count == 0


def test_ai_config_model():
    """测试AIConfig模型"""
    # 创建测试AI配置
    ai_config = AIConfig(
        provider='openai',
        api_key='test-api-key',
        ai_enabled=True
    )
    
    # 测试AI配置表示
    assert repr(ai_config) == '<AIConfig id=None provider=openai enabled=True>'
    
    # 测试数据转换为字典
    ai_config_dict = ai_config.to_dict()
    assert isinstance(ai_config_dict, dict)
    assert 'id' in ai_config_dict
    assert 'provider' in ai_config_dict
    assert 'api_key' in ai_config_dict
    assert 'ai_enabled' in ai_config_dict
    assert 'updated_at' in ai_config_dict
