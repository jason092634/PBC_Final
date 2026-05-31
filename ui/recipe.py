import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 引入資料庫、演算法與匯出工具
from db.database import get_all_ingredients, get_all_recipes
from utils.recommender import recommend_recipes
from utils.exporter import export_shopping_list

class RecipePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        """建構食譜頁面"""
        # --- 標題區 ---
        header_frame = ttk.Frame(self, style="Main.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(header_frame, text="🍳 智慧食譜篩選推薦", style="Title.TLabel").pack(side="left")
        
        ttk.Button(header_frame, text="🔄 依最新庫存算食譜", style="Action.TButton", 
                   command=self.load_and_calculate_recipes).pack(side="right", padx=5)

        # 捲動區域 (處理食譜卡片過多)
        container = ttk.Frame(self, style="Main.TFrame")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="#0F172A", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style="Main.TFrame")

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 底部操作區
        action_frame = ttk.Frame(self, style="Main.TFrame", padding=(0, 20, 0, 0))
        action_frame.pack(fill="x", side="bottom")

        ttk.Button(action_frame, text="📝 匯出缺少食材(採購清單)", style="Action.TButton",
                   command=self.on_export_shopping_list).pack(side="left")
        
        ttk.Button(action_frame, text="🛒 前往庫存管理 ➔", style="Action.TButton",
                   command=lambda: self.controller.show_frame("Inventory")).pack(side="right")

    def load_and_calculate_recipes(self):
        """讀取真實資料庫，呼叫組員 C 的演算法算分數，動態畫出卡片"""
        # 清空舊卡片
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 1. 從資料庫拿到最新食材與食譜
        fridge_ingredients = get_all_ingredients()
        all_recipes = get_all_recipes()

        # 2. 呼叫組員 C 寫的演算法 (recommender.py)
        # 這裡會算得分數，並由高到低排序好
        self.computed_results = recommend_recipes(fridge_ingredients, all_recipes)

        if not self.computed_results:
            ttk.Label(self.scrollable_frame, text="目前食譜庫中沒有任何食譜，請先建立資料。", style="CardText.TLabel").pack(pady=20)
            return

        # 3. 根據算出的結果，動態建立美美的卡片
        for rcp in self.computed_results:
            self._create_recipe_card(rcp)

    def _create_recipe_card(self, recipe):
        """建立單個食譜卡片元件"""
        card = ttk.Frame(self.scrollable_frame, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=10, padx=5)
        
        # 卡片標題與匹配度
        title_row = ttk.Frame(card, style="Card.TFrame")
        title_row.pack(fill="x")
        
        ttk.Label(title_row, text=recipe["name"], style="CardTitle.TLabel").pack(side="left")
        
        # 匹配度顏色區分 (大於等於70%用翡翠綠，否則用玫瑰紅)
        match_color = "#10B981" if recipe["match_rate"] >= 70 else "#F43F5E"
        match_label = tk.Label(title_row, text=f"{recipe['match_rate']}% 匹配", 
                              bg=match_color, fg="white", font=("Arial", 10, "bold"), padx=10)
        match_label.pack(side="right")
        
        # 食材詳細資訊
        info_text = f"所需食材：{recipe['ingredients']}\n目前缺少：{recipe['missing']}"
        ttk.Label(card, text=info_text, style="CardText.TLabel").pack(anchor="w", pady=(10, 5))
        
        ttk.Label(card, text=f"💡 烹飪提示：{recipe['status']}", style="CardText.TLabel", foreground="#94A3B8").pack(anchor="w")

    def on_export_shopping_list(self):
        """蒐集當前缺少的食材，塞入預設日期欄位以相容組員 D 的 exporter.py 格式"""
        if_calculated = getattr(self, "computed_results", None)
        if not if_calculated:
            messagebox.showwarning("提示", "請先點選右上角『依最新庫存算食譜』生成清單！")
            return

        # 1. 蒐集所有缺少的食材，過濾掉"無"
        missing_set = set()
        for rcp in self.computed_results:
            if rcp["missing"] != "無":
                # 將「雞蛋、起司」拆開加入集合，避免重複
                for item in rcp["missing"].split("、"):
                    missing_set.add(item.strip())

        if not missing_set:
            messagebox.showinfo("太讚了", "目前冰箱食材充足，沒有缺少的食材需要採買！")
            return

        # 🌟 核心修正點：
        # 因為組員 D 的匯出函數會去讀取 'expiry_date' 等庫存相關欄位
        # 我們在這裡把每一筆採購項目塞入「今天」作為預設日期，以防止他的程式碼報錯。
        from datetime import date
        today_str = date.today().strftime("%Y-%m-%d")

        shopping_data = []
        for item in missing_set:
            shopping_data.append({
                "name": item,
                "quantity": 1.0,        # 預設採購數量
                "unit": "份",           # 預設單位
                "purchase_date": today_str, # 💡 補上這個以防組員的代碼爆掉
                "expiry_date": today_str,   # 💡 補上這個！滿足他的 _days_until_expiry 運算
                "status": "ok"          # 預設狀態
            })

        # 2. 彈出儲存檔案視窗
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile="採購清單.csv",
            title="儲存採購清單", filetypes=[("CSV 檔案", "*.csv")]
        )
        if not filepath: 
            return

        # 3. 呼交組員 D 的匯出工具
        result = export_shopping_list(shopping_data, filepath)
        
        # 4. 顯示結果
        if result.get("success") or (isinstance(result, dict) and result.get("success") == True): 
            messagebox.showinfo("匯出成功", result.get("message", "已成功導出採購清單！"))
        else: 
            # 如果對方回傳的是字串或其他結構，做個安全的 fallback 處理
            msg = result.get("message") if isinstance(result, dict) else "導出失敗，請確認檔案未被開啟。"
            messagebox.showerror("匯出失敗", msg)