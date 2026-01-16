# 🎊 過年紅包賽馬遊戲 - NAS部署指引

## 📋 部署前準備清單

請填寫以下資訊,以便選擇最適合的部署方案:

### 1. NAS環境
- **NAS品牌與型號**: ___________________
- **作業系統版本**: ___________________
- **是否支援Docker**: □ 是 □ 否 □ 不確定
- **是否可SSH連線**: □ 是 □ 否

### 2. 網路環境
- **內網IP配置**:
  - NAS內網IP: ___________________
  - 是否固定IP: □ 是 □ 否
  
- **外網IP配置**:
  - 外網IP類型: □ 固定IP □ 動態IP
  - 外網IP位址(如知道): ___________________

- **路由器資訊**:
  - 品牌型號: ___________________
  - 管理介面網址: ___________________

### 3. 網域與SSL偏好
- **網域名稱**:
  - 是否有網域: □ 有 (網域名稱: ___________________) □ 沒有
  - DNS服務商: ___________________

- **SSL方案偏好** (請選擇一項):
  - □ **方案A**: Cloudflare Tunnel (最簡單,推薦!)
    - 需求: Cloudflare帳號 + 網域
    - 優點: 免Port Forwarding、自動HTTPS、隱藏IP
  
  - □ **方案B**: Let's Encrypt SSL
    - 需求: 網域 + Port Forwarding設定
    - 優點: 標準方案、免費SSL
  
  - □ **方案C**: 僅HTTP (快速測試)
    - 需求: Port Forwarding設定
    - 限制: ⚠️ iOS無法使用搖動功能,只能用TAP按鈕

---

## 🚀 快速部署 - 選項1: Docker部署 (推薦)

### 步驟1: 準備檔案
1. 將整個專案資料夾上傳到NAS (例如: `/volume1/docker/horse-race/`)
2. 確認包含以下檔案:
   - `Dockerfile`
   - `docker-compose.yml`
   - `server.py`
   - `requirements.txt`
   - `templates/` 資料夾
   - `static/` 資料夾

### 步驟2: SSH連線到NAS
```bash
ssh your-nas-username@<NAS-IP>
cd /volume1/docker/horse-race/
```

### 步驟3: 啟動服務
```bash
# 使用Docker Compose啟動
docker-compose up -d

# 查看日誌確認啟動成功
docker-compose logs -f
```

### 步驟4: 測試本地訪問
在同一區網的電腦或手機瀏覽器開啟:
```
http://<NAS-IP>:5000
```

應該會看到主持人畫面和QR Code!

---

## 🏃 快速部署 - 選項2: 直接Python執行

如果NAS不支援Docker,可以直接執行Python:

### 步驟1: SSH連線並安裝依賴
```bash
ssh your-nas-username@<NAS-IP>
cd /path/to/horse-race/

# 安裝Python依賴
pip3 install -r requirements.txt
# 或
python3 -m pip install -r requirements.txt
```

### 步驟2: 執行伺服器
```bash
python3 server.py
```

### 步驟3: 測試訪問
```
http://<NAS-IP>:5000
```

---

## 🌐 外網訪問設定

### 方法A: Cloudflare Tunnel (最簡單!)

**前置需求:**
- Cloudflare帳號 (免費)
- 網域名稱 (指向Cloudflare DNS)

**步驟:**

1. **安裝cloudflared** (在NAS上)
```bash
# 下載cloudflared (依NAS架構選擇)
# for x86_64
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# for ARM
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
chmod +x cloudflared-linux-arm64
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
```

2. **登入Cloudflare**
```bash
cloudflared tunnel login
```
瀏覽器會開啟,選擇您的網域並授權。

3. **創建Tunnel**
```bash
cloudflared tunnel create horse-race
```
記下 Tunnel ID。

4. **設定Tunnel路由**
```bash
# 創建配置檔
nano ~/.cloudflared/config.yml
```

貼上以下內容 (修改YOUR_TUNNEL_ID和YOUR_DOMAIN):
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /root/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: game.YOUR_DOMAIN.com
    service: http://localhost:5000
  - service: http_status:404
```

5. **設定DNS**
```bash
cloudflared tunnel route dns horse-race game.YOUR_DOMAIN.com
```

6. **啟動Tunnel**
```bash
cloudflared tunnel run horse-race
```

7. **設定開機自動啟動** (選用)
```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

完成! 現在訪問 `https://game.YOUR_DOMAIN.com` 即可!

---

### 方法B: Port Forwarding + Let's Encrypt

**步驟1: 路由器Port Forwarding設定**

登入路由器管理介面,設定Port Forwarding:
- 外部端口: `5000` (或其他如80, 443)
- 內部IP: `<NAS-IP>`
- 內部端口: `5000`
- 協議: `TCP`

**步驟2: 設定DNS記錄**

在您的DNS服務商 (如Cloudflare, GoDaddy):
- 類型: `A`
- 名稱: `game` (或其他子網域)
- 內容: `<您的外網IP>`
- TTL: Auto

**步驟3: 安裝Nginx和Certbot** (用於SSL)

```bash
# Synology DSM
sudo apt-get update
sudo apt-get install nginx certbot python3-certbot-nginx

# 或使用NAS套件中心安裝Nginx
```

**步驟4: 取得SSL憑證**
```bash
sudo certbot --nginx -d game.yourdomain.com
```

**步驟5: 設定Nginx反向代理**

編輯 `/etc/nginx/sites-available/horse-race`:
```nginx
server {
    listen 80;
    server_name game.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name game.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/game.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/game.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

啟用網站:
```bash
sudo ln -s /etc/nginx/sites-available/horse-race /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

完成! 訪問 `https://game.yourdomain.com`

---

### 方法C: 簡單HTTP + Port Forwarding

⚠️ **注意**: iOS用戶無法使用搖動功能,只能用TAP按鈕!

**步驟1: 路由器Port Forwarding**
- 外部端口: `5000`
- 內部IP: `<NAS-IP>`
- 內部端口: `5000`

**步驟2: 訪問**
```
http://<外網IP>:5000
```

---

## 🧪 測試檢查清單

完成部署後,請依序測試:

### ✅ 本地網路測試
- [ ] 在電腦瀏覽器開啟遊戲主持人頁面
- [ ] 看到QR Code
- [ ] 手機連接同一WiFi,掃描QR Code
- [ ] 手機成功加入遊戲
- [ ] 在主持人頁面看到玩家頭像

### ✅ 外網測試
- [ ] 手機關閉WiFi,使用4G/5G網路
- [ ] 掃描QR Code或輸入網址
- [ ] 成功連線

### ✅ 手機功能測試 (iOS)
- [ ] 加入遊戲後看到「開啟搖晃感應📳」按鈕
- [ ] 點擊後允許動作感應權限
- [ ] 遊戲開始後搖動手機
- [ ] 馬匹在賽道上移動 (✅ 僅HTTPS可用)
- [ ] TAP按鈕可正常使用

### ✅ 手機功能測試 (Android)
- [ ] 加入遊戲後進入等待畫面
- [ ] 遊戲開始後搖動手機
- [ ] 馬匹移動正常
- [ ] TAP按鈕可正常使用

### ✅ 多人遊戲測試
- [ ] 3-5人同時加入
- [ ] 所有玩家都顯示在主持人畫面
- [ ] 開始遊戲,所有人可同時操作
- [ ] 遊戲結束後排名正確
- [ ] 所有手機都顯示獲獎資訊

---

## ❓ 常見問題

### Q1: iOS無法搖動怎麼辦?
**A**: 檢查是否使用HTTPS。iOS 13+必須使用HTTPS才能存取動作感應器。如果是HTTP,請使用TAP按鈕。

### Q2: Socket.IO連線失敗?
**A**: 
1. 檢查防火牆是否開放5000端口
2. 如使用Nginx,確認WebSocket upgrade設定正確
3. 檢查瀏覽器Console的錯誤訊息

### Q3: QR Code掃描後連不上?
**A**:
1. 確認手機網路可以訪問NAS IP
2. 如果是外網,確認Port Forwarding設定正確
3. 檢查QR Code中的網址是否正確

### Q4: 遊戲進行中斷線?
**A**:
1. 手機可能進入省電模式,關閉瀏覽器
2. Socket.IO會自動重連,刷新頁面即可
3. 確保NAS不會進入休眠模式

### Q5: 多人遊戲卡頓?
**A**:
1. 檢查NAS網路頻寬
2. 建議玩家人數控制在10人以內
3. 確保NAS效能足夠 (CPU/RAM)

---

## 📞 需要協助?

如遇到問題,請提供:
1. NAS型號和作業系統
2. 選擇的部署方案
3. 錯誤訊息截圖
4. 瀏覽器Console日誌

我會協助您解決!

---

## 🎉 享受遊戲!

部署完成後,過年時就可以讓親朋好友一起玩賽馬遊戲領紅包啦! 🧧🐴

**祝您:**
- 🎊 馬到成功
- 🧧 萬馬奔騰  
- 🏆 龍馬精神
