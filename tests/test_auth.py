import pytest
from flask import url_for


def test_register_page(client):
    """测试注册页面访问"""
    response = client.get(url_for('auth.register'))
    assert response.status_code == 200
    assert '注册' in response.data.decode('utf-8')


def test_login_page(client):
    """测试登录页面访问"""
    response = client.get(url_for('auth.login'))
    assert response.status_code == 200
    assert '登录' in response.data.decode('utf-8')


def test_valid_registration(client, app):
    """测试有效注册"""
    response = client.post(url_for('auth.register'), data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    # 检查注册后是否重定向到登录页面
    assert response.status_code == 200
    
    # 验证用户已添加到数据库
    with app.app_context():
        from app.models import User
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.username == 'newuser'


def test_invalid_registration(client):
    """测试无效注册"""
    # 测试密码不匹配
    response = client.post(url_for('auth.register'), data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'wrongpassword'
    })
    
    # 检查是否返回注册页面，而不是重定向
    assert response.status_code == 200
    assert url_for('auth.register') in response.request.url


def test_valid_login(client):
    """测试有效登录"""
    response = client.post(url_for('auth.login'), data={
        'email': 'test1@example.com',
        'password': 'password123',
        'remember': False
    }, follow_redirects=True)
    
    # 检查登录后是否重定向到首页
    assert response.status_code == 200
    assert url_for('main.index') in response.request.url


def test_invalid_login(client):
    """测试无效登录"""
    # 测试密码错误
    response = client.post(url_for('auth.login'), data={
        'email': 'test1@example.com',
        'password': 'wrongpassword',
        'remember': False
    }, follow_redirects=False)
    
    # 检查登录失败时是否返回登录页面
    assert response.status_code == 200
    assert url_for('auth.login') in response.request.url
    
    # 测试邮箱不存在
    response = client.post(url_for('auth.login'), data={
        'email': 'nonexistent@example.com',
        'password': 'password123',
        'remember': False
    }, follow_redirects=False)
    
    # 检查登录失败时是否返回登录页面
    assert response.status_code == 200
    assert url_for('auth.login') in response.request.url


def test_logout(client):
    """测试登出功能"""
    # 先登录
    client.post(url_for('auth.login'), data={
        'email': 'test1@example.com',
        'password': 'password123',
        'remember': False
    }, follow_redirects=True)
    
    # 然后登出
    response = client.get(url_for('auth.logout'), follow_redirects=True)
    
    # 检查登出后是否重定向到首页
    assert response.status_code == 200
    assert url_for('main.index') in response.request.url
    
    # 检查是否包含登录和注册链接
    assert '登录' in response.data.decode('utf-8')
    assert '注册' in response.data.decode('utf-8')


def test_protected_page_access(client):
    """测试未登录用户访问受保护页面"""
    # 测试访问缺陷列表页
    response = client.get(url_for('bugs.bug_list'), follow_redirects=True)
    assert response.status_code == 200
    # 检查是否重定向到登录页面
    assert url_for('auth.login') in response.request.url
    
    # 测试访问测试用例列表页
    response = client.get(url_for('test_cases.test_case_list'), follow_redirects=True)
    assert response.status_code == 200
    # 检查是否重定向到登录页面
    assert url_for('auth.login') in response.request.url
    
    # 测试访问创建缺陷页
    response = client.get(url_for('bugs.create_bug'), follow_redirects=True)
    assert response.status_code == 200
    # 检查是否重定向到登录页面
    assert url_for('auth.login') in response.request.url
