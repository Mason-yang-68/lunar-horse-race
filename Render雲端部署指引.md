# 🚀 Render雲端部署指引 - 最簡單方案

> 完全免費，自動HTTPS，無需NAS！

---

## 📋 優勢對比

| 項目 | NAS部署 | Render雲端部署 |
|------|---------|----------------|
| **費用** | 免費 | 免費 |
| **需要NAS** | ✅ 需要 | ❌ 不需要 |
| **HTTPS** | 需設定 | ✅ 自動 |
| **網域** | 需申請 | ✅ 自動給 |
| **Port Forwarding** | 需設定 | ❌ 不需要 |
| **iOS搖動** | 需HTTPS設定 | ✅ 自動支援 |
| **部署時間** | 30-45分鐘 | **10分鐘** |
| **缺點** | 需要硬體 | 15分鐘無活動會休眠 |

**結論：如果您沒有NAS或想最簡單的方式，Render是最佳選擇！**

---

## 🎯 部署流程（總時間：10分鐘）

### 前置需求
- [ ] GitHub帳號（沒有的話免費註冊：https://github.com）
- [ ] Render帳號（用GitHub登入即可）

---

### 步驟1: 上傳專案到GitHub (3分鐘)

#### 1.1 創建GitHub Repository

1. 登入 https://github.com
2. 點選右上角 **+** → **New repository**
3. 填寫：
   - Repository name: `lunar-horse-race`（或任何名稱）
   - Description: `過年紅包賽馬遊戲`
   - Visibility: **Public** ✅（免費方案需公開）
4. 點選 **Create repository**

#### 1.2 上傳專案檔案

**方法A: 網頁上傳（推薦，最簡單）**

1. 在新建的repository頁面，點選 **uploading an existing file**
2. 將以下檔案拖曳上傳：
   ```
   ├── server.py
   ├── prize_logic.py
   ├── requirements.txt
   ├── templates/
   │   ├── host.html
   │   └── client.html
   └── static/
       ├── style.css
       └── images/
           └── (所有馬匹圖片)
   ```
3. 寫 Commit message: `Initial commit`
4. 點選 **Commit changes**

**方法B: 使用Git指令（進階）**

```bash
cd c:\Users\guziy\Documents\過年紅包

git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/您的用戶名/lunar-horse-race.git
git push -u origin main
```

---

### 步驟2: 修改server.py（重要！）

在GitHub上編輯 `server.py`，找到最後幾行：

**原始代碼（第296-307行）：**
```python
if __name__ == '__main__':
    # Get local IP
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'
        
    print(f"Server running at http://{local_ip}:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

**修改為（支援Render的PORT環境變數）：**
```python
if __name__ == '__main__':
    import os
    import socket
    
    # Render會提供PORT環境變數
    port = int(os.environ.get('PORT', 5000))
    
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'
        
    print(f"Server running at http://{local_ip}:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
```

**修改步驟：**
1. 在GitHub上點選 `server.py`
2. 點選編輯按鈕（鉛筆圖示）
3. 替換上述代碼
4. 點選 **Commit changes**

---

### 步驟3: 部署到Render (5分鐘)

#### 3.1 註冊Render

1. 前往 https://render.com
2. 點選 **Get Started for Free**
3. 選擇 **Sign up with GitHub**（用GitHub帳號登入）
4. 授權Render存取您的repositories

#### 3.2 創建Web Service

1. 登入後，點選 **New +** → **Web Service**
2. 選擇您剛建立的repository：`lunar-horse-race`
3. 點選 **Connect**

#### 3.3 設定Web Service

填寫以下資訊：

| 欄位 | 值 |
|------|-----|
| **Name** | `lunar-horse-race`（或任何名稱） |
| **Region** | Singapore（選最近的） |
| **Branch** | `main` |
| **Root Directory** | 留空 |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python server.py` |
| **Instance Type** | **Free** ✅ |

#### 3.4 新增環境變數（選用）

在 **Environment Variables** 區域，可以新增：

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.10.0` |

#### 3.5 部署

1. 點選 **Create Web Service**
2. Render會開始部署（需時3-5分鐘）
3. 等待狀態變為 **Live** ✅

---

### 步驟4: 取得網址並測試 (1分鐘)

部署完成後：

1. Render會提供網址，例如：`https://lunar-horse-race.onrender.com`
2. 點選該網址測試
3. 應該看到遊戲主持人畫面！

---

## 📱 使用方式

### 分享網址給親友

您的遊戲網址：
```
https://您的服務名稱.onrender.com
```

例如：`https://lunar-horse-race.onrender.com`

### 手機掃QR Code

1. 開啟遊戲頁面
2. 手機掃描QR Code
3. 自動導向遊戲（HTTPS，iOS可完整搖動！）

---

## ⚡ 重要注意事項

### 休眠機制

**Render免費方案限制：**
- 15分鐘無人訪問會**自動休眠**
- 下次訪問需等**10-15秒喚醒**

**解決方案（過年使用時）：**

1. **提前5分鐘喚醒**
   - 遊戲開始前先開啟網址
   - 等待10秒載入完成

2. **使用UptimeRobot保持喚醒**（選用）
   - 註冊 https://uptimerobot.com（免費）
   - 新增Monitor監控您的網址
   - 每5分鐘自動ping一次，保持服務運行

### 效能限制

免費方案規格：
- RAM: 512MB
- CPU: 共享
- 建議同時遊戲人數：**10人以內**

如果人數較多（>10人），建議：
- 升級到付費方案（$7/月）
- 或使用NAS部署

---

## 🔧 管理與更新

### 查看日誌

1. 登入Render Dashboard
2. 選擇您的服務
3. 點選 **Logs** 標籤
4. 即時查看伺服器日誌

### 更新程式碼

**方法1: GitHub網頁編輯**
1. 在GitHub上編輯檔案
2. Commit changes
3. Render會**自動重新部署**（2-3分鐘）

**方法2: 手動重新部署**
1. 登入Render Dashboard
2. 點選 **Manual Deploy** → **Deploy latest commit**

### 停止服務

1. Render Dashboard → 您的服務
2. **Settings** → **Delete Web Service**

（不用時可刪除，需要時再重新部署）

---

## 💰 費用說明

**Render免費方案：**
- ✅ 完全免費
- ✅ 無需信用卡
- ✅ 每月750小時免費運行時間（足夠個人使用）
- ✅ 自動HTTPS
- ⚠️ 15分鐘無活動會休眠

**付費方案（選用）：**
- Starter: $7/月
  - 不會休眠
  - 更好的效能
  - 支援更多人同時遊戲

---

## 🆚 方案比較建議

### 選擇 Render 雲端部署，如果您：
- ✅ 沒有NAS
- ✅ 想要最簡單的方式
- ✅ 每次遊戲人數 < 10人
- ✅ 不介意首次訪問需等待10秒
- ✅ 一年只玩幾次（過年、聚會）

### 選擇 NAS 部署，如果您：
- ✅ 已有NAS（如DS420j）
- ✅ 需要長時間運行
- ✅ 遊戲人數較多（>10人）
- ✅ 重視數據隱私（都在自家網路）
- ✅ 想要完全掌控

---

## 🎯 快速決策流程圖

```
有NAS嗎？
├─ 是 → 想要最簡單？
│         ├─ 是 → Render雲端部署 ⭐
│         └─ 否 → NAS部署
└─ 否 → Render雲端部署 ⭐⭐⭐
```

---

## ❓ 常見問題

### Q: Render會不會很慢？
A: 正常情況下很順暢。但：
- 首次訪問需10秒喚醒（休眠後）
- 建議選Singapore區域（離台灣近）
- 10人以內遊戲體驗良好

### Q: 可以用自己的網域嗎？
A: 可以！Render支援自訂網域：
1. 在DNS設定CNAME指向Render
2. Render Dashboard → Settings → Custom Domain
3. 免費SSL自動配置

### Q: GitHub必須Public嗎？
A: Render免費方案需要Public repository。
- 如需Private，需升級Render付費方案
- 或使用NAS部署

### Q: 如何防止別人惡意使用？
A: 建議：
1. 不公開分享網址（只給親友）
2. 遊戲結束後刪除Render服務
3. 或在host.html加入簡單密碼保護

### Q: 可以同時有NAS和Render嗎？
A: 可以！
- Render當備用方案（外出、朋友家聚會）
- NAS當主要方案（家中使用）

---

## 🎉 完成！

部署到Render只需**10分鐘**，就能獲得：
- ✅ 自動HTTPS網址
- ✅ iOS完整搖動功能
- ✅ 無需設定路由器
- ✅ 無需管理伺服器

**網址範例：** `https://lunar-horse-race.onrender.com`

**分享給親友，開始玩吧！🐴🧧**

---

## 📞 需要協助？

部署過程中遇到問題，請提供：
1. Render Logs截圖
2. 錯誤訊息
3. GitHub repository網址

我會協助您解決！
