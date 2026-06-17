#!/bin/bash

echo "🛑 正在停止茶席管理系统..."

if [ -f .backend.pid ]; then
    PID=$(cat .backend.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "   已停止后端服务 (PID: $PID)"
    fi
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    PID=$(cat .frontend.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "   已停止前端服务 (PID: $PID)"
    fi
    rm .frontend.pid
fi

pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "vite --port 9701" 2>/dev/null

echo "✅ 系统已停止"
