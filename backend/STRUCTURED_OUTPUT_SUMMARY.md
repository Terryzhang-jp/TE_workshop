# AI Agent结构化输入输出规范

## 📋 概述

我们已经成功实现了AI Agent的完整结构化输入输出系统，使整个决策流程更加透明、可读和易于前后端集成。

## 🏗️ 架构组件

### 1. 结构化数据模型 (`structured_models.py`)

#### 核心模型类
- **`ThinkingStepModel`**: 单步思考的完整结构
- **`UserInputModel`**: 标准化用户输入格式
- **`FinalOutputModel`**: 最终决策输出格式
- **`StreamEventModel`**: 流式事件标准格式

#### 支持模型类
- **`InsightModel`**: 洞察信息结构
- **`QuestionModel`**: 问题信息结构
- **`PlanModel`**: 计划信息结构
- **`DecisionModel`**: 决策信息结构
- **`RecommendationModel`**: 推荐信息结构

#### 枚举类型
- **`ThinkingPhase`**: 思考阶段枚举
- **`ActionType`**: 行动类型枚举

### 2. 结构化格式化器 (`structured_formatter.py`)

#### 主要功能
- **输入格式化**: `format_user_input()`
- **思考步骤格式化**: `format_thinking_step()`
- **流式事件格式化**: `format_stream_event()`
- **最终输出格式化**: `format_final_output()`
- **可读摘要生成**: `format_readable_summary()`

#### 状态管理
- 会话级别的状态跟踪
- 累积洞察和问题管理
- 性能指标计算

### 3. 增强的思考节点 (`thinking.py`)

#### 新增功能
- 结构化思考步骤生成
- 思考阶段自动识别
- 置信度动态计算
- 性能指标记录

#### 思考阶段识别
- `PROBLEM_ANALYSIS`: 问题分析
- `INFORMATION_GATHERING`: 信息收集
- `PATTERN_RECOGNITION`: 模式识别
- `SOLUTION_DESIGN`: 方案设计
- `DECISION_MAKING`: 决策制定
- `EXECUTION_PLANNING`: 执行规划

### 4. 结构化API端点 (`ai_agent.py`)

#### 新增端点
- **`/stream-structured`**: 完全结构化的流式处理
- **更新的`/status`**: 包含结构化功能信息

#### 增强的事件类型
- `session_start`: 会话开始
- `thinking_step_complete`: 思考步骤完成
- `step_progress`: 基础进度更新
- `process_complete`: 流程完成
- `error`: 错误事件

## 📊 结构化输出示例

### 用户输入结构
```json
{
  "session_id": "uuid",
  "intention": "用户调整意图",
  "reasoning": "用户思考原因",
  "context": {"额外上下文"},
  "constraints": ["约束条件"],
  "preferences": {"用户偏好"},
  "timestamp": "ISO时间戳"
}
```

### 思考步骤结构
```json
{
  "step_number": 1,
  "iteration": 0,
  "phase": "problem_analysis",
  "plan": {
    "phase": "problem_analysis",
    "objective": "当前目标",
    "planned_actions": ["think"],
    "success_criteria": ["完成标准"]
  },
  "thinking_content": "AI思考内容",
  "reasoning": "推理过程",
  "actions_taken": [],
  "next_action": "access_context",
  "new_insights": [
    {
      "id": "uuid",
      "content": "洞察内容",
      "confidence": 0.8,
      "source": "thinking",
      "iteration": 0
    }
  ],
  "new_questions": [
    {
      "id": "uuid", 
      "content": "问题内容",
      "target_source": "contextual_information",
      "priority": 0.9
    }
  ],
  "processing_time": 23.5,
  "confidence": 0.7
}
```

### 最终输出结构
```json
{
  "session_id": "uuid",
  "user_input": "用户输入对象",
  "thinking_steps": ["思考步骤数组"],
  "total_iterations": 5,
  "final_decision": {
    "strategy": "决策策略",
    "rationale": "决策理由", 
    "adjustments": {"具体调整"},
    "confidence": 0.85,
    "risk_assessment": {"风险评估"}
  },
  "recommendations": [
    {
      "id": "uuid",
      "title": "推荐标题",
      "description": "推荐描述",
      "priority": "high",
      "category": "电力预测调整"
    }
  ],
  "all_insights": ["所有洞察"],
  "answered_questions": ["已回答问题"],
  "processing_summary": {
    "phases_completed": ["完成的阶段"],
    "information_sources_accessed": ["访问的信息源"],
    "total_iterations": 5,
    "completion_status": "完成"
  },
  "performance_metrics": {
    "total_processing_time": 180.5,
    "average_step_time": 36.1,
    "total_insights_generated": 12,
    "total_questions_raised": 8,
    "final_confidence": 0.85
  },
  "is_successful": true,
  "error_messages": []
}
```

## 🔄 流式事件结构

### 基础事件格式
```json
{
  "type": "thinking_step_complete",
  "timestamp": "ISO时间戳",
  "session_id": "uuid",
  "step_number": 1,
  "iteration": 0,
  "data": {"事件数据"},
  "thinking_phase": "problem_analysis",
  "confidence": 0.7,
  "insights_count": 2,
  "questions_count": 3
}
```

## 🎯 使用方式

### 1. 基础流式API
```bash
POST /api/v1/ai-agent/stream
```
- 向后兼容的基础流式处理
- 适用于现有前端集成

### 2. 结构化流式API
```bash
POST /api/v1/ai-agent/stream-structured
```
- 完全结构化的输入输出
- 详细的思考过程透明化
- 丰富的性能指标

### 3. 状态查询API
```bash
GET /api/v1/ai-agent/status
```
- 服务器状态和能力查询
- 支持的功能列表

## 📈 性能指标

### 自动记录指标
- **处理时间**: 总时间、平均步骤时间
- **思考质量**: 洞察数量、问题数量
- **置信度**: 动态计算的决策置信度
- **完成状态**: 成功/失败状态跟踪

### 置信度计算
```python
base_confidence = 0.5
+ insights_count * 0.1  # 洞察加分
- questions_count * 0.05  # 问题扣分  
+ loop_count * 0.05  # 迭代加分
```

## 🔧 配置选项

### 请求配置
```json
{
  "max_iterations": 15,
  "timeout_seconds": 300,
  "include_debug": true,
  "structured_output": true,
  "confidence_threshold": 0.7
}
```

## ✅ 测试验证

### 测试脚本
- **`test_structured_output.py`**: 完整的结构化输出测试
- 验证所有组件的正确性
- 性能指标分析

### 测试结果
- ✅ 结构化数据模型正常工作
- ✅ 流式事件格式正确
- ✅ 思考过程完全透明
- ✅ 性能指标完整记录

## 🚀 前端集成建议

### 1. 使用结构化端点
```javascript
const response = await fetch('/api/v1/ai-agent/stream-structured', {
  method: 'POST',
  headers: {'Accept': 'text/event-stream'},
  body: JSON.stringify(requestData)
});
```

### 2. 处理结构化事件
```javascript
const eventSource = new EventSource(url);
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'thinking_step_complete':
      updateThinkingDisplay(data.data.structured_step);
      break;
    case 'process_complete':
      showFinalResults(data.data.final_output);
      break;
  }
};
```

### 3. 显示结构化信息
- **思考阶段**: 显示当前AI的思考阶段
- **置信度**: 实时置信度指示器
- **洞察列表**: 动态更新的洞察展示
- **问题列表**: AI提出的问题展示
- **性能指标**: 处理时间、效率指标

## 🎉 总结

通过这次结构化改进，我们实现了：

1. **完全透明的AI思考过程**
2. **标准化的输入输出格式**
3. **丰富的性能指标追踪**
4. **易于前端集成的API设计**
5. **向后兼容的渐进式升级**

现在AI Agent的每一步思考、每一个洞察、每一个决策都有完整的结构化记录，为前端提供了丰富的展示数据，也为后续的分析和优化提供了坚实的基础！🚀
