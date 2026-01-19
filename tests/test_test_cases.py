import pytest
from flask import url_for
from app.models import TestCase


@pytest.mark.usefixtures('init_database')
def test_test_case_list(logged_in_client):
    """测试测试用例列表页面访问"""
    response = logged_in_client.get(url_for('test_cases.test_case_list'))
    assert response.status_code == 200


@pytest.mark.usefixtures('init_database')
def test_create_test_case_form(logged_in_client):
    """测试创建测试用例表单访问"""
    response = logged_in_client.get(url_for('test_cases.create_test_case'))
    assert response.status_code == 200


@pytest.mark.usefixtures('init_database')
def test_create_test_case(logged_in_client, app):
    """测试创建测试用例"""
    response = logged_in_client.post(url_for('test_cases.create_test_case'), data={
        'title': '新测试用例',
        'description': '这是一个新的测试用例',
        'steps': '1. 步骤1\n2. 步骤2\n3. 步骤3',
        'expected_result': '预期结果',
        'preconditions': '前置条件',
        'priority': 'p2',
        'test_type': 'functional',
        'module': '测试模块',
        'status': 'not_run'
    }, follow_redirects=False)
    
    # 检查创建测试用例后是否重定向
    assert response.status_code == 302
    
    # 验证测试用例已添加到数据库
    with app.app_context():
        test_case = TestCase.query.filter_by(title='新测试用例').first()
        assert test_case is not None
        assert test_case.description == '这是一个新的测试用例'
        assert test_case.status == 'not_run'


@pytest.mark.usefixtures('init_database')
def test_invalid_create_test_case(logged_in_client):
    """测试无效创建测试用例"""
    # 测试标题太短
    response = logged_in_client.post(url_for('test_cases.create_test_case'), data={
        'title': '短标题',
        'description': '这是一个测试用例',
        'steps': '1. 步骤1',
        'expected_result': '预期结果',
        'preconditions': '前置条件',
        'priority': 'p2',
        'test_type': 'functional',
        'module': '测试模块',
        'status': 'not_run'
    }, follow_redirects=False)
    
    # 检查无效创建时是否返回创建页面
    assert response.status_code == 200
    
    # 测试描述太短
    response = logged_in_client.post(url_for('test_cases.create_test_case'), data={
        'title': '测试用例标题',
        'description': '短描述',
        'steps': '1. 步骤1',
        'expected_result': '预期结果',
        'preconditions': '前置条件',
        'priority': 'p2',
        'test_type': 'functional',
        'module': '测试模块',
        'status': 'not_run'
    }, follow_redirects=False)
    
    # 检查无效创建时是否返回创建页面
    assert response.status_code == 200


@pytest.mark.usefixtures('init_database')
def test_test_case_detail(logged_in_client):
    """测试测试用例详情页面访问"""
    response = logged_in_client.get(url_for('test_cases.test_case_detail', test_case_id=1))
    assert response.status_code == 200


@pytest.mark.usefixtures('init_database')
def test_edit_test_case(logged_in_client, app):
    """测试编辑测试用例"""
    response = logged_in_client.get(url_for('test_cases.edit_test_case', test_case_id=1))
    assert response.status_code == 200
    
    # 提交编辑
    response = logged_in_client.post(url_for('test_cases.edit_test_case', test_case_id=1), data={
        'title': '编辑后的测试用例1',
        'description': '这是编辑后的测试用例',
        'steps': '1. 编辑后的步骤1\n2. 编辑后的步骤2',
        'expected_result': '编辑后的预期结果',
        'preconditions': '编辑后的前置条件',
        'priority': 'p1',
        'test_type': 'regression',
        'module': '编辑后的模块',
        'status': 'passed'
    }, follow_redirects=False)
    
    # 检查编辑后是否重定向
    assert response.status_code == 302
    
    # 验证测试用例已更新
    with app.app_context():
        test_case = TestCase.query.get(1)
        assert test_case.title == '编辑后的测试用例1'
        assert test_case.test_type == 'regression'
        assert test_case.status == 'passed'
        assert test_case.module == '编辑后的模块'


@pytest.mark.usefixtures('init_database')
def test_delete_test_case(logged_in_client, app):
    """测试删除测试用例"""
    response = logged_in_client.post(url_for('test_cases.delete_test_case', test_case_id=1), follow_redirects=False)
    
    # 检查删除后是否重定向
    assert response.status_code == 302
    
    # 验证测试用例已从数据库中删除
    with app.app_context():
        test_case = TestCase.query.get(1)
        assert test_case is None


@pytest.mark.usefixtures('init_database')
def test_update_test_case_status(logged_in_client, app):
    """测试更新测试用例状态"""
    # 从未执行更新为通过
    response = logged_in_client.post(url_for('test_cases.update_test_case_status', test_case_id=2), data={
        'status': 'passed'
    }, follow_redirects=False)
    
    # 检查状态更新后是否重定向
    assert response.status_code == 302
    
    # 验证状态已更新
    with app.app_context():
        test_case = TestCase.query.get(2)
        assert test_case.status == 'passed'
    
    # 从通过更新为失败
    response = logged_in_client.post(url_for('test_cases.update_test_case_status', test_case_id=2), data={
        'status': 'failed'
    }, follow_redirects=True)
    
    with app.app_context():
        test_case = TestCase.query.get(2)
        assert test_case.status == 'failed'
    
    # 从失败更新为阻塞
    response = logged_in_client.post(url_for('test_cases.update_test_case_status', test_case_id=2), data={
        'status': 'blocked'
    }, follow_redirects=True)
    
    with app.app_context():
        test_case = TestCase.query.get(2)
        assert test_case.status == 'blocked'


@pytest.mark.usefixtures('init_database')
def test_link_test_case_to_bug(logged_in_client, app):
    """测试关联测试用例到缺陷"""
    # 关联测试用例到缺陷2
    response = logged_in_client.post(url_for('test_cases.link_test_case_to_bug', test_case_id=2), data={
        'bug_id': 2
    }, follow_redirects=False)
    
    # 检查关联后是否重定向
    assert response.status_code == 302
    
    # 验证测试用例已关联到缺陷
    with app.app_context():
        test_case = TestCase.query.get(2)
        assert len(test_case.bugs) == 1
        assert test_case.bugs[0].id == 2
    
    # 解除关联
    response = logged_in_client.post(url_for('test_cases.unlink_test_case_from_bug', test_case_id=2, bug_id=2), follow_redirects=False)
    
    # 检查解除关联后是否重定向
    assert response.status_code == 302
    
    # 验证测试用例已解除关联
    with app.app_context():
        test_case = TestCase.query.get(2)
        assert len(test_case.bugs) == 0
