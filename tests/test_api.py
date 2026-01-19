import pytest
from flask import url_for


@pytest.mark.usefixtures('init_database')
def test_bug_api(logged_in_client):
    """测试缺陷API"""
    # 获取缺陷详情API
    response = logged_in_client.get(url_for('bugs.get_bug_json', bug_id=2))
    assert response.status_code == 200
    assert response.is_json
    bug_data = response.get_json()
    assert 'id' in bug_data
    assert 'title' in bug_data
    assert 'description' in bug_data
    assert bug_data['id'] == 2
    assert bug_data['title'] == '测试缺陷2'


@pytest.mark.usefixtures('init_database')
def test_test_case_bugs_api(logged_in_client):
    """测试测试用例关联缺陷API"""
    # 获取测试用例关联的缺陷列表
    response = logged_in_client.get(url_for('test_cases.get_test_case_bugs', test_case_id=2))
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert 'bugs' in data
    assert isinstance(data['bugs'], list)
    # 初始状态下，测试用例2没有关联缺陷
    assert len(data['bugs']) == 0


@pytest.mark.usefixtures('init_database')
def test_ai_api_disabled(logged_in_client):
    """测试AI功能未启用时的API"""
    # 测试优化缺陷描述API
    response = logged_in_client.post(url_for('ai.api_improve_bug'), json={
        'description': '这是一个测试缺陷描述',
        'bug_type': 'functional'
    })
    
    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'AI功能未启用'
    
    # 测试优化测试用例API
    response = logged_in_client.post(url_for('ai.api_improve_test_case'), json={
        'description': '这是一个测试用例描述',
        'module': '测试模块'
    })
    
    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'AI功能未启用'
    
    # 测试分类缺陷API
    response = logged_in_client.post(url_for('ai.api_classify_bug'), json={
        'description': '这是一个测试缺陷描述'
    })
    
    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'AI功能未启用'
    
    # 测试建议相似缺陷API
    response = logged_in_client.post(url_for('ai.api_suggest_similar_bugs'), json={
        'description': '这是一个测试缺陷描述'
    })
    
    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'AI功能未启用'


@pytest.mark.usefixtures('init_database')
def test_ai_connection_api(logged_in_client):
    """测试AI连接API"""
    response = logged_in_client.post(url_for('ai.api_test_connection'))
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert 'connected' in data
    assert 'message' in data
    # 由于AI功能未启用，连接应该失败
    assert data['connected'] is False


def test_main_pages(client):
    """测试主页面访问"""
    # 测试首页访问
    response = client.get('/')
    assert response.status_code == 200
    
    # 测试关于页面（如果有）
    # 假设没有关于页面，返回404
    response = client.get('/about')
    assert response.status_code == 404
