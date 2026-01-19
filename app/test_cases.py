from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import TestCase, Bug, bug_testcase_association
from app.forms import TestCaseForm, TestCaseSearchForm
from datetime import datetime
import json

test_cases_bp = Blueprint('test_cases', __name__)

@test_cases_bp.route('/test-cases')
@login_required
def test_case_list():
    """测试用例列表页"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    form = TestCaseSearchForm(request.args)
    
    # 构建查询
    query = TestCase.query
    
    # 应用筛选条件
    if form.keyword.data:
        keyword = f"%{form.keyword.data}%"
        query = query.filter(db.or_(
            TestCase.title.like(keyword),
            TestCase.description.like(keyword)
        ))
    
    if form.status.data:
        query = query.filter_by(status=form.status.data)
    
    if form.test_type.data:
        query = query.filter_by(test_type=form.test_type.data)
    
    if form.module.data:
        module_filter = f"%{form.module.data}%"
        query = query.filter(TestCase.module.like(module_filter))
    
    # 按创建时间倒序排列
    query = query.order_by(TestCase.created_at.desc())
    
    # 分页
    test_cases_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    test_cases = test_cases_pagination.items
    
    # 统计数据
    total_cases = TestCase.query.count()
    not_run_cases = TestCase.query.filter_by(status='not_run').count()
    passed_cases = TestCase.query.filter_by(status='passed').count()
    failed_cases = TestCase.query.filter_by(status='failed').count()
    blocked_cases = TestCase.query.filter_by(status='blocked').count()
    
    return render_template('test_cases/list.html',
                         test_cases=test_cases,
                         pagination=test_cases_pagination,
                         form=form,
                         total_cases=total_cases,
                         not_run_cases=not_run_cases,
                         passed_cases=passed_cases,
                         failed_cases=failed_cases,
                         blocked_cases=blocked_cases,
                         title='测试用例列表')

@test_cases_bp.route('/test-cases/create', methods=['GET', 'POST'])
@login_required
def create_test_case():
    """创建测试用例"""
    form = TestCaseForm()
    
    if form.validate_on_submit():
        try:
            test_case = TestCase(
                title=form.title.data,
                description=form.description.data,
                steps=form.steps.data,
                expected_result=form.expected_result.data,
                preconditions=form.preconditions.data,
                priority=form.priority.data,
                test_type=form.test_type.data,
                module=form.module.data,
                status=form.status.data,
                created_by=current_user.id
            )
            
            db.session.add(test_case)
            db.session.commit()
            
            flash(f'测试用例 #{test_case.id} 创建成功！', 'success')
            return redirect(url_for('test_cases.test_case_detail', test_case_id=test_case.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'danger')
    
    return render_template('test_cases/create.html', form=form, title='创建测试用例')

@test_cases_bp.route('/test-cases/<int:test_case_id>')
@login_required
def test_case_detail(test_case_id):
    """测试用例详情页"""
    test_case = TestCase.query.get_or_404(test_case_id)
    
    # 获取关联的缺陷
    linked_bugs = test_case.bugs
    
    # 获取所有缺陷（用于关联下拉框）
    all_bugs = Bug.query.all()
    
    return render_template('test_cases/detail.html',
                         test_case=test_case,
                         linked_bugs=linked_bugs,
                         all_bugs=all_bugs,
                         title=f'测试用例 #{test_case.id}')

@test_cases_bp.route('/test-cases/<int:test_case_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_test_case(test_case_id):
    """编辑测试用例"""
    test_case = TestCase.query.get_or_404(test_case_id)
    
    # 检查权限：只有创建者可以编辑
    if test_case.created_by != current_user.id:
        flash('您没有权限编辑此测试用例', 'danger')
        return redirect(url_for('test_cases.test_case_list'))
    
    form = TestCaseForm(obj=test_case)
    
    if form.validate_on_submit():
        try:
            test_case.title = form.title.data
            test_case.description = form.description.data
            test_case.steps = form.steps.data
            test_case.expected_result = form.expected_result.data
            test_case.preconditions = form.preconditions.data
            test_case.priority = form.priority.data
            test_case.test_type = form.test_type.data
            test_case.module = form.module.data
            test_case.status = form.status.data
            test_case.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('测试用例更新成功！', 'success')
            return redirect(url_for('test_cases.test_case_detail', test_case_id=test_case.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    
    return render_template('test_cases/edit.html', form=form, test_case=test_case, 
                         title=f'编辑测试用例 #{test_case.id}')

@test_cases_bp.route('/test-cases/<int:test_case_id>/delete', methods=['POST'])
@login_required
def delete_test_case(test_case_id):
    """删除测试用例"""
    test_case = TestCase.query.get_or_404(test_case_id)
    
    # 检查权限
    if test_case.created_by != current_user.id:
        flash('您没有权限删除此测试用例', 'danger')
        return redirect(url_for('test_cases.test_case_detail', test_case_id=test_case_id))
    
    test_case_id_deleted = test_case.id
    
    try:
        db.session.delete(test_case)
        db.session.commit()
        flash(f'测试用例 #{test_case_id_deleted} 已删除', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    
    return redirect(url_for('test_cases.test_case_list'))

@test_cases_bp.route('/test-cases/<int:test_case_id>/update-status', methods=['POST'])
@login_required
def update_test_case_status(test_case_id):
    """更新测试用例状态"""
    test_case = TestCase.query.get_or_404(test_case_id)
    new_status = request.form.get('status')
    
    if new_status not in ['not_run', 'passed', 'failed', 'blocked']:
        flash('无效的状态', 'danger')
        return redirect(url_for('test_cases.test_case_detail', test_case_id=test_case_id))
    
    try:
        test_case.status = new_status
        test_case.updated_at = datetime.utcnow()
        db.session.commit()
        
        status_display = test_case.get_status_display()
        flash(f'状态已更新为 {status_display}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'状态更新失败：{str(e)}', 'danger')
    
    return redirect(url_for('test_cases.test_case_detail', test_case_id=test_case_id))

@test_cases_bp.route('/test-cases/<int:test_case_id>/link-bug', methods=['POST'])
@login_required
def link_test_case_to_bug(test_case_id):
    """关联测试用例到缺陷"""
    test_case = TestCase.query.get_or_404(test_case_id)
    bug_id = request.form.get('bug_id')
    
    if not bug_id:
        flash('请选择缺陷', 'danger')
        return redirect(url_for('test_cases.test_case_detail', test_case_id=test_case_id))
    
    try:
        bug = Bug.query.get(int(bug_id))
        if not bug:
            flash('缺陷不存在', 'danger')
            return redirect(url_for('test_cases.test_case_detail', test_case_id=test_case_id))
        
        # 检查是否已经关联
        if bug in test_case.bugs:
            flash('已经关联过此缺陷', 'info')
        else:
            test_case.bugs.append(bug)
            db.session.commit()
            flash(f'已关联到缺陷 #{bug.id}', 'success')
            
    except Exception as e:
        db.session.rollback()
        flash(f'关联失败：{str(e)}', 'danger')
    
    return redirect(url_for('test_cases.test_case_detail', test_case_id=test_case_id))

@test_cases_bp.route('/test-cases/<int:test_case_id>/unlink-bug/<int:bug_id>', methods=['POST'])
@login_required
def unlink_test_case_from_bug(test_case_id, bug_id):
    """解除测试用例与缺陷的关联"""
    test_case = TestCase.query.get_or_404(test_case_id)
    
    try:
        bug = Bug.query.get(int(bug_id))
        if bug and bug in test_case.bugs:
            test_case.bugs.remove(bug)
            db.session.commit()
            flash('已解除关联', 'success')
        else:
            flash('未找到关联关系', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'解除关联失败：{str(e)}', 'danger')
    
    return redirect(url_for('test_cases.test_case_detail', test_case_id=test_case_id))

@test_cases_bp.route('/api/test-cases/<int:test_case_id>/bugs')
@login_required
def get_test_case_bugs(test_case_id):
    """获取测试用例关联的缺陷列表（API）"""
    test_case = TestCase.query.get_or_404(test_case_id)
    bugs = [{'id': bug.id, 'title': bug.title, 'status': bug.status} for bug in test_case.bugs]
    return jsonify({'bugs': bugs})