from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.forms import AIConfigForm
from app.services.ai_service import AIService
from app.models import AIConfig
from app import db
import os

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/config', methods=['GET', 'POST'])
@login_required
def ai_config():
    """AI配置页面"""
    # 获取当前配置
    ai_config = AIConfig.query.first()
    if not ai_config:
        ai_config = AIConfig()
        db.session.add(ai_config)
        db.session.commit()
    
    form = AIConfigForm()
    
    if request.method == 'GET':
        form.provider.data = ai_config.provider or 'openai'
        form.api_key.data = ai_config.api_key or ''
        form.ai_enabled.data = ai_config.ai_enabled
    
    if form.validate_on_submit():
        try:
            # 测试AI连接（如果启用了AI）
            if form.ai_enabled.data and form.api_key.data:
                ai_service = AIService(api_key=form.api_key.data, provider=form.provider.data)
                if not ai_service.test_connection():
                    # 获取详细错误信息
                    error_msg = getattr(ai_service, 'last_error', 'API密钥验证失败，请检查密钥是否正确')
                    flash(f'API密钥验证失败：{error_msg}', 'danger')
                    return render_template('ai/config.html', form=form, config=ai_config, title='AI配置')
            
            # 保存配置
            ai_config.provider = form.provider.data
            ai_config.api_key = form.api_key.data
            ai_config.ai_enabled = form.ai_enabled.data
            
            db.session.commit()
            
            # 更新环境变量
            if ai_config.ai_enabled and ai_config.api_key:
                os.environ['OPENAI_API_KEY'] = ai_config.api_key
            
            flash('AI配置保存成功', 'success')
            return redirect(url_for('ai.ai_config'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'保存配置时出错：{str(e)}', 'danger')
    
    return render_template('ai/config.html', form=form, config=ai_config, title='AI配置')

@ai_bp.route('/improve-bug', methods=['POST'])
@login_required
def api_improve_bug():
    """API：优化缺陷描述"""
    data = request.json
    user_input = data.get('description', '')
    bug_type = data.get('bug_type', '')
    
    if not user_input:
        return jsonify({'error': '缺少描述内容'}), 400
    
    # 获取系统配置
    ai_config = AIConfig.query.first()
    
    # 创建AI服务实例
    provider = ai_config.provider if ai_config else 'openai'
    api_key = ai_config.api_key if ai_config else os.getenv('OPENAI_API_KEY')
    ai_enabled = ai_config.ai_enabled if ai_config else False
    
    if not ai_enabled:
        return jsonify({'error': 'AI功能未启用'}), 400
    
    ai_service = AIService(api_key=api_key, provider=provider)
    
    # 调用AI服务
    result = ai_service.improve_bug_description(user_input, bug_type)
    
    return jsonify(result)

@ai_bp.route('/improve-test-case', methods=['POST'])
@login_required
def api_improve_test_case():
    """API：优化测试用例"""
    data = request.json
    description = data.get('description', '')
    module = data.get('module', '')
    
    if not description:
        return jsonify({'error': '缺少测试用例描述'}), 400
    
    # 获取系统配置
    ai_config = AIConfig.query.first()
    
    # 创建AI服务实例
    provider = ai_config.provider if ai_config else 'openai'
    api_key = ai_config.api_key if ai_config else os.getenv('OPENAI_API_KEY')
    ai_enabled = ai_config.ai_enabled if ai_config else False
    
    if not ai_enabled:
        return jsonify({'error': 'AI功能未启用'}), 400
    
    ai_service = AIService(api_key=api_key, provider=provider)
    
    # 调用AI服务
    result = ai_service.improve_test_case(description, module)
    
    return jsonify(result)

@ai_bp.route('/classify-bug', methods=['POST'])
@login_required
def api_classify_bug():
    """API：分类缺陷"""
    data = request.json
    description = data.get('description', '')
    
    if not description:
        return jsonify({'error': '缺少描述内容'}), 400
    
    # 获取系统配置
    ai_config = AIConfig.query.first()
    
    # 创建AI服务实例
    provider = ai_config.provider if ai_config else 'openai'
    api_key = ai_config.api_key if ai_config else os.getenv('OPENAI_API_KEY')
    ai_enabled = ai_config.ai_enabled if ai_config else False
    
    if not ai_enabled:
        return jsonify({'error': 'AI功能未启用'}), 400
    
    ai_service = AIService(api_key=api_key, provider=provider)
    
    # 调用AI服务
    classification = ai_service.classify_bug(description)
    
    return jsonify(classification)

@ai_bp.route('/suggest-similar-bugs', methods=['POST'])
@login_required
def api_suggest_similar_bugs():
    """API：建议相似缺陷"""
    data = request.json
    description = data.get('description', '')
    
    if not description:
        return jsonify({'error': '缺少描述内容'}), 400
    
    # 这里需要从数据库获取现有缺陷
    from app.models import Bug
    existing_bugs = Bug.query.limit(50).all()
    
    # 准备数据
    bugs_data = []
    for bug in existing_bugs:
        bugs_data.append({
            'id': bug.id,
            'title': bug.title,
            'description': bug.description
        })
    
    # 获取系统配置
    ai_config = AIConfig.query.first()
    
    # 创建AI服务实例
    provider = ai_config.provider if ai_config else 'openai'
    api_key = ai_config.api_key if ai_config else os.getenv('OPENAI_API_KEY')
    ai_enabled = ai_config.ai_enabled if ai_config else False
    
    if not ai_enabled:
        return jsonify({'error': 'AI功能未启用'}), 400
    
    ai_service = AIService(api_key=api_key, provider=provider)
    
    # 调用AI服务
    similar_bugs = ai_service.suggest_similar_bugs(description, bugs_data)
    
    return jsonify({'similar_bugs': similar_bugs})

@ai_bp.route('/test-connection', methods=['POST'])
@login_required
def api_test_connection():
    """API：测试AI连接"""
    # 获取系统配置
    ai_config = AIConfig.query.first()
    
    # 创建AI服务实例
    provider = ai_config.provider if ai_config else 'openai'
    api_key = ai_config.api_key if ai_config else os.getenv('OPENAI_API_KEY')
    ai_enabled = ai_config.ai_enabled if ai_config else False
    ai_service = AIService(api_key=api_key, provider=provider)
    
    # 测试连接
    if not ai_enabled or not api_key:
        return jsonify({'connected': False, 'message': 'AI功能未启用或未配置API密钥'})
    
    connected = ai_service.test_connection()
    message = "连接成功" if connected else "连接失败，请检查API密钥"
    
    return jsonify({'connected': connected, 'message': message})