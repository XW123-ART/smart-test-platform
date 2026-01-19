from flask import Blueprint, render_template, redirect, url_for, flash, request 
from flask_login import login_user, logout_user, login_required, current_user 
from app import db 
from app.models import User 
from app.forms import RegistrationForm, LoginForm 

# 创建认证蓝图 
auth_bp = Blueprint('auth', __name__) 

@auth_bp.route('/register', methods=['GET', 'POST']) 
def register():
    """用户注册"""
    # 如果用户已登录，跳转到首页
    if current_user.is_authenticated:
        flash('您已登录，如需注册新账号请先退出登录', 'info')
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # 创建新用户
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            
            # 保存到数据库
            db.session.add(user)
            db.session.commit()
            
            flash('注册成功！请登录您的账号', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'注册失败：{str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form, title='注册')

@auth_bp.route('/login', methods=['GET', 'POST']) 
def login():
    """用户登录"""
    # 如果用户已登录，跳转到首页
    if current_user.is_authenticated:
        flash('您已登录', 'info')
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # 查找用户
        user = User.query.filter_by(email=form.email.data).first()
        
        # 验证用户和密码
        if user is None or not user.check_password(form.password.data):
            flash('邮箱或密码错误', 'danger')
        else:
            # 登录用户
            login_user(user, remember=form.remember.data)
            
            # 获取重定向页面
            next_page = request.args.get('next')
            
            # 显示欢迎消息
            flash(f'欢迎回来，{user.username}！', 'success')
            
            # 重定向到目标页面或首页
            return redirect(next_page if next_page else url_for('main.index'))
    
    return render_template('auth/login.html', form=form, title='登录')

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('main.index'))