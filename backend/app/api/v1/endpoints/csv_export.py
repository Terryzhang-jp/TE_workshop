"""
CSV导出API端点
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
import logging
import subprocess
import os
from typing import Dict, List

from app.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate-user-csv")
async def generate_user_csv(background_tasks: BackgroundTasks):
    """
    生成所有用户的CSV文件
    """
    try:
        # 运行CSV生成脚本
        script_path = Path("scripts/generate_current_user_csv.py")
        if not script_path.exists():
            raise HTTPException(status_code=500, detail="CSV generation script not found")
        
        # 在后台运行脚本
        result = subprocess.run(
            ["python", str(script_path)],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"CSV generation failed: {result.stderr}")
            raise HTTPException(status_code=500, detail=f"CSV generation failed: {result.stderr}")
        
        # 解析输出，获取生成的文件列表
        output_lines = result.stdout.strip().split('\n')
        generated_files = []
        for line in output_lines:
            if line.startswith("Generated: "):
                file_path = line.replace("Generated: ", "")
                generated_files.append(file_path)
        
        return {
            "success": True,
            "message": "CSV files generated successfully",
            "generated_files": generated_files,
            "output": result.stdout
        }
        
    except Exception as e:
        logger.error(f"Error generating CSV files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list-csv-files")
async def list_csv_files():
    """
    列出所有生成的CSV文件
    """
    try:
        csv_dir = Path(settings.data_dir) / "user_csv_exports"
        if not csv_dir.exists():
            return {
                "success": True,
                "files": [],
                "message": "No CSV files found"
            }
        
        csv_files = []
        for file_path in csv_dir.glob("*.csv"):
            file_info = {
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "created_at": file_path.stat().st_ctime,
                "path": str(file_path.relative_to(Path.cwd()))
            }
            csv_files.append(file_info)
        
        # 按创建时间排序
        csv_files.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "files": csv_files,
            "total_files": len(csv_files)
        }
        
    except Exception as e:
        logger.error(f"Error listing CSV files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-csv/{filename}")
async def download_csv(filename: str):
    """
    下载指定的CSV文件
    """
    try:
        csv_dir = Path(settings.data_dir) / "user_csv_exports"
        file_path = csv_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        if not file_path.suffix == ".csv":
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="text/csv"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading CSV file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-csv/{filename}")
async def delete_csv(filename: str):
    """
    删除指定的CSV文件
    """
    try:
        csv_dir = Path(settings.data_dir) / "user_csv_exports"
        file_path = csv_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        if not file_path.suffix == ".csv":
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        file_path.unlink()
        
        return {
            "success": True,
            "message": f"CSV file {filename} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CSV file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/csv-stats")
async def get_csv_stats():
    """
    获取CSV文件统计信息
    """
    try:
        csv_dir = Path(settings.data_dir) / "user_csv_exports"
        if not csv_dir.exists():
            return {
                "success": True,
                "stats": {
                    "total_files": 0,
                    "total_size": 0,
                    "users_count": 0
                }
            }
        
        csv_files = list(csv_dir.glob("*.csv"))
        total_size = sum(f.stat().st_size for f in csv_files)
        
        # 统计用户数量（从文件名中提取）
        users = set()
        for file_path in csv_files:
            # 文件名格式：user_id_username_timestamp.csv
            parts = file_path.stem.split('_')
            if len(parts) >= 2:
                user_id = f"{parts[0]}_{parts[1]}"
                users.add(user_id)
        
        return {
            "success": True,
            "stats": {
                "total_files": len(csv_files),
                "total_size": total_size,
                "users_count": len(users),
                "average_file_size": total_size / len(csv_files) if csv_files else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting CSV stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
