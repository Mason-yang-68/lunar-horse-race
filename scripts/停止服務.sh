#!/bin/bash
# 停止過年紅包賽馬遊戲服務

echo "🛑 停止遊戲服務..."

# 停止Python伺服器
echo "   停止遊戲伺服器..."
pkill -f server.py
if [ $? -eq 0 ]; then
    echo "   ✅ Game server stopped"
else
    echo "   ℹ️  Game server was not running"
fi

# 停止Cloudflare Tunnel
echo "   停止Cloudflare Tunnel..."
pkill -f cloudflared
if [ $? -eq 0 ]; then
    echo "   ✅ Cloudflare tunnel stopped"
else
    echo "   ℹ️  Cloudflare tunnel was not running"
fi

echo ""
echo "✅ 服務已停止"
