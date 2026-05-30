import tkinter as tk
from tkinter import ttk

# 預留你的外部模組
# from ui.inventory import InventoryPage

class MainWindow:
    def __init__(self, root):
        self.root = root
        
        # ==========================================
        # 🎨 1. 高階科技質感配色 (Dark IoT Theme)
        # ==========================================
        self.BG_COLOR = "#0F172A"       # 深板岩灰 (主背景)
        self.CARD_COLOR = "#1E293B"     # 區塊背景 (卡片)
        self.ACCENT_COLOR = "#10B981"   # 科技翡翠綠 (主要動作)
        self.TEXT_MAIN = "#F8FAFC"      # 亮白 (主標題)
        self.TEXT_MUTED = "#94A3B8"     # 灰白 (副標題)
        self.WARNING_COLOR = "#F43F5E"  # 玫瑰紅 (警告/過期)

        self._setup_styles()

        # ==========================================
        # 🏗️ 2. 全局頂部導航列 (Global Header)
        # ==========================================
        self.header_frame = ttk.Frame(self.root, style="Header.TFrame", padding=(20, 15))
        self.header_frame.pack(fill="x", side="top")
        
        # 系統標題
        ttk.Label(self.header_frame, text="⚡ SMART FRIDGE", font=("Arial", 16, "bold"), 
                  style="Header.TLabel").pack(side="left")
        
        # 全局返回首頁按鈕 (隱藏在右上角，隨時可點)
        self.home_btn = ttk.Button(self.header_frame, text="🏠 返回儀表板", style="Action.TButton",
                                   command=lambda: self.show_frame("Dashboard"))
        self.home_btn.pack(side="right")

        # ==========================================
        # 🗂️ 3. 建立 SPA 路由容器 (Frame Router)
        # ==========================================
        self.container = ttk.Frame(self.root, style="Main.TFrame")
        self.container.pack(fill="both", expand=True)
        # 設定 grid 權重，讓裡面的分頁能 100% 填滿
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # 儲存所有分頁的字典
        self.frames = {}
        
        # 初始化所有頁面並放入容器
        self._build_dashboard_page()
        self._build_mock_inventory_page() # 之後替換成你的 InventoryPage
        self._build_mock_recipe_page()

        # 啟動時，將「首頁儀表板」升到最上層顯示
        self.show_frame("Dashboard")
        print("[UI] 智慧路由與深色儀表板載入完成。")

    # ==========================================
    # 邏輯核心：畫面切換器
    # ==========================================
    def show_frame(self, page_name):
        """將指定的分頁推到畫面的最上層 (tkraise)"""
        frame = self.frames[page_name]
        frame.tkraise()

    # ==========================================
    # 樣式設定
    # ==========================================
    def _setup_styles(self):
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
            
        # 全局背景
        self.style.configure("Main.TFrame", background=self.BG_COLOR)
        self.style.configure("Header.TFrame", background=self.CARD_COLOR)
        self.style.configure("Card.TFrame", background=self.CARD_COLOR)
        
        # 標題與內文
        self.style.configure("Header.TLabel", background=self.CARD_COLOR, foreground=self.ACCENT_COLOR)
        self.style.configure("Title.TLabel", background=self.BG_COLOR, foreground=self.TEXT_MAIN, font=("微軟正黑體", 24, "bold"))
        self.style.configure("CardTitle.TLabel", background=self.CARD_COLOR, foreground=self.TEXT_MAIN, font=("微軟正黑體", 16, "bold"))
        self.style.configure("CardText.TLabel", background=self.CARD_COLOR, foreground=self.TEXT_MUTED, font=("微軟正黑體", 12))
        
        # 動作按鈕 (翡翠綠)
        self.style.configure("Action.TButton", font=("微軟正黑體", 11, "bold"), 
                             background=self.ACCENT_COLOR, foreground=self.BG_COLOR, borderwidth=0, padding=8)
        self.style.map("Action.TButton", background=[("active", "#059669")])
        
        # 警告按鈕 (玫瑰紅)
        self.style.configure("Warning.TButton", font=("微軟正黑體", 11, "bold"), 
                             background=self.WARNING_COLOR, foreground=self.TEXT_MAIN, borderwidth=0, padding=8)
        self.style.map("Warning.TButton", background=[("active", "#E11D48")])

    # ==========================================
    # 頁面 1：首頁儀表板 (Dashboard)
    # ==========================================
    def _build_dashboard_page(self):
        frame = ttk.Frame(self.container, style="Main.TFrame", padding=30)
        frame.grid(row=0, column=0, sticky="nsew") # 使用 grid 疊加
        self.frames["Dashboard"] = frame

        ttk.Label(frame, text="冰箱狀態總覽", style="Title.TLabel").pack(anchor="w", pady=(0, 20))

        # 建立卡片並排容器
        cards_frame = ttk.Frame(frame, style="Main.TFrame")
        cards_frame.pack(fill="x")

        # [左側卡片：庫存警報]
        left_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=20)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ttk.Label(left_card, text="⚠️ 即將過期", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(left_card, text="您有 2 項食材將在 3 天內過期。\n建議盡速處理以避免浪費。", style="CardText.TLabel").pack(anchor="w", pady=10)
        # 【場景連動】跳轉至庫存管理
        ttk.Button(left_card, text="前往清點庫存 ➔", style="Warning.TButton", 
                   command=lambda: self.show_frame("Inventory")).pack(anchor="w", pady=(10, 0))

        # [右側卡片：料理推薦]
        right_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=20)
        right_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        ttk.Label(right_card, text="💡 今日提案", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(right_card, text="目前庫存充足。\n根據您的食材，為您推薦 3 道料理。", style="CardText.TLabel").pack(anchor="w", pady=10)
        # 【場景連動】跳轉至食譜推薦
        ttk.Button(right_card, text="查看推薦食譜 ➔", style="Action.TButton", 
                   command=lambda: self.show_frame("Recipe")).pack(anchor="w", pady=(10, 0))

    # ==========================================
    # 頁面 2：食材庫存管理 (預留對接)
    # ==========================================
    def _build_mock_inventory_page(self):
        """這裡目前是示範，之後可直接替換成你寫好的 InventoryPage"""
        frame = ttk.Frame(self.container, style="Main.TFrame", padding=30)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames["Inventory"] = frame

        ttk.Label(frame, text="📦 食材庫存清單", style="Title.TLabel").pack(anchor="w", pady=(0, 20))
        
        # 模擬表格區塊
        mock_table = ttk.Frame(frame, style="Card.TFrame", height=200)
        mock_table.pack(fill="both", expand=True, pady=(0, 20))
        ttk.Label(mock_table, text="[ 食材表格渲染區 ]", style="CardText.TLabel").place(relx=0.5, rely=0.5, anchor="center")

        # 【極致場景連動】直接在表格下方提供「用現有食材做菜」的按鈕
        action_frame = ttk.Frame(frame, style="Main.TFrame")
        action_frame.pack(fill="x")
        ttk.Label(action_frame, text="食材太多不知道怎麼煮？", style="CardText.TLabel", foreground=self.TEXT_MAIN).pack(side="left")
        ttk.Button(action_frame, text="🍳 根據目前庫存生成食譜 ➔", style="Action.TButton", 
                   command=lambda: self.show_frame("Recipe")).pack(side="right")

    # ==========================================
    # 頁面 3：食譜智慧推薦 (預留對接)
    # ==========================================
    def _build_mock_recipe_page(self):
        frame = ttk.Frame(self.container, style="Main.TFrame", padding=30)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames["Recipe"] = frame

        ttk.Label(frame, text="🍳 食譜智慧推薦", style="Title.TLabel").pack(anchor="w", pady=(0, 20))
        
        mock_table = ttk.Frame(frame, style="Card.TFrame", height=200)
        mock_table.pack(fill="both", expand=True, pady=(0, 20))
        ttk.Label(mock_table, text="[ 食譜運算結果渲染區 ]", style="CardText.TLabel").place(relx=0.5, rely=0.5, anchor="center")

        # 【極致場景連動】在食譜區發現缺料，直接跳回庫存
        action_frame = ttk.Frame(frame, style="Main.TFrame")
        action_frame.pack(fill="x")
        ttk.Label(action_frame, text="想要做的料理缺少食材？", style="CardText.TLabel", foreground=self.TEXT_MAIN).pack(side="left")
        ttk.Button(action_frame, text="🛒 前往庫存匯出採購清單 ➔", style="Action.TButton", 
                   command=lambda: self.show_frame("Inventory")).pack(side="right")