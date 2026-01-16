# 🎊 Synology DS420j + Cloudflare Tunnel 部署指引

> 專為您的環境客製化：DS420j (DSM 7.2.2) + UniFi Dream Router + 無Docker

---

## 📋 環境確認

✅ **您的配置:**
- NAS: Synology DS420j
- 系統: DSM 7.2.2-72806 Update5
- 內網IP: 192.168.0.130
- 路由器: UniFi Dream Router
- Docker: ❌ 不支援（DS420j為入門級機型）
- 方案: **Cloudflare Tunnel + Python直接部署**

✅ **優點:**
- 無需Docker
- 無需設定UniFi Port Forwarding
- 自動HTTPS（iOS完整搖動功能）
- 隱藏家庭IP
- 完全免費

---

## 🚀 部署流程總覽

1. ✅ 準備Cloudflare帳號和免費網域（10分鐘）
2. ✅ 上傳檔案到NAS（5分鐘）
3. ✅ SSH安裝Python依賴（5分鐘）
4. ✅ 安裝並設定Cloudflare Tunnel（15分鐘）
5. ✅ 啟動遊戲服務（2分鐘）
6. ✅ 測試（5分鐘）

**總時間: 約45分鐘**

---

## 步驟1: 準備Cloudflare和免費網域

### 1.1 註冊Cloudflare帳號（如已有請跳過）

1. 前往 https://dash.cloudflare.com/sign-up
2. 註冊免費帳號（使用Email）
3. 驗證Email

### 1.2 申請免費網域（推薦方式）

**選項A: 使用 Freenom 免費網域 (推薦)**

1. 前往 https://www.freenom.com
2. 搜尋一個網域名稱，例如: `horsegame` 或 `newyeargame`
3. 選擇免費後綴: `.tk`, `.ml`, `.ga`, `.cf` 或 `.gq`
4. 註冊並選擇 "Use Freenom DNS" 或 "Use custom DNS"
5. 完成註冊（免費，12個月）

**選項B: 使用現有網域**

如果您有現有網域（如 GoDaddy, Namecheap 購買的），也可以使用。

### 1.3 將網域加入Cloudflare

1. 登入 Cloudflare Dashboard
2. 點選 "Add a Site"
3. 輸入您的網域（例如: `horsegame.tk`）
4. 選擇 **Free** 方案
5. Cloudflare 會掃描DNS記錄
6. 按照指示更新網域的 Nameservers（在Freenom或原DNS服務商）
   - Nameserver 範例:
     ```
     alice.ns.cloudflare.com
     bob.ns.cloudflare.com
     ```
7. 等待DNS生效（通常5-30分鐘）

---

## 步驟2: 上傳檔案到NAS

### 2.1 連接到NAS

**方法A: 使用File Station (圖形介面)**

1. 開啟瀏覽器，前往 `http://192.168.0.130:5000`
2. 登入DSM
3. 開啟 **File Station**
4. 創建資料夾: `/homes/您的用戶名/horse-race/`

**方法B: 使用SMB共享 (Windows檔案總管)**

1. 在Windows檔案總管輸入: `\\192.168.0.130`
2. 登入
3. 進入 `home` → `您的用戶名`
4. 創建資料夾 `horse-race`

### 2.2 上傳專案檔案

將以下檔案和資料夾上傳到 `/homes/您的用戶名/horse-race/`:

```
horse-race/
├── server.py
├── prize_logic.py
├── requirements.txt
├── templates/
│   ├── host.html
│   └── client.html
└── static/
    ├── style.css
    └── images/
        ├── horse1.png
        ├── horse2.png
        └── ... (所有馬匹圖片)
```

**☝️ 重點:** 請從您的電腦專案資料夾 `c:\Users\guziy\Documents\過年紅包\` 複製所有這些檔案。

---

## 步驟3: SSH連線並安裝Python依賴

### 3.1 啟用SSH (如未啟用)

1. 登入DSM
2. 前往 **控制台** → **終端機和SNMP**
3. 勾選 **啟動SSH服務**
4. 保持預設Port 22
5. 套用

### 3.2 SSH連線到NAS

**Windows用戶 (使用PowerShell或CMD):**

```powershell
ssh 您的用戶名@192.168.0.130
```

輸入密碼登入。

**Mac/Linux用戶:**

```bash
ssh 您的用戶名@192.168.0.130
```

### 3.3 檢查Python版本

```bash
python3 --version
```

應該顯示 Python 3.x（DSM 7.x內建Python 3）

### 3.4 安裝Python依賴

```bash
# 切換到專案目錄
cd ~/horse-race

# 安裝pip (如果沒有)
sudo python3 -m ensurepip --upgrade

# 安裝專案依賴
python3 -m pip install --user -r requirements.txt
```

**預期輸出:** 
```
Successfully installed flask-x.x.x flask-socketio-x.x.x eventlet-x.x.x
```

### 3.5 測試啟動（內網測試）

```bash
python3 server.py
```

**預期輸出:**
```
Server running at http://192.168.0.130:5000
 * Serving Flask app 'server'
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.0.130:5000
```

🎉 **測試內網訪問:** 
在同一WiFi的手機或電腦開啟瀏覽器: `http://192.168.0.130:5000`

如果看到遊戲介面，代表成功！

按 `Ctrl+C` 停止服務（我們稍後會用Cloudflare Tunnel啟動）

---

## 步驟4: 安裝Cloudflare Tunnel

### 4.1 下載 cloudflared

```bash
# 進入home目錄
cd ~

# 下載cloudflared (DS420j是x86_64架構)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

# 賦予執行權限
chmod +x cloudflared-linux-amd64

# 移動到PATH目錄
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# 驗證安裝
cloudflared --version
```

**預期輸出:**
```
cloudflared version 2024.x.x
```

### 4.2 登入Cloudflare

```bash
cloudflared tunnel login
```

**會顯示類似:**
```
Please open the following URL and log in with your Cloudflare account:

https://dash.cloudflare.com/argotunnel?callback=https://...

Leave cloudflared running to download the cert automatically.
```

**操作步驟:**
1. 複製該URL
2. 在電腦瀏覽器開啟
3. 登入Cloudflare帳號
4. 選擇您的網域（例如: `horsegame.tk`）
5. 點選 **Authorize**

**SSH視窗會顯示:**
```
You have successfully logged in.
```

憑證會儲存在: `~/.cloudflared/cert.pem`

### 4.3 創建Tunnel

```bash
cloudflared tunnel create horse-race
```

**預期輸出:**
```
Tunnel credentials written to /root/.cloudflared/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.json
Created tunnel horse-race with id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**☝️ 記下這個 Tunnel ID**（例如: `abc12345-1234-1234-1234-123456789abc`）

### 4.4 創建Tunnel配置檔

```bash
# 創建配置目錄
mkdir -p ~/.cloudflared

# 編輯配置檔
nano ~/.cloudflared/config.yml
```

**貼上以下內容** (記得替換 `YOUR_TUNNEL_ID` 和 `YOUR_DOMAIN`):

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /var/services/homes/您的用戶名/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: game.YOUR_DOMAIN.tk
    service: http://localhost:5000
  - service: http_status:404
```

**範例:**
```yaml
tunnel: abc12345-1234-1234-1234-123456789abc
credentials-file: /var/services/homes/john/.cloudflared/abc12345-1234-1234-1234-123456789abc.json

ingress:
  - hostname: game.horsegame.tk
    service: http://localhost:5000
  - service: http_status:404
```

**儲存並退出:**
- 按 `Ctrl+O` 儲存
- 按 `Enter` 確認
- 按 `Ctrl+X` 退出

### 4.5 設定DNS路由

```bash
cloudflared tunnel route dns horse-race game.YOUR_DOMAIN.tk
```

替換 `YOUR_DOMAIN.tk` 為您的網域，例如:
```bash
cloudflared tunnel route dns horse-race game.horsegame.tk
```

**預期輸出:**
```
Created CNAME record for game.horsegame.tk to xxxxxxxx.cfargotunnel.com
```

---

## 步驟5: 啟動服務

### 5.1 創建啟動腳本

```bash
cd ~/horse-race
nano start.sh
```

**貼上以下內容:**

```bash
#!/bin/bash

# 啟動Python伺服器 (背景執行)
cd ~/horse-race
nohup python3 server.py > server.log 2>&1 &

echo "Game server started. PID: $!"

# 等待伺服器啟動
sleep 3

# 啟動Cloudflare Tunnel (背景執行)
nohup cloudflared tunnel run horse-race > tunnel.log 2>&1 &

echo "Cloudflare tunnel started. PID: $!"
echo ""
echo "✅ 部署完成!"
echo "🌐 請訪問: https://game.YOUR_DOMAIN.tk"
echo ""
echo "📊 查看日誌:"
echo "  - Game server: tail -f ~/horse-race/server.log"
echo "  - Tunnel: tail -f ~/horse-race/tunnel.log"
```

**記得替換 `YOUR_DOMAIN.tk` 為您的網域！**

**儲存並賦予執行權限:**
```bash
chmod +x start.sh
```

### 5.2 執行啟動腳本

```bash
./start.sh
```

**預期輸出:**
```
Game server started. PID: 12345
Cloudflare tunnel started. PID: 12346

✅ 部署完成!
🌐 請訪問: https://game.horsegame.tk
```

### 5.3 查看日誌確認運行

```bash
# 查看遊戲伺服器日誌
tail -f ~/horse-race/server.log

# 查看Tunnel日誌
tail -f ~/horse-race/tunnel.log
```

按 `Ctrl+C` 退出日誌檢視。

---

## 步驟6: 測試訪問

### 6.1 外網訪問測試

1. 在任何裝置（手機、電腦）開啟瀏覽器
2. 訪問: `https://game.您的網域.tk`
3. 應該看到遊戲主持人畫面和QR Code！

### 6.2 手機測試

1. 用手機掃描QR Code
2. 選擇馬匹頭像
3. 輸入名字
4. 加入遊戲
5. **iOS測試:** 點選「開啟搖晃感應📳」→ 允許權限
6. 主持人點選「開始賽跑」
7. 搖晃手機或點擊TAP按鈕
8. 確認馬匹移動！

---

## 🔧 管理指令

### 檢查服務狀態

```bash
# 檢查Python進程
ps aux | grep server.py

# 檢查Cloudflare進程
ps aux | grep cloudflared
```

### 停止服務

```bash
# 停止Python伺服器
pkill -f server.py

# 停止Cloudflare Tunnel
pkill -f cloudflared
```

### 重新啟動服務

```bash
cd ~/horse-race
./start.sh
```

### 查看即時日誌

```bash
# 遊戲伺服器日誌
tail -f ~/horse-race/server.log

# Tunnel日誌
tail -f ~/horse-race/tunnel.log
```

---

## 🎯 開機自動啟動（選用）

如果希望NAS重啟後自動啟動遊戲：

### 方法1: 使用DSM任務排程器

1. 登入DSM
2. 前往 **控制台** → **任務排程器**
3. 新增 → **觸發的任務** → **使用者定義的指令碼**
4. 設定:
   - 任務名稱: `啟動賽馬遊戲`
   - 使用者: 您的用戶名
   - 觸發事件: **開機**
   - 指令碼:
     ```bash
     sleep 60
     /var/services/homes/您的用戶名/horse-race/start.sh
     ```
5. 儲存

### 方法2: 使用crontab

```bash
crontab -e
```

新增一行:
```
@reboot sleep 60 && /var/services/homes/您的用戶名/horse-race/start.sh
```

儲存退出。

---

## ❓ 常見問題

### Q1: Cloudflare Tunnel連不上？

**檢查步驟:**
```bash
# 確認tunnel狀態
cloudflared tunnel list

# 測試tunnel連線
cloudflared tunnel run horse-race
```

如顯示錯誤，檢查:
1. config.yml中的tunnel ID是否正確
2. credentials檔案路徑是否正確
3. DNS記錄是否已生效（可能需要等待幾分鐘）

### Q2: 訪問網址顯示404？

1. 確認Python伺服器正在運行: `ps aux | grep server.py`
2. 本地測試是否正常: `curl http://localhost:5000`
3. 檢查tunnel日誌: `tail -f ~/horse-race/tunnel.log`

### Q3: iOS無法使用搖晃功能？

確認:
1. ✅ 使用HTTPS訪問（Cloudflare Tunnel自動提供）
2. ✅ iOS Safari允許動作感應權限
3. ✅ 不是使用Private/Incognito模式

如仍無法使用，可使用TAP按鈕備用方案。

### Q4: 想更改網址？

修改DNS記錄:
```bash
# 刪除舊記錄
cloudflared tunnel route dns delete horse-race game.舊網域.tk

# 新增新記錄
cloudflared tunnel route dns horse-race game.新網域.tk
```

然後更新 `~/.cloudflared/config.yml` 中的 hostname。

---

## 🎊 完成檢查清單

部署完成後，請確認:

- [ ] ✅ 內網可訪問 `http://192.168.0.130:5000`
- [ ] ✅ 外網可訪問 `https://game.您的網域.tk`
- [ ] ✅ HTTPS正常（瀏覽器顯示🔒）
- [ ] ✅ QR Code可掃描
- [ ] ✅ 手機可加入遊戲
- [ ] ✅ iOS可請求動作感應權限
- [ ] ✅ 搖晃或TAP可控制馬匹
- [ ] ✅ 多人同時遊戲正常
- [ ] ✅ 遊戲結束顯示排名和獎金

---

## 🎉 大功告成！

恭喜您成功部署遊戲到NAS！

**過年時:**
1. 確保NAS和網路正常運作
2. 分享網址或QR Code給親友
3. 開始遊戲，享受歡樂時光！

**祝您:**
- 🐴 馬到成功
- 🧧 萬馬奔騰
- 🎊 新年快樂

有任何問題隨時問我！ 😊
