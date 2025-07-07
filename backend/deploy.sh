#!/bin/bash

# 电力预测系统后端部署脚本
# Power Prediction System Backend Deployment Script

set -e

echo "🚀 开始部署电力预测系统后端到Google Cloud Run..."

# 检查必要的工具
command -v gcloud >/dev/null 2>&1 || { echo "❌ 请先安装Google Cloud SDK"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ 请先安装Docker"; exit 1; }

# 设置项目变量
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="power-prediction-backend"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "📋 部署配置:"
echo "  项目ID: $PROJECT_ID"
echo "  区域: $REGION"
echo "  服务名: $SERVICE_NAME"
echo "  镜像名: $IMAGE_NAME"

# 确认部署
read -p "🤔 确认部署配置正确吗? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 1
fi

# 设置gcloud项目
echo "🔧 设置gcloud项目..."
gcloud config set project $PROJECT_ID

# 启用必要的API
echo "🔧 启用必要的Google Cloud API..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 构建Docker镜像
echo "🏗️ 构建Docker镜像..."
docker build -t $IMAGE_NAME:latest .

# 推送镜像到Container Registry
echo "📤 推送镜像到Container Registry..."
docker push $IMAGE_NAME:latest

# 部署到Cloud Run
echo "🚀 部署到Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 15 \
    --concurrency 80 \
    --timeout 300 \
    --set-env-vars "ENVIRONMENT=production,PORT=8080,ALLOWED_HOSTS=*,GEMINI_API_KEY=$GEMINI_API_KEY,AI_AGENT_GEMINI_API_KEY=$AI_AGENT_GEMINI_API_KEY"

# 获取服务URL
echo "🔗 获取服务URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo "✅ 部署完成!"
echo "🌐 服务URL: $SERVICE_URL"
echo "🏥 健康检查: $SERVICE_URL/health"
echo "📚 API文档: $SERVICE_URL/docs"

# 测试健康检查
echo "🧪 测试健康检查..."
sleep 10
if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
    echo "✅ 健康检查通过"
else
    echo "⚠️ 健康检查失败，请检查日志"
fi

echo "🎉 部署完成! 请将以下URL配置到前端:"
echo "   API_BASE_URL: $SERVICE_URL/api/v1"
