#!/bin/bash

# 电力预测系统前端部署脚本
# Power Prediction System Frontend Deployment Script

set -e

echo "🚀 开始部署电力预测系统前端到Vercel..."

# 检查必要的工具
command -v npm >/dev/null 2>&1 || { echo "❌ 请先安装Node.js和npm"; exit 1; }
command -v vercel >/dev/null 2>&1 || { echo "❌ 请先安装Vercel CLI: npm i -g vercel"; exit 1; }

# 获取后端API URL
BACKEND_URL=${1:-""}
if [ -z "$BACKEND_URL" ]; then
    echo "❌ 请提供后端API URL"
    echo "用法: ./deploy.sh <BACKEND_API_URL>"
    echo "示例: ./deploy.sh https://your-backend-service-url.run.app"
    exit 1
fi

# 确保URL以/api/v1结尾
if [[ ! $BACKEND_URL == */api/v1 ]]; then
    BACKEND_URL="$BACKEND_URL/api/v1"
fi

echo "📋 部署配置:"
echo "  后端API URL: $BACKEND_URL"

# 确认部署
read -p "🤔 确认部署配置正确吗? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
npm install

# 构建项目
echo "🏗️ 构建项目..."
VITE_API_BASE_URL=$BACKEND_URL npm run build

# 部署到Vercel
echo "🚀 部署到Vercel..."
vercel --prod --env VITE_API_BASE_URL=$BACKEND_URL

echo "✅ 前端部署完成!"
echo "🌐 请在Vercel控制台查看部署状态和URL"
echo "🔧 环境变量已设置:"
echo "   VITE_API_BASE_URL: $BACKEND_URL"
