# 智慧型冰箱食材與食譜管理系統 (Smart Fridge & Recipe Manager)
> **Programming for Business Computing — Final Project**
> 本專案為商管程式設計期末專案成果，以 Python 為基礎，結合動態時間演算法與關聯式資料庫架構，解決現代家庭食材浪費與飲食規劃之痛點。

## 專案核心亮點 (Core Features)
本系統採用 **Python Tkinter** 建構精美且具備現代感的深色主題 GUI 介面，並以 **SQLite** 作為資料庫核心，實作前後端分離架構。

### 1. 智慧冰箱庫存管理 (Inventory Management)
* **精準計量**：資料庫採用實數 (`REAL`) 型態，支援 `0.5 顆`、`1.5 瓶` 等非整數庫存紀錄。
* **動態計算**：系統讀取食材時，會自動將字串轉換為 `DATETIME` 物件，即時演算剩餘天數並反饋動態視覺標籤（`已過期` / `即期` / `安全`）。
* **即時調整**：支援選取食材後直接點擊修改按鈕，微調任意小數點庫存。

### 2. 智慧食譜篩選推薦 (Smart Recipe Recommendation)
* **即時匹配**：演算法動態比對冰箱現有食材與食譜需求，自動計算「匹配百分比」。
* **雙欄展示**：介面劃分為「*現有食材即可烹飪 (100% 匹配)*」與「*尚缺部分食材 (需要採購)*」，視覺效果簡單明確。
* **自訂食譜**：支援使用者一行輸入一個食材、多行自訂烹飪做法與步驟。

### 3. 高效率工具列操作 (Advanced UI/UX Command Bar)
* **批次匯出採購清單**：勾選想做的食譜，系統自動彙整所有缺少的食材，一鍵導出客製化採購 CSV 表。
* **批次刪除食材食譜**：食譜與食材皆支援多選方格勾選，後端進行 `for-loop` 批次刪除，並具備二階安全確認視窗防呆。

## 專案目錄結構 (Project Architecture)

fridge_project/               # 專案主資料夾
├── db/
│   ├── __init__.py
│   └── database.py           # 資料庫核心 (SQLite 綱要、時效演算、API)
├── ui/
│   ├── __init__.py
│   ├── window.py             # 導覽/視窗主架構切換
│   ├── inventory.py          # 食材庫存管理介面
│   └── recipe.py             # 智慧食譜推薦介面
├── utils/
│   ├── __init__.py
│   ├── recommender.py        # 智慧食譜匹配演算法
│   └── exporter.py           # 採購清單與庫存數據 CSV 匯出
├── data/
│   ├── mock_ingredients.csv  # 初始食材假資料
│   └── mock_recipes.csv      # 初始食譜假資料
├── main.py                   # 專案啟動進入點
└── README.md                 # 專案說明文件

環境需求與安裝指南 (Installation & Setup)
本系統採用 Python 標準庫開發，無需安裝任何額外的第三方套件，確保系統具備極高的跨平台移植性。

1. 必備環境
Python 3.8+ (已內建 tkinter 與 sqlite3)

2. 啟動步驟
請在解壓縮後的專案根目錄下，開啟終端機 (Terminal) 或命令提示字元 (CMD)，執行以下指令：python main.py

系統首次啟動時，主程式會自動檢測。若偵測到 fridge.db 資料庫不存在，會自動建立完備的資料表，並讀取 data/ 中的 CSV 檔案進行初始自動化假資料匯入，使用者可直接看到完整的系統 Demo 狀態。