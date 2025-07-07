"""
简单的用户管理API测试服务器
Simple User Management API Test Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import json
import os

app = FastAPI(title="User Management Test API")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class UserSession(BaseModel):
    user_id: str
    username: str
    session_id: str
    created_at: str
    last_active: str

class UserDecision(BaseModel):
    decision_id: str
    label: str
    reason: str
    status: str
    created_at: str
    completed_at: Optional[str] = None

class UserAdjustment(BaseModel):
    adjustment_id: str
    decision_id: str
    hour: int
    original_value: float
    adjusted_value: float
    timestamp: str

class UserInteraction(BaseModel):
    interaction_id: str
    component: str
    action_type: str
    action_details: Dict
    timestamp: str

class StandardResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    message: str

# 内存存储
user_sessions: Dict[str, UserSession] = {}
user_experiments: Dict[str, Dict] = {}

# 实验结果存储目录
EXPERIMENT_RESULTS_DIR = "experiment_results"
os.makedirs(EXPERIMENT_RESULTS_DIR, exist_ok=True)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-management-test"}

@app.post("/api/v1/user/login")
async def user_login(request: Dict):
    username = request.get("username", "").strip()
    
    if not username or len(username) < 2:
        raise HTTPException(status_code=400, detail="用户名至少需要2个字符")
    
    user_id = f"user_{username}_{int(datetime.now().timestamp())}"
    session_id = str(uuid.uuid4())
    
    user_session = UserSession(
        user_id=user_id,
        username=username,
        session_id=session_id,
        created_at=datetime.now().isoformat(),
        last_active=datetime.now().isoformat()
    )
    
    user_sessions[session_id] = user_session
    user_experiments[session_id] = {
        "user_session": user_session,
        "decisions": [],
        "adjustments": [],
        "interactions": [],
        "experiment_start_time": datetime.now().isoformat(),
        "final_predictions": []
    }
    
    return StandardResponse(
        success=True,
        data=user_session.dict(),
        message="用户登录成功"
    )

@app.get("/api/v1/user/session/{session_id}")
async def get_user_session(session_id: str):
    if session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    user_session = user_sessions[session_id]
    user_session.last_active = datetime.now().isoformat()
    
    return StandardResponse(
        success=True,
        data=user_session.dict(),
        message="会话信息获取成功"
    )

@app.post("/api/v1/user/decision")
async def create_user_decision(request: Dict):
    session_id = request.get("session_id")
    label = request.get("label", "").strip()
    reason = request.get("reason", "").strip()
    
    if session_id not in user_experiments:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    if not label or len(label) < 10:
        raise HTTPException(status_code=400, detail="决策标签至少需要10个字符")
    
    if not reason or len(reason) < 10:
        raise HTTPException(status_code=400, detail="决策理由至少需要10个字符")
    
    decision_id = f"decision_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
    
    user_decision = UserDecision(
        decision_id=decision_id,
        label=label,
        reason=reason,
        status="active",
        created_at=datetime.now().isoformat()
    )
    
    # 将之前的决策设为完成状态
    for decision in user_experiments[session_id]["decisions"]:
        if decision.status == "active":
            decision.status = "completed"
            decision.completed_at = datetime.now().isoformat()
    
    user_experiments[session_id]["decisions"].append(user_decision)
    
    return StandardResponse(
        success=True,
        data=user_decision.dict(),
        message="决策创建成功"
    )

@app.post("/api/v1/user/adjustment")
async def create_user_adjustment(request: Dict):
    session_id = request.get("session_id")
    decision_id = request.get("decision_id")
    hour = request.get("hour")
    original_value = request.get("original_value")
    adjusted_value = request.get("adjusted_value")
    
    if session_id not in user_experiments:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    if not (0 <= hour <= 23):
        raise HTTPException(status_code=400, detail="小时必须在0-23之间")
    
    adjustment_id = f"adj_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
    
    user_adjustment = UserAdjustment(
        adjustment_id=adjustment_id,
        decision_id=decision_id,
        hour=hour,
        original_value=original_value,
        adjusted_value=adjusted_value,
        timestamp=datetime.now().isoformat()
    )
    
    # 移除同一小时的之前调整
    user_experiments[session_id]["adjustments"] = [
        adj for adj in user_experiments[session_id]["adjustments"] 
        if adj.hour != hour
    ]
    
    user_experiments[session_id]["adjustments"].append(user_adjustment)
    
    return StandardResponse(
        success=True,
        data=user_adjustment.dict(),
        message="调整创建成功"
    )

@app.post("/api/v1/user/interaction")
async def record_user_interaction(request: Dict):
    session_id = request.get("session_id")
    component = request.get("component")
    action_type = request.get("action_type")
    action_details = request.get("action_details", {})

    if session_id not in user_experiments:
        raise HTTPException(status_code=404, detail="会话不存在")

    if not component or not action_type:
        raise HTTPException(status_code=400, detail="组件名称和操作类型不能为空")

    interaction_id = f"int_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"

    user_interaction = UserInteraction(
        interaction_id=interaction_id,
        component=component,
        action_type=action_type,
        action_details=action_details,
        timestamp=datetime.now().isoformat()
    )

    user_experiments[session_id]["interactions"].append(user_interaction)

    return StandardResponse(
        success=True,
        data=user_interaction.dict(),
        message="交互记录成功"
    )

@app.post("/api/v1/user/complete-experiment")
async def complete_experiment(request: Dict):
    session_id = request.get("session_id")
    final_predictions = request.get("final_predictions", [])
    
    if session_id not in user_experiments:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    experiment_data = user_experiments[session_id]
    user_session = experiment_data["user_session"]
    
    experiment_end_time = datetime.now().isoformat()
    
    experiment_result = {
        "user_id": user_session.user_id,
        "username": user_session.username,
        "session_id": session_id,
        "experiment_start_time": experiment_data["experiment_start_time"],
        "experiment_end_time": experiment_end_time,
        "decisions": [d.dict() if hasattr(d, 'dict') else d for d in experiment_data["decisions"]],
        "adjustments": [a.dict() if hasattr(a, 'dict') else a for a in experiment_data["adjustments"]],
        "interactions": [i.dict() if hasattr(i, 'dict') else i for i in experiment_data["interactions"]],
        "final_predictions": final_predictions,
        "experiment_duration_minutes": 0  # 简化计算
    }
    
    # 保存到文件
    result_filename = f"{EXPERIMENT_RESULTS_DIR}/experiment_{user_session.username}_{session_id[:8]}_{int(datetime.now().timestamp())}.json"
    
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(experiment_result, f, ensure_ascii=False, indent=2)

    # 自动转换为CSV
    try:
        import sys
        sys.path.append('scripts')
        from json_to_csv_converter import ExperimentDataConverter
        converter = ExperimentDataConverter()
        converter.convert_to_csv()
        print(f"✅ 自动转换CSV完成")
    except Exception as e:
        print(f"⚠️ CSV转换失败: {e}")

    # 清理会话数据
    if session_id in user_sessions:
        del user_sessions[session_id]
    if session_id in user_experiments:
        del user_experiments[session_id]
    
    return StandardResponse(
        success=True,
        data=experiment_result,
        message="实验完成，结果已保存"
    )

@app.get("/api/v1/user/experiment-results")
async def list_experiment_results():
    result_files = []
    if os.path.exists(EXPERIMENT_RESULTS_DIR):
        result_files = [f for f in os.listdir(EXPERIMENT_RESULTS_DIR) if f.endswith('.json')]
    
    return StandardResponse(
        success=True,
        data=result_files,
        message=f"找到 {len(result_files)} 个实验结果文件"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
