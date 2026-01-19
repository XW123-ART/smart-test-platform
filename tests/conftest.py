import pytest
from app import create_app, db
from app.models import User, Bug, TestCase, AIConfig
from flask_login import login_user

@pytest.fixture(scope='module')
def app():
    """创建测试应用"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False  # 测试时禁用CSRF保护
    })
    
    with app.app_context():
        from app import models
        db.create_all()
    
    yield app
    
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    """初始化测试数据库"""
    with app.app_context():
        # 确保所有表都被创建
        db.create_all()
        
        # 创建测试用户
        user1 = User(username='testuser1', email='test1@example.com')
        user1.set_password('password123')
        
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('password123')
        
        # 添加到数据库
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        # 创建测试缺陷
        bug1 = Bug(
            title='测试缺陷1',
            description='这是一个测试缺陷',
            severity='medium',
            priority='p2',
            bug_type='functional',
            environment='test',
            created_by=user1.id
        )
        
        bug2 = Bug(
            title='测试缺陷2',
            description='这是另一个测试缺陷',
            severity='high',
            priority='p1',
            bug_type='performance',
            environment='production',
            created_by=user2.id
        )
        
        # 创建测试用例
        test_case1 = TestCase(
            title='测试用例1',
            description='这是一个测试用例',
            steps='1. 打开页面\n2. 点击按钮\n3. 验证结果',
            expected_result='页面显示成功',
            priority='p2',
            test_type='functional',
            module='登录模块',
            status='not_run',
            created_by=user1.id
        )
        
        test_case2 = TestCase(
            title='测试用例2',
            description='这是另一个测试用例',
            steps='1. 输入数据\n2. 提交表单\n3. 验证响应',
            expected_result='表单提交成功',
            priority='p1',
            test_type='regression',
            module='注册模块',
            status='passed',
            created_by=user2.id
        )
        
        # 创建测试AI配置
        ai_config = AIConfig(provider='openai', api_key='test-api-key', ai_enabled=False)
        
        # 添加到数据库
        db.session.add(bug1)
        db.session.add(bug2)
        db.session.add(test_case1)
        db.session.add(test_case2)
        db.session.add(ai_config)
        db.session.commit()
    
    yield db
    
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def test_user(app, init_database):
    """创建测试用户"""
    with app.app_context():
        user = User.query.filter_by(username='testuser1').first()
        return user

@pytest.fixture(scope='function')
def logged_in_client(client):
    """创建已登录的测试客户端"""
    with client:
        # 通过实际登录请求来获取会话cookie
        client.post('/auth/login', data={
            'email': 'test1@example.com',
            'password': 'password123',
            'remember': False
        })
        yield client
