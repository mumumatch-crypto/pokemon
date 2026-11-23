# 寶可夢圖片探索站

使用 Python 3.12、Flask 與原生 HTML/CSS/JavaScript 建置的繁體中文響應式網站。瀏覽器透過同來源 `/api/pokemon` 請求 Flask，由後端查詢 PokéAPI v2，並只傳回經 HTTPS 與主機白名單驗證的官方圖片網址。

## 本機執行

### Windows（PowerShell）

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest test_app.py -v
python -m flask --app app run
```

若 PowerShell 阻止啟用虛擬環境，可在目前視窗執行 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 後再啟用。

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest test_app.py -v
python -m flask --app app run
```

啟動後開啟 http://127.0.0.1:5000 。測試使用 Python 內建 `unittest` 與 mock，不會呼叫真正的 PokéAPI。

## 推送至 GitHub

先在 GitHub 建立一個空白 repository，再於專案根目錄執行以下指令，並把 `<你的 GitHub 帳號>` 與 `<repository 名稱>` 換成實際值：

```bash
git init
git add app.py templates/index.html requirements.txt .python-version .gitignore test_app.py README.md
git commit -m "建立寶可夢圖片探索站"
git branch -M main
git remote add origin https://github.com/<你的 GitHub 帳號>/<repository 名稱>.git
git push -u origin main
```

## 部署至 Vercel

1. 登入 Vercel，選擇 **Add New → Project**，匯入剛推送的 GitHub repository。
2. Framework Preset 保持自動辨識或 **Other**；Root Directory 使用 repository 根目錄。
3. **Build Command 保持預設留空**，Output Directory 與 Install Command 也使用預設值，不要建立 `vercel.json`。Vercel 會依根目錄的 `app.py` 自動辨識 Flask 應用，並依 `requirements.txt` 安裝執行依賴；手動指定 Build Command 會覆蓋框架自動設定，這個專案不需要自訂建置步驟。
4. 按下 **Deploy**。之後推送到連結的 GitHub 分支即可觸發新部署。

`.python-version` 指定 Python 3.12。應用採無狀態設計，不使用本機資料庫或永久檔案。PokéAPI 上游請求有 5 秒逾時，圖片僅允許 `raw.githubusercontent.com` 的 HTTPS 網址。
