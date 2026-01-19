from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建扩展实例
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# 用户加载器函数 - Flask-Login 必须要有这个函数来从会话中加载用户
@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))


def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)

    # 基础配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-for-testing-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_platform.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'  # 设置登录页面

    # 注册蓝图
    from app.main import main_bp
    from app.auth import auth_bp
    from app.bugs import bugs_bp
    from app.test_cases import test_cases_bp
    from app.ai import ai_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(bugs_bp)
    app.register_blueprint(test_cases_bp)
    app.register_blueprint(ai_bp, url_prefix='/api/ai')

    # 创建数据库表
    with app.app_context():
        from . import models
        db.create_all()

    return app