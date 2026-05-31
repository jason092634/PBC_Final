import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date

from db.database import get_all_ingredients, get_all_recipes, add_recipe_to_db
from utils.recommender import recommend_recipes
from utils.exporter import export_shopping_list

class RecipePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.computed_results = []  # 儲存計算結果，供匯出採購清單使用
        self._build_ui()

    def _build_ui(self):
        # 頂部標題與操作區
        header_frame = ttk.Frame(self, style="Main.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(header_frame, text="🍳 智慧食譜篩選推薦", style="Title.TLabel").pack(side="left")
        
        # 按鈕區 (靠右排列)
        ttk.Button(header_frame, text="🔄 依最新庫存算食譜", style="Action.TButton", 
                   command=self.load_and_calculate_recipes).pack(side="right", padx=(5, 0))

        ttk.Button(header_frame, text="➕ 新增私房食譜", style="Action.TButton", 
                   command=self.open_add_recipe_window).pack(side="right", padx=5)

        # --- 全局中央滾動區域 (包含左右兩欄) ---
        container = ttk.Frame(self, style="Main.TFrame")
        container.pack(fill="both", expand=True, pady=(0, 15))
        
        self.canvas = tk.Canvas(container, bg="#0F172A", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        # 內層放置大版面的容器
        self.scrollable_frame = ttk.Frame(self.canvas, style="Main.TFrame")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 讓內層滾動容器在主視窗拉大時，能夠等寬延展
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

        # 底部動作區
        action_frame = ttk.Frame(self, style="Main.TFrame")
        action_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(action_frame, text="想要做的料理缺少食材？", style="CardText.TLabel", 
                  foreground="#94A3B8").pack(side="left")
                  
        ttk.Button(action_frame, text="🛒 匯出缺少食材(採購清單) ➔", style="Warning.TButton",
                   command=self.on_export_shopping_list).pack(side="right")

    def load_and_calculate_recipes(self):
        """讀取資料庫並計算推薦食譜，並分成 100% 與 非 100% 兩欄展示"""
        ingredients = get_all_ingredients()
        recipes = get_all_recipes()
        
        # 呼叫演算法
        self.computed_results = recommend_recipes(ingredients, recipes)
        
        # 清空舊畫面
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.computed_results:
            ttk.Label(self.scrollable_frame, text="目前沒有食譜資料，請先新增食譜！", 
                      style="CardText.TLabel").pack(pady=20, padx=20)
            return

        # 🌟 核心排版改造：建立左欄與右欄的獨立容器 (Frame)
        # 為了美觀，為兩欄加上稍有區隔的深色背板
        left_column = ttk.LabelFrame(self.scrollable_frame, text="✨ 現有食材即可烹飪 (100% 匹配)", style="Card.TFrame", padding=10)
        left_column.grid(row=0, column=0, padx=15, pady=5, sticky="nsew")
        
        right_column = ttk.LabelFrame(self.scrollable_frame, text="❌ 尚缺部分食材 (需要採購)", style="Card.TFrame", padding=10)
        right_column.grid(row=0, column=1, padx=15, pady=5, sticky="nsew")

        # 追蹤左右兩欄目前排到第幾行卡片
        left_row_idx = 0
        right_row_idx = 0

        # 將食譜進行分類投放
        for recipe in self.computed_results:
            if recipe["match_rate"] == 100:
                self._create_recipe_card(left_column, recipe, left_row_idx)
                left_row_idx += 1
            else:
                self._create_recipe_card(right_column, recipe, right_row_idx)
                right_row_idx += 1

        # 如果某個分類是空的，貼心加上提示字眼，畫面更完整
        if left_row_idx == 0:
            ttk.Label(left_column, text="目前沒有 100% 匹配的食譜\n趕快清點冰箱補貨吧！", 
                      style="CardText.TLabel", justify="center").pack(pady=30)
        if right_row_idx == 0:
            ttk.Label(right_column, text="太棒了！目前的材料\n足以應付所有的食譜！", 
                      style="CardText.TLabel", justify="center").pack(pady=30)

    def _create_recipe_card(self, parent_column, recipe, row_idx):
        """在指定的欄位容器中，由上而下垂直堆疊建立食譜卡片"""
        card = ttk.Frame(parent_column, style="Card.TFrame", padding=15)
        card.pack(fill="x", pady=10, padx=5)
        
        # 卡片內標題列
        title_row = ttk.Frame(card, style="Card.TFrame")
        title_row.pack(fill="x", pady=(0, 8))
        
        ttk.Label(title_row, text=recipe["name"], style="CardTitle.TLabel").pack(side="left")
        
        match_color = "#10B981" if recipe["match_rate"] == 100 else "#F43F5E"
        match_label = tk.Label(title_row, text=f"{recipe['match_rate']}% 匹配", 
                              bg=match_color, fg="white", font=("Arial", 9, "bold"), padx=8, pady=2)
        match_label.pack(side="right")
        
        # 食材與步驟詳細資訊
        info_text = (
            f"🔹 所需食材：{recipe['ingredients']}\n"
            f"❌ 目前缺少：{recipe['missing']}\n"
            f"📝 烹飪步驟：{recipe.get('instructions', '無步驟說明。')}"
        )
        
        # wraplength 設定在 350~400 之間，防止視窗縮小時文字爆開
        text_label = ttk.Label(card, text=info_text, style="CardText.TLabel", justify="left", wraplength=380)
        text_label.pack(anchor="w", fill="both", expand=True)

    def open_add_recipe_window(self):
        """彈出新增食譜視窗"""
        dialog = tk.Toplevel(self)
        dialog.title("新增私房食譜")
        dialog.geometry("400x320")
        dialog.configure(bg="#1E293B")
        dialog.transient(self)
        dialog.grab_set()

        lbl_style = {"bg": "#1E293B", "fg": "#F8FAFC", "font": ("微軟正黑體", 10, "bold")}
        
        tk.Label(dialog, text="食譜名稱：", **lbl_style).pack(anchor="w", padx=20, pady=(20, 2))
        entry_name = tk.Entry(dialog, font=("微軟正黑體", 10), bg="#0F172A", fg="#F8FAFC", insertbackground="white")
        entry_name.pack(fill="x", padx=20)

        tk.Label(dialog, text="所需食材 (請以頓號或逗號隔開)：", **lbl_style).pack(anchor="w", padx=20, pady=(15, 2))
        entry_ingredients = tk.Entry(dialog, font=("微軟正黑體", 10), bg="#0F172A", fg="#F8FAFC", insertbackground="white")
        entry_ingredients.pack(fill="x", padx=20)
        
        tk.Label(dialog, text="例如：雞肉、香菇、醬油", bg="#1E293B", fg="#94A3B8", font=("微軟正黑體", 9)).pack(anchor="w", padx=20)

        def save_recipe():
            name = entry_name.get().strip()
            raw_ingredients = entry_ingredients.get().strip()

            if not name or not raw_ingredients:
                messagebox.showwarning("提示", "請填寫完整欄位！", parent=dialog)
                return

            processed_ing = raw_ingredients.replace("，", "|").replace("、", "|").replace(",", "|")
            ing_list = [i.strip() for i in processed_ing.split("|") if i.strip()]
            final_ingredients_str = "|".join(ing_list)

            success = add_recipe_to_db(name, final_ingredients_str)
            if success:
                messagebox.showinfo("成功", f"食譜「{name}」已成功儲存！", parent=dialog)
                dialog.destroy()
                self.load_and_calculate_recipes()  # 即時刷新主畫面
            else:
                messagebox.showerror("錯誤", "儲存失敗，食譜名稱可能重複。", parent=dialog)

        ttk.Button(dialog, text="儲存食譜", style="Action.TButton", command=save_recipe).pack(pady=25)

    def on_export_shopping_list(self):
        """匯出採購清單"""
        if_calculated = getattr(self, "computed_results", None)
        if not if_calculated:
            messagebox.showwarning("提示", "請先點選『依最新庫存算食譜』生成清單")
            return

        missing_set = set()
        for rcp in self.computed_results:
            if rcp["missing"] != "無":
                for item in rcp["missing"].split("、"):
                    missing_set.add(item.strip())

        if not missing_set:
            messagebox.showinfo("提示", "目前食材充足，無須採買。")
            return

        today_str = date.today().strftime("%Y-%m-%d")
        shopping_data = [{
            "name": item,
            "quantity": 1.0,
            "unit": "份",
            "purchase_date": today_str,
            "expiry_date": today_str,
            "status": "ok"
        } for item in missing_set]

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile="採購清單.csv",
            title="儲存採購清單", filetypes=[("CSV 檔案", "*.csv")]
        )
        if not filepath: 
            return

        result = export_shopping_list(shopping_data, filepath)
        
        if result.get("success") or (isinstance(result, dict) and result.get("success") == True):
            messagebox.showinfo("匯出成功", result.get("message", "已成功導出採購清單！"))
        else:
            msg = result.get("message") if isinstance(result, dict) else "導出失敗，請確認檔案未被開啟。"
            messagebox.showerror("匯出失敗", msg)