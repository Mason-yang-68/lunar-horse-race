# 🚀 無網域快速部署 - HTTP方案

> 適用於：快速測試、時間緊迫、不介意iOS只能TAP按鈕

---

## ⚠️ 重要提醒

**此方案限制：**
- ❌ iOS **無法使用搖動功能**，只能使用TAP按鈕
- ✅ Android 可正常搖動
- ✅ 所有裝置的TAP按鈕都可用

**如果iOS搖動功能很重要，請使用Cloudflare Tunnel方案（需申請免費網域）**

---

## 部署步驟（總時間：~15分鐘）

### 步驟1: 上傳檔案到NAS (5分鐘)

1. 連接到NAS：`http://192.168.0.130:5000` 登入DSM
2. 開啟 File Station
3. 創建資料夾：`/homes/您的用戶名/horse-race/`
4. 上傳所有專案檔案：
   - `server.py`
   - `prize_logic.py`
   - `requirements.txt`
   - `templates/` 資料夾
   - `static/` 資料夾

---

### 步驟2: SSH安裝依賴 (5分鐘)

```bash
# SSH連線
ssh 您的用戶名@192.168.0.130

# 進入專案目錄
cd ~/horse-race

# 安裝Python依賴
python3 -m pip install --user -r requirements.txt

# 測試啟動（內網測試）
python3 server.py
```

**測試內網：** 在手機或電腦瀏覽器開啟 `http://192.168.0.130:5000`

如果看到遊戲畫面，按 `Ctrl+C` 停止（我們稍後會背景執行）

---

### 步驟3: 設定UniFi Port Forwarding (3分鐘)

#### 3.1 登入UniFi Dream Router

1. 開啟瀏覽器訪問：`https://unifi.ui.com` 或路由器IP
2. 登入您的UniFi帳號

#### 3.2 設定Port Forwarding

1. 前往 **Settings** → **Routing** → **Port Forwarding**
2. 點選 **Create New Port Forward Rule**
3. 填寫：
   - **Name**: `Horse Race Game`
   - **Enable**: ✅ 勾選
   - **From**: `Any` 或 `Limited` (如只允許特定IP)
   - **Port**: `5000`
   - **Forward IP**: `192.168.0.130` (您的NAS內網IP)
   - **Forward Port**: `5000`
   - **Protocol**: `TCP`
4. 點選 **Apply Changes**

---

### 步驟4: 取得外網IP (1分鐘)

**方法A: 在NAS上查詢**
```bash
curl ifconfig.me
```

**方法B: 在網站查詢**
Google搜尋「我的IP」或訪問 https://whatismyip.com

**記下您的外網IP，例如：** `123.45.67.89`

---

### 步驟5: 背景啟動服務 (1分鐘)

```bash
# SSH連線到NAS
ssh 您的用戶名@192.168.0.130

# 進入專案目錄
cd ~/horse-race

# 背景執行伺服器
nohup python3 server.py > server.log 2>&1 &

# 確認運行
ps aux | grep server.py
```

應該看到 Python 進程正在運行。

---

### 步驟6: 測試訪問

#### 內網測試
```
http://192.168.0.130:5000
```

#### 外網測試（關閉WiFi，用4G/5G）
```
http://您的外網IP:5000
```

例如：`http://123.45.67.89:5000`

---

## 📱 手機使用說明

### 掃QR Code加入

1. 主持人開啟遊戲頁面
2. 手機掃描QR Code（會自動帶入網址）
3. 選擇馬匹頭像
4. 輸入名字
5. 加入遊戲

### 操作方式

**Android手機：**
- ✅ 可以搖動手機控制
- ✅ 也可以點擊TAP按鈕

**iPhone (iOS)：**
- ❌ 搖動功能無法使用（HTTP限制）
- ✅ **使用TAP按鈕** （一樣好玩！）

---

## 🔧 服務管理

### 查看服務狀態
```bash
ps aux | grep server.py
```

### 查看日誌
```bash
tail -f ~/horse-race/server.log
```

### 停止服務
```bash
pkill -f server.py
```

### 重新啟動
```bash
cd ~/horse-race
nohup python3 server.py > server.log 2>&1 &
```

---

## 📋 過年使用流程

**開始前：**
1. 確認NAS開機
2. SSH啟動服務：`cd ~/horse-race && nohup python3 server.py > server.log 2>&1 &`
3. 確認服務運行：`ps aux | grep server.py`

**分享給親友：**
- 內網用戶：`http://192.168.0.130:5000`
- 外網用戶：`http://您的外網IP:5000`

**提醒iOS用戶：**
"搖動功能需要HTTPS，請使用TAP按鈕操作喔！一樣很好玩！"

**遊戲結束後：**
```bash
pkill -f server.py
```

---

## ⚡ 快速啟動腳本（選用）

創建啟動腳本方便管理：

```bash
cd ~/horse-race
nano start-simple.sh
```

貼上以下內容：
```bash
#!/bin/bash
cd ~/horse-race
pkill -f server.py 2>/dev/null
sleep 1
nohup python3 server.py > server.log 2>&1 &
echo "✅ 遊戲啟動成功!"
echo "🌐 內網: http://192.168.0.130:5000"
echo "🌐 外網: http://$(curl -s ifconfig.me):5000"
```

賦予執行權限：
```bash
chmod +x start-simple.sh
```

以後只需執行：
```bash
./start-simple.sh
```

---

## 🆙 未來升級到HTTPS（支援iOS搖動）

如果日後想讓iOS也能搖動，可以：

### 選項1: 申請免費網域 + Cloudflare Tunnel
- 參考 `DS420j_Cloudflare部署步驟.md`
- 需時約30分鐘
- 完全免費

### 選項2: 使用動態DNS服務
- 服務如 No-IP, DuckDNS（免費）
- 取得免費子網域
- 配合 Let's Encrypt 免費SSL

---

## ❓ 常見問題

### Q: 外網訪問很慢？
可能是ISP限制，或上傳頻寬不足。建議：
- 減少同時線上人數（5人以內）
- 或升級到Cloudflare Tunnel（有CDN加速）

### Q: 動態IP變了怎麼辦？
每次重啟路由器後，外網IP可能改變。
- 重新查詢IP：`curl ifconfig.me`
- 更新分享的網址
- 或使用動態DNS服務

### Q: UniFi找不到Port Forwarding設定？
新版UniFi介面可能在：
- **Settings** → **Internet** → **Port Forwarding**
- 或搜尋「Port Forward」

### Q: 想讓iOS也能搖動？
需要升級到HTTPS方案：
1. 申請免費網域（Freenom）
2. 使用Cloudflare Tunnel
3. 參考完整指引：`DS420j_Cloudflare部署步驟.md`

---

## 🎉 完成！

現在您可以讓親友用手機掃QR Code玩遊戲了！

雖然iOS只能用TAP按鈕，但**遊戲一樣好玩**！按鈕反饋很流暢，完全不影響遊戲體驗！

**祝您新年快樂！馬到成功！🐴🧧**
