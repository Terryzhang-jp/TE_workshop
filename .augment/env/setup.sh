#!/bin/bash
set -e

echo "🚀 完整设置并运行测试"
echo "===================="

# 更新系统包
sudo apt-get update -y

# 安装 Python 和相关工具
sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential

# 进入工作目录
cd /mnt/persist/workspace/backend

# 清理并创建虚拟环境
rm -rf venv
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
if [ -f "requirements/dev.txt" ]; then
    pip install -r requirements/dev.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# 创建必要的目录
mkdir -p data/models data/raw data/processed logs

# 创建测试数据文件
cat > data/temp_usage_data.csv << 'EOF'
time,temp,usage
2024-01-01 00:00:00,20.5,2500.0
2024-01-01 01:00:00,19.8,2300.0
2024-01-01 02:00:00,19.2,2200.0
2024-01-01 03:00:00,18.9,2100.0
2024-01-01 04:00:00,18.5,2000.0
2024-01-01 05:00:00,18.8,2150.0
2024-01-01 06:00:00,19.5,2400.0
2024-01-01 07:00:00,20.2,2800.0
2024-01-01 08:00:00,21.0,3200.0
2024-01-01 09:00:00,22.1,3600.0
2024-01-01 10:00:00,23.5,4000.0
2024-01-01 11:00:00,24.8,4200.0
2024-01-01 12:00:00,25.5,4300.0
2024-01-01 13:00:00,26.0,4400.0
2024-01-01 14:00:00,26.2,4450.0
2024-01-01 15:00:00,26.0,4400.0
2024-01-01 16:00:00,25.5,4200.0
2024-01-01 17:00:00,24.8,4000.0
2024-01-01 18:00:00,23.9,3800.0
2024-01-01 19:00:00,23.0,3600.0
2024-01-01 20:00:00,22.2,3400.0
2024-01-01 21:00:00,21.5,3200.0
2024-01-01 22:00:00,20.8,2900.0
2024-01-01 23:00:00,20.2,2600.0
EOF

# 创建环境变量文件
cat > .env << 'EOF'
DEBUG=true
ENVIRONMENT=test
DATA_FILE_PATH=data/temp_usage_data.csv
MODEL_SAVE_PATH=data/models/
LOG_LEVEL=INFO
EOF

# 设置环境变量
export PYTHONPATH=/mnt/persist/workspace/backend:$PYTHONPATH

echo "✅ 环境设置完成，准备运行测试"