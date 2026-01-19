import pytest
from flask import url_for
from app.models import Bug


@pytest.mark.usefixtures('init_database')
def test_bug_list(logged_in_client):
    """测试缺陷列表页面访问"""
    response = logged_in_client.get(url_for('bugs.bug_list'), follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.usefixtures('init_database')
def test_create_bug_form(logged_in_client):
    """测试创建缺陷表单访问"""
    response = logged_in_client.get(url_for('bugs.create_bug'), follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.usefixtures('init_database')
def test_create_bug(logged_in_client, app):
    """测试创建缺陷"""
    response = logged_in_client.post(url_for('bugs.create_bug'), data={
        'title': '新测试缺陷',
        'description': '这是一个新的测试缺陷',
        'severity': 'medium',
        'priority': 'p2',
        'bug_type': 'functional',
        'environment': 'test',
        'reproduction_steps': '1. 步骤1\n2. 步骤2\n3. 步骤3',
        'expected_result': '预期结果',
        'actual_result': '实际结果'
    }, follow_redirects=True)
    
    # 检查创建缺陷后是否成功
    assert response.status_code == 200
    
    # 验证缺陷已添加到数据库
    with app.app_context():
        bug = Bug.query.filter_by(title='新测试缺陷').first()
        assert bug is not None
        assert bug.description == '这是一个新的测试缺陷'
        assert bug.status == 'new'


@pytest.mark.usefixtures('init_database')
def test_invalid_create_bug(logged_in_client):
    """测试无效创建缺陷"""
    # 测试标题太短
    response = logged_in_client.post(url_for('bugs.create_bug'), data={
        'title': '短标题',
        'description': '这是一个测试缺陷',
        'severity': 'medium',
        'priority': 'p2',
        'bug_type': 'functional',
        'environment': 'test'
    }, follow_redirects=True)
    
    # 检查无效创建时是否返回创建页面
    assert response.status_code == 200
    
    # 测试描述太短
    response = logged_in_client.post(url_for('bugs.create_bug'), data={
        'title': '测试缺陷标题',
        'description': '短描述',
        'severity': 'medium',
        'priority': 'p2',
        'bug_type': 'functional',
        'environment': 'test'
    }, follow_redirects=True)
    
    # 检查无效创建时是否返回创建页面
    assert response.status_code == 200


@pytest.mark.usefixtures('init_database')
def test_bug_detail(logged_in_client):
    """测试缺陷详情页面访问"""
    response = logged_in_client.get(url_for('bugs.bug_detail', bug_id=1), follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.usefixtures('init_database')
def test_edit_bug(logged_in_client, app):
    """测试编辑缺陷"""
    response = logged_in_client.get(url_for('bugs.edit_bug', bug_id=1), follow_redirects=True)
    assert response.status_code == 200
    
    # 提交编辑
    response = logged_in_client.post(url_for('bugs.edit_bug', bug_id=1), data={
        'title': '编辑后的测试缺陷1',
        'description': '这是编辑后的测试缺陷',
        'severity': 'high',
        'priority': 'p1',
        'bug_type': 'performance',
        'environment': 'production',
        'reproduction_steps': '1. 编辑后的步骤1\n2. 编辑后的步骤2',
        'expected_result': '编辑后的预期结果',
        'actual_result': '编辑后的实际结果'
    }, follow_redirects=True)
    
    # 检查编辑后是否成功
    assert response.status_code == 200
    
    # 验证缺陷已更新
    with app.app_context():
        bug = Bug.query.get(1)
        assert bug.title == '编辑后的测试缺陷1'
        assert bug.severity == 'high'
        assert bug.priority == 'p1'
        assert bug.bug_type == 'performance'


@pytest.mark.usefixtures('init_database')
def test_delete_bug(logged_in_client, app):
    """测试删除缺陷"""
    response = logged_in_client.post(url_for('bugs.delete_bug', bug_id=1), follow_redirects=True)
    
    # 检查删除后是否成功
    assert response.status_code == 200
    
    # 验证缺陷已从数据库中删除
    with app.app_context():
        bug = Bug.query.get(1)
        assert bug is None


@pytest.mark.usefixtures('init_database')
def test_update_bug_status(logged_in_client, app):
    """测试更新缺陷状态"""
    # 从新建状态更新为处理中
    response = logged_in_client.post(url_for('bugs.update_bug_status', bug_id=2), data={
        'status': 'in_progress'
    }, follow_redirects=True)
    
    # 检查状态更新后是否成功
    assert response.status_code == 200
    
    # 验证状态已更新
    with app.app_context():
        bug = Bug.query.get(2)
        assert bug.status == 'in_progress'


@pytest.mark.usefixtures('init_database')
def test_assign_bug(logged_in_client, app):
    """测试分配缺陷"""
    # 分配缺陷给用户2
    response = logged_in_client.post(url_for('bugs.assign_bug', bug_id=2), data={
        'assignee_id': 2
    }, follow_redirects=True)
    
    # 检查分配后是否成功
    assert response.status_code == 200
    
    # 验证缺陷已分配
    with app.app_context():
        bug = Bug.query.get(2)
        assert bug.assigned_to == 2
    
    # 取消分配
    response = logged_in_client.post(url_for('bugs.assign_bug', bug_id=2), data={
        'assignee_id': ''
    }, follow_redirects=True)
    
    # 检查取消分配后是否成功
    assert response.status_code == 200
    
    # 验证缺陷已取消分配
    with app.app_context():
        bug = Bug.query.get(2)
        assert bug.assigned_to is None
    
    # 验证缺陷已取消分配
    with app.app_context():
        bug = Bug.query.get(2)
        assert bug.assigned_to is None
