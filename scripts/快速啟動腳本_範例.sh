#!/bin/bash
# 過年紅包賽馬遊戲 - 啟動腳本
# 適用於 Synology NAS (無Docker)

# 設定您的網域名稱
YOUR_DOMAIN="game.horsegame.tk"  # ⚠️ 請替換為您的實際網域

# 切換到專案目錄
cd ~/horse-race

echo "🎊 啟動過年紅包賽馬遊戲..."
echo ""

# 停止舊的進程（如果存在）
pkill -f server.py 2>/dev/null
pkill -f cloudflared 2>/dev/null
sleep 2

# 啟動Python伺服器 (背景執行)
echo "📡 啟動遊戲伺服器..."
nohup python3 server.py > server.log 2>&1 &
SERVER_PID=$!
echo "   ✅ Game server started. PID: $SERVER_PID"

# 等待伺服器啟動
sleep 3

# 檢查伺服器是否正常啟動
if ps -p $SERVER_PID > /dev/null; then
    echo "   ✅ Server is running"
else
    echo "   ❌ Server failed to start. Check server.log"
    exit 1
fi

# 啟動Cloudflare Tunnel (背景執行)
echo "🌐 啟動Cloudflare Tunnel..."
nohup cloudflared tunnel run horse-race > tunnel.log 2>&1 &
TUNNEL_PID=$!
echo "   ✅ Cloudflare tunnel started. PID: $TUNNEL_PID"

# 顯示狀態
echo ""
echo "═══════════════════════════════════════════"
echo "✅ 部署完成！"
echo "═══════════════════════════════════════════"
echo ""
echo "🌐 外網訪問網址: https://$YOUR_DOMAIN"
echo "🏠 內網訪問網址: http://192.168.0.130:5000"
echo ""
echo "📊 查看日誌指令:"
echo "   Game server: tail -f ~/horse-race/server.log"
echo "   Tunnel:      tail -f ~/horse-race/tunnel.log"
echo ""
echo "🛑 停止服務指令:"
echo "   pkill -f server.py && pkill -f cloudflared"
echo ""
echo "🎉 馬到成功！新年快樂！"
echo "═══════════════════════════════════════════"
