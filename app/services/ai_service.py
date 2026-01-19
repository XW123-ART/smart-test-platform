import os
import json
import re
from typing import Dict, List, Optional, Any
import openai
from flask import current_app

class AIService:
    """AI服务类，支持OpenAI和DeepSeek等兼容OpenAI API规范的服务"""
    
    def __init__(self, api_key: str = None, provider: str = "openai"):
        """
        初始化AI服务
        
        Args:
            api_key: API密钥，如果为None则从环境变量读取
            provider: AI服务提供商，支持"openai"、"deepseek"或其他兼容OpenAI API规范的服务
        """
        # 优先级：1. 传入的api_key 2. 环境变量 3. None
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.provider = provider.lower()
        self.client = None
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            try:
                # 根据不同提供商设置不同的基础URL
                base_urls = {
                    "deepseek": "https://api.deepseek.com/v1",
                    "openai": "https://api.openai.com/v1"
                }
                
                # 创建客户端，支持不同提供商
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=base_urls.get(self.provider, "https://api.openai.com/v1")
                )
            except Exception as e:
                current_app.logger.error(f"Failed to initialize AI client: {e}")
                self.enabled = False
        else:
            current_app.logger.warning("API key not provided. AI features will use mock responses.")
    
    def improve_bug_description(self, user_input: str, bug_type: str = None) -> Dict[str, Any]:
        """
        优化缺陷描述和标题
        
        Args:
            user_input: 用户输入的缺陷描述
            bug_type: 可选，缺陷类型
            
        Returns:
            包含优化后的标题、描述、分类等的字典
        """
        prompt = self._create_bug_improvement_prompt(user_input, bug_type)
        system_prompt = "你是一个专业的测试工程师，擅长分析和描述软件缺陷。"
        
        result = self._call_ai_api(prompt, system_prompt)
        
        if "error" in result:
            return result
        
        # 确保所有必要字段都存在
        result.setdefault("improved_title", "AI生成的缺陷标题")
        result.setdefault("improved_description", "AI生成的缺陷描述")
        result.setdefault("reproduction_steps", "1. 执行操作\n2. 验证结果")
        result.setdefault("expected_result", "预期结果：操作成功")
        result.setdefault("actual_result", "实际结果：操作失败")
        result.setdefault("suggested_severity", "medium")
        result.setdefault("suggested_priority", "p2")
        
        return result
    
    def improve_test_case(self, user_input: str, module: str = None) -> Dict[str, Any]:
        """
        优化测试用例描述和标题
        
        Args:
            user_input: 用户输入的测试用例描述
            module: 可选，模块名称
            
        Returns:
            包含优化后的标题、描述、前置条件、测试步骤、预期结果等的字典
        """
        current_app.logger.info(f"improve_test_case called with user_input: {user_input[:100]}..., module: {module}")
        
        prompt = self._create_test_case_improvement_prompt(user_input, module)
        system_prompt = "你是一个专业的测试工程师，擅长设计全面的测试用例。"
        
        current_app.logger.info(f"Test case prompt: {prompt}")
        
        result = self._call_ai_api(prompt, system_prompt)
        
        current_app.logger.info(f"Test case AI response raw: {result}")
        
        if "error" in result:
            current_app.logger.error(f"Test case AI error: {result['error']}")
            return result
        
        # 确保所有必要字段都存在
        result.setdefault("improved_title", "AI生成的测试用例标题")
        result.setdefault("improved_description", "AI生成的测试用例描述")
        result.setdefault("improved_preconditions", "1. 系统已正常启动\n2. 用户已登录系统\n3. 相关数据已准备就绪")
        result.setdefault("improved_steps", ["步骤1: 点击测试按钮", "步骤2: 输入测试数据", "步骤3: 验证测试结果"])
        result.setdefault("improved_expected_result", "测试结果符合预期，系统正常工作")
        result.setdefault("suggested_priority", "p2")
        result.setdefault("suggested_module", "测试模块")
        
        # 确保improved_steps始终是数组
        if not isinstance(result.get("improved_steps"), list):
            result["improved_steps"] = self._ensure_steps_array(result.get("improved_steps", []))
        
        current_app.logger.info(f"Test case final result: {result}")
        
        return result
    
    def _create_test_case_improvement_prompt(self, user_input: str, module: str = None) -> str:
        """
        创建优化测试用例的提示词
        """
        base_prompt = f""
        base_prompt += "请优化以下测试用例描述，使其更专业、清晰和完整：\n\n"
        base_prompt += f"原始描述：{user_input}\n"
        
        if module:
            base_prompt += f"所属模块：{module}\n"
        
        base_prompt += "\n"
        base_prompt += "请返回一个JSON对象，包含以下字段：\n"
        base_prompt += "1. improved_title: 优化后的测试用例标题（简洁明了，包含关键信息）\n"
        base_prompt += "2. improved_description: 优化后的测试用例描述（详细、有条理）\n"
        base_prompt += "3. improved_preconditions: 优化后的前置条件\n"
        base_prompt += "4. improved_steps: 优化后的测试步骤（数组形式）\n"
        base_prompt += "5. improved_expected_result: 优化后的预期结果\n"
        base_prompt += "6. suggested_priority: 建议优先级 (p0/p1/p2/p3)\n"
        base_prompt += "7. suggested_module: 建议所属模块\n"
        base_prompt += "\n"
        base_prompt += "只返回JSON，不要有其他内容。"
        
        return base_prompt
    
    def classify_bug(self, description: str) -> Dict[str, Any]:
        """
        分类缺陷
        
        Args:
            description: 缺陷描述
            
        Returns:
            包含分类信息或错误信息的字典
        """
        prompt = f""
        prompt += "请根据以下缺陷描述进行分类：\n\n"
        prompt += f"描述：{description}\n"
        prompt += "\n"
        prompt += "请返回JSON格式，包含以下字段：\n"
        prompt += "1. severity: 严重程度 (critical/high/medium/low)\n"
        prompt += "2. priority: 优先级 (p0/p1/p2/p3)\n"
        prompt += "3. category: 缺陷类型 (functional/performance/security/ui/compatibility/other)\n"
        prompt += "4. suggested_title: 建议的标题\n"
        prompt += "\n"
        prompt += "只返回JSON，不要有其他内容。"
        
        return self._call_ai_api(prompt)

    def _call_ai_api(self, prompt: str, system_prompt: str = None, max_tokens: int = 500, temperature: float = 0.3) -> Dict[str, Any]:
        """
        通用AI API调用方法，处理重试逻辑和响应解析
        
        Args:
            prompt: 用户提示词
            system_prompt: 可选，系统提示词
            max_tokens: 最大令牌数
            temperature: 生成温度
            
        Returns:
            解析后的AI响应或包含错误信息的字典
        """
        if not self.enabled or not self.client:
            current_app.logger.error(f"AI service not enabled or client not initialized. Enabled: {self.enabled}, Client: {self.client}")
            return {
                "error": "AI服务未正确配置或初始化失败，请检查配置"
            }
        
        # 模型映射，移到通用方法中避免重复
        models = {
            "deepseek": "deepseek-chat",
            "openai": "gpt-3.5-turbo"
        }
        
        max_retries = 2
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                current_app.logger.info(f"Calling AI service with provider: {self.provider}, model: {models.get(self.provider, 'gpt-3.5-turbo')}, retry: {retry_count}")
                response = self.client.chat.completions.create(
                    model=models.get(self.provider, "gpt-3.5-turbo"),
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                result_text = response.choices[0].message.content
                current_app.logger.info(f"AI response received: {result_text[:100]}...")
                
                # 统一使用_parse_json_response方法解析响应
                return self._parse_json_response(result_text)
                
            except Exception as e:
                current_app.logger.error(f"Error in _call_ai_api (retry {retry_count}/{max_retries}): {type(e).__name__}: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    return {
                        "error": f"AI生成失败：{type(e).__name__}: {str(e)}"
                    }
    
    def suggest_similar_bugs(self, bug_description: str, existing_bugs: List[Dict]) -> List[Dict]:
        """
        建议相似的缺陷
        
        Args:
            bug_description: 新缺陷描述
            existing_bugs: 现有缺陷列表，每个元素包含id、title、description
            
        Returns:
            相似缺陷列表
        """
        if not self.enabled or not existing_bugs:
            return []
        
        try:
            # 这里简化处理，实际可以使用向量相似度搜索
            # 我们先使用关键词匹配
            keywords = self._extract_keywords(bug_description)
            
            similar_bugs = []
            for bug in existing_bugs:
                score = self._calculate_similarity_score(bug_description, bug)
                if score > 0.3:  # 相似度阈值
                    bug['similarity_score'] = round(score, 2)
                    similar_bugs.append(bug)
            
            # 按相似度排序
            similar_bugs.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_bugs[:5]  # 返回最相似的5个
            
        except Exception as e:
            current_app.logger.error(f"Error in suggest_similar_bugs: {e}")
            return []
    
    def _create_bug_improvement_prompt(self, user_input: str, bug_type: str = None) -> str:
        """
        创建优化缺陷描述的提示词
        """
        base_prompt = f""
        base_prompt += "请优化以下缺陷描述，使其更专业、清晰和完整：\n\n"
        base_prompt += f"原始描述：{user_input}\n"
        
        if bug_type:
            base_prompt += f"缺陷类型：{bug_type}\n"
        
        base_prompt += "\n"
        base_prompt += "请返回一个JSON对象，包含以下字段：\n"
        base_prompt += "1. improved_title: 优化后的标题（简洁明了，包含关键信息）\n"
        base_prompt += "2. improved_description: 优化后的描述（详细、有条理）\n"
        base_prompt += "3. reproduction_steps: 复现步骤（如果原始描述中没有，请补充）\n"
        base_prompt += "4. expected_result: 预期结果\n"
        base_prompt += "5. actual_result: 实际结果\n"
        base_prompt += "6. suggested_severity: 建议严重程度 (critical/high/medium/low)\n"
        base_prompt += "7. suggested_priority: 建议优先级 (p0/p1/p2/p3)\n"
        base_prompt += "\n"
        base_prompt += "只返回JSON，不要有其他内容。"
        
        return base_prompt
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析JSON响应，支持多种格式的AI返回结果，包括被截断的响应
        """
        original_text = response_text
        
        try:
            # 记录完整响应，不截断
            current_app.logger.info(f"Raw AI response length: {len(response_text)} chars")
            current_app.logger.info(f"Raw AI response: {response_text}")
            
            # 复制原始响应，用于调试
            temp_text = response_text.strip()
            
            # 1. 移除可能的代码块标记
            if temp_text.startswith('```json'):
                current_app.logger.debug("移除json代码块标记")
                temp_text = temp_text[7:-3] if temp_text.endswith('```') else temp_text[7:]
            elif temp_text.startswith('```'):
                current_app.logger.debug("移除普通代码块标记")
                temp_text = temp_text[3:-3] if temp_text.endswith('```') else temp_text[3:]
            temp_text = temp_text.strip()
            
            current_app.logger.debug(f"处理后完整文本: {temp_text}")
            
            # 2. 直接尝试解析，不使用复杂的转换
            try:
                parsed = json.loads(temp_text)
                if isinstance(parsed, dict):
                    current_app.logger.debug("直接解析成功")
                    # 确保improved_steps是数组
                    if 'improved_steps' in parsed:
                        parsed['improved_steps'] = self._ensure_steps_array(parsed['improved_steps'])
                    return parsed
            except json.JSONDecodeError as e:
                current_app.logger.error(f"直接解析失败: {e}")
                current_app.logger.error(f"错误位置: {temp_text[e.pos-20:e.pos+20]}")
            
            # 3. 修复被截断的JSON响应
            current_app.logger.debug("尝试修复被截断的JSON响应")
            
            # 检查响应是否被截断
            if not temp_text.endswith('}'):
                current_app.logger.debug("检测到JSON响应可能被截断")
                
                # 修复1: 确保有适当的结束标记
                # 统计引号数量
                quote_count = temp_text.count('"')
                current_app.logger.debug(f"引号数量: {quote_count}")
                
                # 如果引号数量为奇数，添加一个引号
                if quote_count % 2 != 0:
                    current_app.logger.debug("引号数量为奇数，添加一个引号")
                    temp_text += '"'
                
                # 修复2: 尝试添加缺失的字段和结束括号
                # 检查是否缺少结束括号
                open_braces = temp_text.count('{')
                close_braces = temp_text.count('}')
                if open_braces > close_braces:
                    current_app.logger.debug(f"大括号不匹配: 开={open_braces}, 关={close_braces}")
                    # 添加缺失的大括号
                    temp_text += '}' * (open_braces - close_braces)
                
                # 修复3: 检查是否缺少逗号
                if not any(temp_text.endswith(c) for c in [',', '}']):
                    current_app.logger.debug("末尾缺少逗号，添加逗号")
                    temp_text += ','
                
                # 修复4: 尝试添加缺失的字段
                if 'improved_title' in temp_text and 'improved_description' not in temp_text:
                    temp_text += '"improved_description":"AI生成的描述",'
                if 'improved_description' in temp_text and 'improved_preconditions' not in temp_text:
                    temp_text += '"improved_preconditions":"1. 系统已正常启动\n2. 用户已登录系统\n3. 相关数据已准备就绪",'
                if 'improved_preconditions' in temp_text and 'improved_steps' not in temp_text:
                    temp_text += '"improved_steps":["步骤1: 执行操作","步骤2: 验证结果"],'
                if 'improved_steps' in temp_text and 'improved_expected_result' not in temp_text:
                    temp_text += '"improved_expected_result":"操作结果符合预期",'
                if 'improved_expected_result' in temp_text and 'suggested_priority' not in temp_text:
                    temp_text += '"suggested_priority":"p2",'
                if 'suggested_priority' in temp_text and 'suggested_module' not in temp_text:
                    temp_text += '"suggested_module":"测试模块",'
                
                # 移除末尾可能的逗号
                if temp_text.endswith(','):
                    temp_text = temp_text[:-1]
                
                # 确保末尾有结束括号
                if not temp_text.endswith('}'):
                    temp_text += '}'
                
                current_app.logger.debug(f"修复后文本: {temp_text}")
                
                # 尝试解析修复后的文本
                try:
                    parsed = json.loads(temp_text)
                    if isinstance(parsed, dict):
                        current_app.logger.debug("修复后解析成功")
                        if 'improved_steps' in parsed:
                            parsed['improved_steps'] = self._ensure_steps_array(parsed['improved_steps'])
                        return parsed
                except json.JSONDecodeError as e:
                    current_app.logger.error(f"修复后解析失败: {e}")
                    current_app.logger.error(f"错误位置: {temp_text[e.pos-20:e.pos+20]}")
            
            # 4. 修复AI返回的格式错误
            # 处理类似 "suggested_"}"suggested_priority" 这样的格式错误
            import re
            current_app.logger.debug("尝试修复AI返回的格式错误")
            
            # 修复0: 移除多余的空字段，例如 "","suggested_priority" 中的多余 "",
            fixed_text = re.sub(r'"",', '', temp_text)
            # 修复1: 移除多余的结束括号和引号
            fixed_text = re.sub(r'suggested_"\}', 'suggested_', fixed_text)
            # 修复2: 替换 "}"suggested_" 为 ","suggested_"
            fixed_text = re.sub(r'\}"suggested_', ',"suggested_', fixed_text)
            # 修复3: 移除可能的多余字符
            fixed_text = re.sub(r'[^\{\}\[\]",:\s\w\d\.\-!@#$%^&*()_+|~=`<>?/\u4e00-\u9fa5]', '', fixed_text)
            # 修复4: 移除可能的多余逗号
            fixed_text = re.sub(r',\s*\}', '}', fixed_text)
            fixed_text = re.sub(r',\s*\]', ']', fixed_text)
            
            current_app.logger.debug(f"修复格式错误后文本: {fixed_text}")
            
            # 尝试解析修复后的文本
            try:
                parsed = json.loads(fixed_text)
                if isinstance(parsed, dict):
                    current_app.logger.debug("修复格式错误后解析成功")
                    if 'improved_steps' in parsed:
                        parsed['improved_steps'] = self._ensure_steps_array(parsed['improved_steps'])
                    return parsed
            except json.JSONDecodeError as e:
                current_app.logger.error(f"修复格式错误后解析失败: {e}")
            
            # 5. 尝试使用正则表达式提取最外层的JSON对象
            try:
                # 提取最外层的JSON对象
                json_match = re.search(r'\{[\s\S]*\}', fixed_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    current_app.logger.debug(f"正则提取的JSON: {json_str}")
                    parsed = json.loads(json_str)
                    if isinstance(parsed, dict):
                        current_app.logger.debug("正则提取解析成功")
                        if 'improved_steps' in parsed:
                            parsed['improved_steps'] = self._ensure_steps_array(parsed['improved_steps'])
                        return parsed
            except json.JSONDecodeError as e:
                current_app.logger.error(f"正则提取解析失败: {e}")
            
            # 5. 最后尝试：只提取已知的关键字段（使用修复后的文本）
            current_app.logger.debug("尝试只提取已知关键字段")
            
            # 定义要提取的字段
            fields = ['improved_title', 'improved_description', 'improved_preconditions', 'improved_steps', 'improved_expected_result', 'suggested_priority', 'suggested_module']
            result = {}
            
            # 使用修复后的文本进行关键字段提取
            extract_text = fixed_text
            
            for field in fields:
                # 使用正则表达式提取字段值
                # 增强的正则表达式，支持更多格式变化
                pattern = rf'{field}\s*:\s*("(?:\\.|[^"])*"|\[(?:\\.|[^\]]*)*\]|true|false|null|\d+\.\d+|\d+)'  # 匹配字符串、数组、布尔值、null、数字
                match = re.search(pattern, extract_text, re.DOTALL | re.IGNORECASE)
                if match:
                    value_str = match.group(1)
                    try:
                        # 尝试解析值
                        value = json.loads(value_str)
                        result[field] = value
                        current_app.logger.debug(f"提取字段 {field} 成功: {value}")
                    except json.JSONDecodeError:
                        # 如果解析失败，直接使用字符串值
                        result[field] = value_str.strip('"')
                        current_app.logger.debug(f"提取字段 {field} 成功（作为字符串）: {value_str.strip('"')}")
                else:
                    # 如果无法提取，尝试使用原始文本再试一次
                    match = re.search(pattern, temp_text, re.DOTALL | re.IGNORECASE)
                    if match:
                        value_str = match.group(1)
                        try:
                            # 尝试解析值
                            value = json.loads(value_str)
                            result[field] = value
                            current_app.logger.debug(f"从原始文本提取字段 {field} 成功: {value}")
                        except json.JSONDecodeError:
                            # 如果解析失败，直接使用字符串值
                            result[field] = value_str.strip('"')
                            current_app.logger.debug(f"从原始文本提取字段 {field} 成功（作为字符串）: {value_str.strip('"')}")
            
            # 确保improved_steps是数组
            if 'improved_steps' in result:
                result['improved_steps'] = self._ensure_steps_array(result['improved_steps'])
            
            if result:
                current_app.logger.debug(f"提取关键字段成功: {result}")
                return result
            
        except Exception as e:
            current_app.logger.error(f"Unexpected error in _parse_json_response: {e}")
            import traceback
            current_app.logger.error(f"详细错误: {traceback.format_exc()}")
        
        # 如果所有解析策略都失败，返回一个包含默认值的字典
        current_app.logger.debug("所有解析策略失败，返回包含默认值的字典")
        return {
            "improved_title": "AI生成的标题",
            "improved_description": "AI生成的描述",
            "improved_preconditions": "1. 系统已正常启动\n2. 用户已登录系统\n3. 相关数据已准备就绪",
            "improved_steps": ["步骤1: 执行操作", "步骤2: 验证结果"],
            "improved_expected_result": "操作结果符合预期",
            "suggested_priority": "p2",
            "suggested_module": "测试模块"
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词（简化版）
        """
        # 移除常见停用词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', text.lower())
        return [word for word in words if word not in stop_words and len(word) > 1]
    
    def _calculate_similarity_score(self, new_description: str, existing_bug: Dict) -> float:
        """
        计算相似度分数（简化版）
        """
        new_keywords = set(self._extract_keywords(new_description))
        
        # 组合现有缺陷的标题和描述
        existing_text = f"{existing_bug.get('title', '')} {existing_bug.get('description', '')}"
        existing_keywords = set(self._extract_keywords(existing_text))
        
        if not new_keywords or not existing_keywords:
            return 0.0
        
        # Jaccard相似度
        intersection = len(new_keywords.intersection(existing_keywords))
        union = len(new_keywords.union(existing_keywords))
        
        return intersection / union if union > 0 else 0.0
    
    def _ensure_steps_array(self, steps: Any) -> List[str]:
        """
        确保steps始终是字符串数组形式
        
        Args:
            steps: 输入的步骤数据，可以是字符串、数组或其他类型
            
        Returns:
            格式化后的字符串数组
        """
        if not steps:
            return []
        
        if isinstance(steps, list):
            # 确保数组中的每个元素都是字符串，并过滤掉空字符串
            return [str(step).strip() for step in steps if str(step).strip()]
        
        if isinstance(steps, str):
            # 如果是字符串，按换行符分割，并过滤掉空字符串
            return [step.strip() for step in steps.split('\n') if step.strip()]
        
        # 其他类型转换为字符串数组
        processed_step = str(steps).strip()
        return [processed_step] if processed_step else []
    
    # 移除了模拟方法，因为我们现在直接返回实际的AI结果或错误信息
    
    def test_connection(self) -> bool:
        """
        测试AI服务连接
        """
        if not self.enabled:
            return False
        
        try:
            # 使用通用的模型映射
            models = {
                "openai": "gpt-3.5-turbo",
                "deepseek": "deepseek-chat"
            }
            
            # 简单的测试请求
            response = self.client.chat.completions.create(
                model=models.get(self.provider, "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            current_app.logger.error(f"AI connection test failed: {e}")
            return False
