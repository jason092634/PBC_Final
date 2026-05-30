import tkinter as tk
from tkinter import ttk

class RecipePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        
        # 模擬一些食譜資料 (未來這部分會跟組員的資料庫對接)
        self.mock_recipes = [
            {
                "name": "香煎鮮奶吐司",
                "match_rate": 100,
                "ingredients": "鮮奶、吐司、雞蛋",
                "missing": "無",
                "status": "現有食材即可烹飪"
            },
            {
                "name": "高麗菜炒蛋",
                "match_rate": 66,
                "ingredients": "高麗菜、雞蛋、大蒜",
                "missing": "雞蛋",
                "status": "缺少 1 項食材"
            },
            {
                "name": "法式起司吐司",
                "match_rate": 50,
                "ingredients": "吐司、起司、牛奶、奶油",
                "missing": "起司、奶油",
                "status": "缺少 2 項食材"
            }
        ]
        
        self._build_ui()

    def _build_ui(self):
        """建構食譜頁面"""
        # --- 標題區 ---
        header_frame = ttk.Frame(self, style="Main.TFrame")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        
        ttk.Label(header_frame, text="🍳 智能食譜推薦", style="Title.TLabel").pack(side="left")
        
        # 刷新按鈕：模擬重新計算食譜的動作
        refresh_btn = ttk.Button(header_frame, text="🔄 重新計算建議", style="Action.TButton")
        refresh_btn.pack(side="right")

        # --- 中央：食譜卡片顯示區 (使用 Canvas 模擬捲動效果) ---
        # 為了美觀，我們用卡片式排列
        self.canvas = tk.Canvas(self, bg="#0F172A", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Main.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(30, 0), pady=10)
        self.scrollbar.pack(side="right", fill="y", padx=(0, 30), pady=10)

        # 生成食譜卡片
        for recipe in self.mock_recipes:
            self._create_recipe_card(recipe)

        # --- 🌟 底部：場景連動專屬區塊 ---
        action_frame = ttk.Frame(self, style="Main.TFrame")
        action_frame.pack(fill="x", padx=30, pady=30)
        
        ttk.Label(action_frame, text="想要做的料理缺少食材嗎？", style="CardText.TLabel", foreground="#F8FAFC").pack(side="left")
        
        # 場景連動：發現缺料，跳回庫存頁面準備匯出採購單
        jump_btn = ttk.Button(action_frame, text="🛒 前往庫存匯出採購清單 ➔", style="Action.TButton",
                              command=lambda: self.controller.show_frame("Inventory"))
        jump_btn.pack(side="right")

    def _create_recipe_card(self, recipe):
        """建立單個食譜卡片元件"""
        card = ttk.Frame(self.scrollable_frame, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=10, padx=5)
        
        # 卡片標題與匹配度
        title_row = ttk.Frame(card, style="Card.TFrame")
        title_row.pack(fill="x")
        
        ttk.Label(title_row, text=recipe["name"], style="CardTitle.TLabel").pack(side="left")
        
        match_color = "#10B981" if recipe["match_rate"] == 100 else "#F43F5E"
        match_label = tk.Label(title_row, text=f"{recipe['match_rate']}% 匹配", 
                              bg=match_color, fg="white", font=("Arial", 10, "bold"), padx=10)
        match_label.pack(side="right")
        
        # 食材詳細資訊
        info_text = f"所需食材：{recipe['ingredients']}\n目前缺少：{recipe['missing']}"
        ttk.Label(card, text=info_text, style="CardText.TLabel", justify="left").pack(anchor="w", pady=10)
        
        # 狀態提示
        status_label = ttk.Label(card, text=f"● {recipe['status']}", style="CardText.TLabel")
        if "缺少" in recipe["status"]:
            status_label.configure(foreground="#F43F5E") # 顯示警告色
        else:
            status_label.configure(foreground="#10B981") # 顯示成功色
        status_label.pack(anchor="w")