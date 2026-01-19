from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify 
from flask_login import login_required, current_user 
from app import db 
from app.models import Bug, User 
from app.forms import BugForm, BugSearchForm 
from datetime import datetime 

bugs_bp = Blueprint('bugs', __name__) 

@bugs_bp.route('/bugs') 
@login_required 
def bug_list(): 
    """缺陷列表页"""
    try:
        page = request.args.get('page', 1, type=int) 
        per_page = 10 
        
        form = BugSearchForm(request.args) 
        
        # 构建查询 
        query = Bug.query 
        
        # 应用筛选条件 
        if form.keyword.data: 
            keyword = f"%{form.keyword.data}%" 
            query = query.filter(db.or_( 
                Bug.title.like(keyword), 
                Bug.description.like(keyword) 
            )) 
        
        if form.status.data: 
            query = query.filter_by(status=form.status.data) 
        
        if form.severity.data: 
            query = query.filter_by(severity=form.severity.data) 
        
        # 按创建时间倒序排列 
        query = query.order_by(Bug.created_at.desc()) 
        
        # 分页 
        bugs_pagination = query.paginate(page=page, per_page=per_page, error_out=False) 
        bugs = bugs_pagination.items 
        
        # 统计数据 
        total_bugs = Bug.query.count() 
        new_bugs = Bug.query.filter_by(status='new').count() 
        in_progress_bugs = Bug.query.filter_by(status='in_progress').count() 
        fixed_bugs = Bug.query.filter_by(status='fixed').count() 
        
        return render_template('bugs/list.html', 
                             bugs=bugs, 
                             pagination=bugs_pagination, 
                             form=form, 
                             total_bugs=total_bugs, 
                             new_bugs=new_bugs, 
                             in_progress_bugs=in_progress_bugs, 
                             fixed_bugs=fixed_bugs, 
                             title='缺陷列表')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('bugs/list.html', 
                             bugs=[], 
                             pagination=None, 
                             form=BugSearchForm(), 
                             total_bugs=0, 
                             new_bugs=0, 
                             in_progress_bugs=0, 
                             fixed_bugs=0, 
                             title='缺陷列表') 

@bugs_bp.route('/bugs/create', methods=['GET', 'POST']) 
@login_required 
def create_bug(): 
    """创建缺陷"""
    form = BugForm() 
    
    if form.validate_on_submit(): 
        try: 
            bug = Bug( 
                title=form.title.data, 
                description=form.description.data, 
                severity=form.severity.data, 
                priority=form.priority.data, 
                bug_type=form.bug_type.data, 
                environment=form.environment.data, 
                reproduction_steps=form.reproduction_steps.data, 
                expected_result=form.expected_result.data, 
                actual_result=form.actual_result.data, 
                created_by=current_user.id 
            ) 
            
            db.session.add(bug) 
            db.session.commit() 
            
            flash(f'缺陷 #{bug.id} 创建成功！', 'success') 
            return redirect(url_for('bugs.bug_detail', bug_id=bug.id)) 
            
        except Exception as e: 
            db.session.rollback() 
            flash(f'创建失败：{str(e)}', 'danger') 
    
    return render_template('bugs/create.html', form=form, title='创建缺陷') 

@bugs_bp.route('/bugs/<int:bug_id>') 
@login_required 
def bug_detail(bug_id): 
    """缺陷详情页"""
    bug = Bug.query.get_or_404(bug_id) 
    
    # 获取所有用户（用于分配下拉框） 
    users = User.query.all() 
    
    return render_template('bugs/detail.html', 
                         bug=bug, 
                         users=users, 
                         title=f'缺陷 #{bug.id}') 

@bugs_bp.route('/bugs/<int:bug_id>/edit', methods=['GET', 'POST']) 
@login_required 
def edit_bug(bug_id): 
    """编辑缺陷"""
    bug = Bug.query.get_or_404(bug_id) 
    
    # 检查权限：只有创建者或管理员可以编辑 
    if bug.created_by != current_user.id: 
        flash('您没有权限编辑此缺陷', 'danger') 
        return redirect(url_for('bugs.bug_detail', bug_id=bug_id)) 
    
    form = BugForm(obj=bug) 
    
    if form.validate_on_submit(): 
        try: 
            bug.title = form.title.data 
            bug.description = form.description.data 
            bug.severity = form.severity.data 
            bug.priority = form.priority.data 
            bug.bug_type = form.bug_type.data 
            bug.environment = form.environment.data 
            bug.reproduction_steps = form.reproduction_steps.data 
            bug.expected_result = form.expected_result.data 
            bug.actual_result = form.actual_result.data 
            bug.updated_at = datetime.utcnow() 
            
            db.session.commit() 
            flash('缺陷更新成功！', 'success') 
            return redirect(url_for('bugs.bug_detail', bug_id=bug.id)) 
            
        except Exception as e: 
            db.session.rollback() 
            flash(f'更新失败：{str(e)}', 'danger') 
    
    return render_template('bugs/edit.html', form=form, bug=bug, title=f'编辑缺陷 #{bug.id}') 

@bugs_bp.route('/bugs/<int:bug_id>/delete', methods=['POST']) 
@login_required 
def delete_bug(bug_id): 
    """删除缺陷"""
    bug = Bug.query.get_or_404(bug_id) 
    
    # 检查权限 
    if bug.created_by != current_user.id: 
        flash('您没有权限删除此缺陷', 'danger') 
        return redirect(url_for('bugs.bug_detail', bug_id=bug_id)) 
    
    try: 
        db.session.delete(bug) 
        db.session.commit() 
        flash(f'缺陷 #{bug.id} 已删除', 'success') 
    except Exception as e: 
        db.session.rollback() 
        flash(f'删除失败：{str(e)}', 'danger') 
    
    return redirect(url_for('bugs.bug_list')) 

@bugs_bp.route('/bugs/<int:bug_id>/update_status', methods=['POST']) 
@login_required 
def update_bug_status(bug_id): 
    """更新缺陷状态"""
    bug = Bug.query.get_or_404(bug_id) 
    new_status = request.form.get('status') 
    
    if new_status not in ['new', 'in_progress', 'fixed', 'closed', 'reopened']: 
        flash('无效的状态', 'danger') 
        return redirect(url_for('bugs.bug_detail', bug_id=bug_id)) 
    
    try: 
        old_status = bug.status 
        bug.status = new_status 
        
        # 如果状态变为已关闭，记录关闭时间 
        if new_status == 'closed' and old_status != 'closed': 
            bug.closed_at = datetime.utcnow() 
        
        # 如果从已关闭重新打开，清除关闭时间 
        if new_status in ['new', 'in_progress', 'reopened'] and old_status == 'closed': 
            bug.closed_at = None 
        
        bug.updated_at = datetime.utcnow() 
        db.session.commit() 
        
        flash(f'状态已从 {bug.get_status_display()} 更新为 {bug.get_status_display()}', 'success') 
    except Exception as e: 
        db.session.rollback() 
        flash(f'状态更新失败：{str(e)}', 'danger') 
    
    return redirect(url_for('bugs.bug_detail', bug_id=bug_id)) 

@bugs_bp.route('/bugs/<int:bug_id>/assign', methods=['POST']) 
@login_required 
def assign_bug(bug_id): 
    """分配缺陷给用户"""
    bug = Bug.query.get_or_404(bug_id) 
    assignee_id = request.form.get('assignee_id') 
    
    if assignee_id: 
        try: 
            user = User.query.get(int(assignee_id)) 
            if user: 
                bug.assigned_to = user.id 
                bug.updated_at = datetime.utcnow() 
                db.session.commit() 
                flash(f'已分配给 {user.username}', 'success') 
            else: 
                flash('用户不存在', 'danger') 
        except Exception as e: 
            db.session.rollback() 
            flash(f'分配失败：{str(e)}', 'danger') 
    else: 
        # 取消分配 
        bug.assigned_to = None 
        bug.updated_at = datetime.utcnow() 
        db.session.commit() 
        flash('已取消分配', 'success') 
    
    return redirect(url_for('bugs.bug_detail', bug_id=bug_id)) 

@bugs_bp.route('/api/bugs/<int:bug_id>', methods=['GET']) 
@login_required 
def get_bug_json(bug_id): 
    """获取缺陷JSON数据（用于API）"""
    bug = Bug.query.get_or_404(bug_id) 
    return jsonify(bug.to_dict())