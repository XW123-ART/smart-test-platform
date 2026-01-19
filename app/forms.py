from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField 
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError 
from app.models import User 

class RegistrationForm(FlaskForm): 
    """注册表单""" 
    username = StringField('用户名', validators=[ 
        DataRequired(message='用户名不能为空'), 
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间') 
    ]) 
    
    email = StringField('邮箱', validators=[ 
        DataRequired(message='邮箱不能为空'), 
        Email(message='请输入有效的邮箱地址') 
    ]) 
    
    password = PasswordField('密码', validators=[ 
        DataRequired(message='密码不能为空'), 
        Length(min=6, message='密码长度至少6位') 
    ]) 
    
    confirm_password = PasswordField('确认密码', validators=[ 
        DataRequired(message='请确认密码'), 
        EqualTo('password', message='两次输入的密码不一致') 
    ]) 
    
    submit = SubmitField('注册') 
    
    def validate_username(self, username): 
        """验证用户名是否已存在""" 
        user = User.query.filter_by(username=username.data).first() 
        if user: 
            raise ValidationError('该用户名已被使用，请换一个') 
    
    def validate_email(self, email): 
        """验证邮箱是否已存在""" 
        user = User.query.filter_by(email=email.data).first() 
        if user: 
            raise ValidationError('该邮箱已被注册，请换一个或尝试登录') 

class LoginForm(FlaskForm):
    """登录表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email(message='请输入有效的邮箱地址')
    ])
    
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码')
    ])
    
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class BugForm(FlaskForm):
    """缺陷表单"""
    title = StringField('缺陷标题', validators=[
        DataRequired(message='缺陷标题不能为空'),
        Length(min=5, max=200, message='标题长度5-200字符')
    ])
    
    description = TextAreaField('缺陷描述', validators=[
        DataRequired(message='请填写缺陷描述'),
        Length(min=10, message='描述至少10个字符')
    ], render_kw={"rows": 4})
    
    severity = SelectField('严重程度', choices=[
        ('critical', '致命'),
        ('high', '严重'),
        ('medium', '一般'),
        ('low', '轻微')
    ], validators=[DataRequired()])
    
    priority = SelectField('优先级', choices=[
        ('p0', 'P0（最高）'),
        ('p1', 'P1（高）'),
        ('p2', 'P2（中）'),
        ('p3', 'P3（低）')
    ], validators=[DataRequired()])
    
    bug_type = SelectField('缺陷类型', choices=[
        ('functional', '功能缺陷'),
        ('performance', '性能缺陷'),
        ('security', '安全缺陷'),
        ('ui', 'UI缺陷'),
        ('compatibility', '兼容性缺陷'),
        ('other', '其他')
    ], validators=[DataRequired()])
    
    environment = SelectField('发现环境', choices=[
        ('development', '开发环境'),
        ('test', '测试环境'),
        ('production', '生产环境')
    ], validators=[DataRequired()])
    
    reproduction_steps = TextAreaField('复现步骤', render_kw={"rows": 3})
    expected_result = TextAreaField('预期结果', render_kw={"rows": 2})
    actual_result = TextAreaField('实际结果', render_kw={"rows": 2})
    
    submit = SubmitField('提交缺陷')

class BugSearchForm(FlaskForm):
    """缺陷搜索表单"""
    keyword = StringField('关键词', validators=[Length(max=100)])
    status = SelectField('状态', choices=[
        ('', '全部状态'),
        ('new', '新建'),
        ('in_progress', '处理中'),
        ('fixed', '已修复'),
        ('closed', '已关闭'),
        ('reopened', '重新打开')
    ])
    severity = SelectField('严重程度', choices=[
        ('', '全部'),
        ('critical', '致命'),
        ('high', '严重'),
        ('medium', '一般'),
        ('low', '轻微')
    ])
    submit = SubmitField('搜索')

class TestCaseForm(FlaskForm):
    """测试用例表单"""
    title = StringField('用例标题', validators=[
        DataRequired(message='用例标题不能为空'),
        Length(min=5, max=200, message='标题长度5-200字符')
    ])
    
    description = TextAreaField('用例描述', validators=[
        DataRequired(message='请填写用例描述'),
        Length(min=10, message='描述至少10个字符')
    ], render_kw={"rows": 3})
    
    steps = TextAreaField('测试步骤', validators=[
        DataRequired(message='请填写测试步骤')
    ], render_kw={"rows": 5})
    
    expected_result = TextAreaField('预期结果', validators=[
        DataRequired(message='请填写预期结果')
    ], render_kw={"rows": 3})
    
    preconditions = TextAreaField('前置条件', render_kw={"rows": 2})
    
    priority = SelectField('优先级', choices=[
        ('p0', 'P0（最高）'),
        ('p1', 'P1（高）'),
        ('p2', 'P2（中）'),
        ('p3', 'P3（低）')
    ], validators=[DataRequired()])
    
    test_type = SelectField('测试类型', choices=[
        ('functional', '功能测试'),
        ('regression', '回归测试'),
        ('smoke', '冒烟测试'),
        ('performance', '性能测试'),
        ('security', '安全测试'),
        ('compatibility', '兼容性测试')
    ], validators=[DataRequired()])
    
    module = StringField('所属模块', validators=[
        DataRequired(message='请填写所属模块'),
        Length(max=50)
    ])
    
    status = SelectField('状态', choices=[
        ('not_run', '未执行'),
        ('passed', '通过'),
        ('failed', '失败'),
        ('blocked', '阻塞')
    ], validators=[DataRequired()])
    
    submit = SubmitField('提交用例')

class TestCaseSearchForm(FlaskForm):
    """测试用例搜索表单"""
    keyword = StringField('关键词', validators=[Length(max=100)])
    status = SelectField('状态', choices=[
        ('', '全部状态'),
        ('not_run', '未执行'),
        ('passed', '通过'),
        ('failed', '失败'),
        ('blocked', '阻塞')
    ])
    test_type = SelectField('测试类型', choices=[
        ('', '全部类型'),
        ('functional', '功能测试'),
        ('regression', '回归测试'),
        ('smoke', '冒烟测试'),
        ('performance', '性能测试')
    ])
    module = StringField('模块')
    submit = SubmitField('搜索')

class AIConfigForm(FlaskForm):
    """AI配置表单"""
    provider = SelectField('AI服务提供商', choices=[
        ('openai', 'OpenAI'),
        ('deepseek', 'DeepSeek')
    ], default='openai', validators=[DataRequired()])
    
    api_key = PasswordField('API密钥', validators=[
        Length(max=200, message='API密钥长度不能超过200字符')
    ], render_kw={
        "placeholder": "请输入您的API密钥",
        "autocomplete": "off"
    })
    
    ai_enabled = BooleanField('启用AI功能', default=True)
    
    submit = SubmitField('保存配置')
    
    def validate_api_key(self, field):
        """验证API密钥格式"""
        if field.data:
            # 根据不同提供商放宽验证要求
            # DeepSeek和OpenAI的API密钥都以sk-开头，但其他提供商可能不同
            # 只检查长度，不强制要求前缀
            if len(field.data) < 20:
                raise ValidationError('API密钥格式不正确，长度应至少20个字符')