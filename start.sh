#!/bin/bash

echo "🍵 新中式茶席主题策划与器物借用管理系统"
echo "========================================"

echo "📦 检查并安装依赖..."

cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "🚀 启动后端服务 (端口 9702)..."
pkill -f "uvicorn main:app" 2>/dev/null
sleep 1
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 9702 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端PID: $BACKEND_PID"

sleep 2

cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

echo "🚀 启动前端服务 (端口 9701)..."
pkill -f "vite --port 9701" 2>/dev/null
sleep 1
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端PID: $FRONTEND_PID"

sleep 3

echo ""
echo "✅ 系统启动完成！"
echo "   前端地址: http://localhost:9701"
echo "   后端API:  http://localhost:9702"
echo "   API文档: http://localhost:9702/docs"
echo ""
echo "📋 启动脚本已保存进程PID，停止服务请运行: ./stop.sh"
echo ""

echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid
