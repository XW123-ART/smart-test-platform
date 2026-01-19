from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """用户模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """设置密码（加密存储）"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典，用于JSON响应"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Bug(db.Model):
    """缺陷模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # 状态：new, in_progress, fixed, closed, reopened
    status = db.Column(db.String(20), default='new')
    
    # 严重程度：critical, high, medium, low
    severity = db.Column(db.String(20), default='medium')
    
    # 优先级：p0, p1, p2, p3
    priority = db.Column(db.String(10), default='p2')
    
    # 缺陷类型：functional, performance, security, ui, compatibility
    bug_type = db.Column(db.String(30), default='functional')
    
    # 环境：development, test, production
    environment = db.Column(db.String(20), default='test')
    
    # 复现步骤
    reproduction_steps = db.Column(db.Text)
    
    # 预期结果
    expected_result = db.Column(db.Text)
    
    # 实际结果
    actual_result = db.Column(db.Text)
    
    # AI辅助字段
    ai_suggested_title = db.Column(db.String(200))
    ai_suggested_category = db.Column(db.String(30))
    
    # 关联字段
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    # 关系
    creator = db.relationship('User', foreign_keys=[created_by], backref=db.backref('created_bugs', lazy='dynamic'))
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref=db.backref('assigned_bugs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Bug {self.id}: {self.title}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'severity': self.severity,
            'priority': self.priority,
            'bug_type': self.bug_type,
            'environment': self.environment,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'creator_name': self.creator.username if self.creator else None,
            'assignee_name': self.assignee.username if self.assignee else None
        }
    
    def get_status_display(self):
        """获取状态的中文显示"""
        status_map = {
            'new': '新建',
            'in_progress': '处理中',
            'fixed': '已修复',
            'closed': '已关闭',
            'reopened': '重新打开'
        }
        return status_map.get(self.status, self.status)
    
    def get_severity_display(self):
        """获取严重程度的中文显示"""
        severity_map = {
            'critical': '致命',
            'high': '严重',
            'medium': '一般',
            'low': '轻微'
        }
        return severity_map.get(self.severity, self.severity)
    
    def get_priority_display(self):
        """获取优先级的中文显示"""
        priority_map = {
            'p0': 'P0（最高）',
            'p1': 'P1（高）',
            'p2': 'P2（中）',
            'p3': 'P3（低）'
        }
        return priority_map.get(self.priority, self.priority)

# 缺陷和测试用例的多对多关联表
bug_testcase_association = db.Table('bug_testcase_association',
    db.Column('bug_id', db.Integer, db.ForeignKey('bug.id'), primary_key=True),
    db.Column('testcase_id', db.Integer, db.ForeignKey('test_case.id'), primary_key=True)
)

class TestCase(db.Model):
    """测试用例模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)  # 测试步骤，JSON格式存储
    expected_result = db.Column(db.Text, nullable=False)
    
    # 状态：not_run, passed, failed, blocked
    status = db.Column(db.String(20), default='not_run')
    
    # 优先级：p0, p1, p2, p3
    priority = db.Column(db.String(10), default='p2')
    
    # 测试类型：functional, regression, smoke, performance, security
    test_type = db.Column(db.String(30), default='functional')
    
    # 所属模块
    module = db.Column(db.String(50))
    
    # 前置条件
    preconditions = db.Column(db.Text)
    
    # 关联字段
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 与缺陷的多对多关系（通过关联表）
    bugs = db.relationship('Bug',
                          secondary=bug_testcase_association,
                          backref=db.backref('linked_test_cases', lazy='dynamic'))
    
    # 关系
    creator = db.relationship('User', foreign_keys=[created_by],
                               backref=db.backref('created_test_cases', lazy='dynamic'))
    
    def __repr__(self):
        return f'<TestCase {self.id}: {self.title}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'steps': self.steps,
            'expected_result': self.expected_result,
            'status': self.status,
            'priority': self.priority,
            'test_type': self.test_type,
            'module': self.module,
            'preconditions': self.preconditions,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'creator_name': self.creator.username if self.creator else None,
            'bug_count': len(self.bugs)
        }
    
    def get_status_display(self):
        """获取状态的中文显示"""
        status_map = {
            'not_run': '未执行',
            'passed': '通过',
            'failed': '失败',
            'blocked': '阻塞'
        }
        return status_map.get(self.status, self.status)
    
    def get_status_class(self):
        """获取状态的CSS类"""
        status_classes = {
            'not_run': 'secondary',
            'passed': 'success',
            'failed': 'danger',
            'blocked': 'warning'
        }
        return status_classes.get(self.status, 'secondary')
    
    def get_priority_display(self):
        """获取优先级的中文显示"""
        priority_map = {
            'p0': 'P0（最高）',
            'p1': 'P1（高）',
            'p2': 'P2（中）',
            'p3': 'P3（低）'
        }
        return priority_map.get(self.priority, self.priority)
    
    @property
    def bug_count(self):
        """获取关联的缺陷数量"""
        return len(self.bugs)

class AIConfig(db.Model):
    """AI配置模型"""
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(20), default='openai')  # AI服务提供商
    api_key = db.Column(db.String(200))  # 通用API密钥字段
    ai_enabled = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AIConfig id={self.id} provider={self.provider} enabled={self.ai_enabled}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'provider': self.provider,
            'api_key': self.api_key,
            'ai_enabled': self.ai_enabled,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
