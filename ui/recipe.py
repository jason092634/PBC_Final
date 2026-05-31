import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date

from db.database import get_all_ingredients, get_all_recipes, add_recipe_to_db, update_recipe_in_db
from utils.recommender import recommend_recipes
from utils.exporter import export_shopping_list

class RecipePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.computed_results = []  # 儲存食譜計算結果
        self.check_vars = {}        # 儲存每個食譜對應的 BooleanVar 狀態字典
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
                   command=lambda: self.open_recipe_window(mode="add")).pack(side="right", padx=5)

        # --- 全局中央滾動區域 ---
        container = ttk.Frame(self, style="Main.TFrame")
        container.pack(fill="both", expand=True, pady=(0, 15))
        
        self.canvas = tk.Canvas(container, bg="#0F172A", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas, style="Main.TFrame")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

        # 底部動作區
        action_frame = ttk.Frame(self, style="Main.TFrame")
        action_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(action_frame, text="💡 勾選想做的料理即可匯出專屬採購清單。點選卡片右下角可直接修改內容。", style="CardText.TLabel", 
                  foreground="#94A3B8").pack(side="left")
                  
        ttk.Button(action_frame, text="🛒 匯出所選食譜之採購清單 ➔", style="Warning.TButton",
                   command=self.on_export_shopping_list).pack(side="right")

    def load_and_calculate_recipes(self):
        """讀取資料庫並計算推薦食譜，並分成 100% 與 非 100% 兩欄展示"""
        ingredients = get_all_ingredients()
        recipes = get_all_recipes()
        
        self.computed_results = recommend_recipes(ingredients, recipes)
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.check_vars.clear()

        if not self.computed_results:
            ttk.Label(self.scrollable_frame, text="目前沒有食譜資料，請先新增食譜！", 
                      style="CardText.TLabel").pack(pady=20, padx=20)
            return

        left_column = ttk.LabelFrame(self.scrollable_frame, text="✨ 現有食材即可烹飪 (100% 匹配)", style="Card.TFrame", padding=10)
        left_column.grid(row=0, column=0, padx=15, pady=5, sticky="nsew")
        
        right_column = ttk.LabelFrame(self.scrollable_frame, text="❌ 尚缺部分食材 (需要採購)", style="Card.TFrame", padding=10)
        right_column.grid(row=0, column=1, padx=15, pady=5, sticky="nsew")

        left_row_idx = 0
        right_row_idx = 0

        for recipe in self.computed_results:
            self.check_vars[recipe["name"]] = tk.BooleanVar(master=self, value=False)
            
            if recipe["match_rate"] == 100:
                self._create_recipe_card(left_column, recipe)
                left_row_idx += 1
            else:
                self._create_recipe_card(right_column, recipe)
                right_row_idx += 1

        if left_row_idx == 0:
            ttk.Label(left_column, text="目前沒有 100% 匹配的食譜\n趕快清點冰箱補貨吧！", 
                      style="CardText.TLabel", justify="center").pack(pady=30)
        if right_row_idx == 0:
            ttk.Label(right_column, text="太棒了！目前的材料\n足以應付所有的食譜！", 
                      style="CardText.TLabel", justify="center").pack(pady=30)

    def _create_recipe_card(self, parent_column, recipe):
        """在指定的欄位容器中，建立食譜卡片"""
        card = ttk.Frame(parent_column, style="Card.TFrame", padding=15)
        card.pack(fill="x", pady=10, padx=5)
        
        # 卡片內標題列
        title_row = ttk.Frame(card, style="Card.TFrame")
        title_row.pack(fill="x", pady=(0, 8))
        
        # 質感優化：原生 tk.Checkbutton 搭配手動深色模式配色
        chk = tk.Checkbutton(title_row, 
                             variable=self.check_vars[recipe["name"]],
                             bg="#1E293B", activebackground="#1E293B",
                             selectcolor="#0F172A", bd=0, highlightthickness=0)
        chk.pack(side="left", padx=(0, 8))
        
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
        
        text_label = ttk.Label(card, text=info_text, style="CardText.TLabel", justify="left", wraplength=380)
        text_label.pack(anchor="w", fill="both", expand=True)

        # 🌟 新增：右下角「修改食譜」按鈕列
        btn_row = ttk.Frame(card, style="Card.TFrame")
        btn_row.pack(fill="x", pady=(8, 0))
        
        # 利用 lambda 把目前這張卡片的完整資料傳給視窗
        edit_btn = ttk.Button(btn_row, text="✏️ 修改食譜", style="Action.TButton",
                              command=lambda r=recipe: self.open_recipe_window(mode="edit", target_recipe=r))
        edit_btn.pack(side="right")

    def open_recipe_window(self, mode="add", target_recipe=None):
        """
        🌟 核心整合視窗：同時支援「新增食譜」與「修改食譜」
        - 食材輸入與做法皆全面升級為『多行文字框 (Text)』，支援一行一行輸入
        """
        dialog = tk.Toplevel(self)
        dialog.title("新增私房食譜" if mode == "add" else f"修改食譜 - {target_recipe['name']}")
        dialog.geometry("450x550")  # 微調高度以容納兩個多行輸入框
        dialog.configure(bg="#1E293B")
        dialog.transient(self)
        dialog.grab_set()

        lbl_style = {"bg": "#1E293B", "fg": "#F8FAFC", "font": ("微軟正黑體", 10, "bold")}
        
        # 1. 食譜名稱
        tk.Label(dialog, text="食譜名稱：", **lbl_style).pack(anchor="w", padx=25, pady=(15, 2))
        entry_name = tk.Entry(dialog, font=("微軟正黑體", 10), bg="#0F172A", fg="#F8FAFC", insertbackground="white")
        entry_name.pack(fill="x", padx=25)

        # 2. 所需食材 (升級為多行輸入，一行一個)
        tk.Label(dialog, text="所需食材 (🌟請一行輸入一個食材)：", **lbl_style).pack(anchor="w", padx=25, pady=(15, 2))
        text_ingredients = tk.Text(dialog, font=("微軟正黑體", 10), bg="#0F172A", fg="#F8FAFC", 
                                   insertbackground="white", height=5, wrap="w")
        text_ingredients.pack(fill="x", padx=25)
        tk.Label(dialog, text="例如：\n雞肉\n香菇\n醬油", bg="#1E293B", fg="#94A3B8", font=("微軟正黑體", 9), justify="left").pack(anchor="w", padx=25)

        # 3. 烹飪做法/步驟說明 (多行輸入)
        tk.Label(dialog, text="烹飪做法 / 步驟說明：", **lbl_style).pack(anchor="w", padx=25, pady=(15, 2))
        text_instructions = tk.Text(dialog, font=("微軟正黑體", 10), bg="#0F172A", fg="#F8FAFC", 
                                    insertbackground="white", height=5, wrap="w")
        text_instructions.pack(fill="x", padx=25)

        # 🌟 如果是「修改模式」，自動把舊資料填入格子裡
        if mode == "edit" and target_recipe:
            entry_name.insert(0, target_recipe["name"])
            
            # 將原本格式化成「雞肉、香菇、醬油」的字串，轉換回「一行一個」填入文字框
            raw_ing_lines = target_recipe["ingredients"].replace("、", "\n")
            text_ingredients.insert("1.0", raw_ing_lines)
            
            # 填入烹飪步驟
            text_instructions.insert("1.0", target_recipe.get("instructions", ""))

        def save_recipe_logic():
            name = entry_name.get().strip()
            # 讀取多行食材，並過濾掉空行
            raw_ing_text = text_ingredients.get("1.0", tk.END).strip()
            ing_list = [line.strip() for line in raw_ing_text.split("\n") if line.strip()]
            
            # 讀取多行做法
            instructions = text_instructions.get("1.0", tk.END).strip()

            if not name or not ing_list or not instructions:
                messagebox.showwarning("提示", "請填寫完整食譜欄位 (名稱、食材與做法)！", parent=dialog)
                return

            # 將陣列重新用「|」打包存入資料庫
            final_ingredients_str = "|".join(ing_list)

            if mode == "add":
                # 呼叫新增 API
                success = add_recipe_to_db(name, final_ingredients_str, instructions)
                msg_success, msg_fail = f"私房食譜「{name}」已成功儲存！", "儲存失敗，食譜名稱可能重複。"
            else:
                # 呼叫修改 API (傳入原本的菜名 target_recipe["name"] 作為修正依據)
                success = update_recipe_in_db(target_recipe["name"], name, final_ingredients_str, instructions)
                msg_success, msg_fail = f"食譜「{name}」已成功修改更新！", "修改失敗，可能有名稱重複或其他資料庫錯誤。"

            if success:
                messagebox.showinfo("成功", msg_success, parent=dialog)
                dialog.destroy()
                self.load_and_calculate_recipes()  # 立即重新整理雙欄主畫面
            else:
                messagebox.showerror("錯誤", msg_fail, parent=dialog)

        ttk.Button(dialog, text="💾 儲存食譜" if mode == "add" else "✨ 更新食譜內容", 
                   style="Action.TButton", command=save_recipe_logic).pack(pady=20)

    def on_export_shopping_list(self):
        """動態讀取畫面上最新勾選狀態並匯出採購清單"""
        if not self.computed_results:
            messagebox.showwarning("提示", "請先點選右上角『🔄 依最新庫存算食譜』生成清單！")
            return

        selected_recipes = [name for name, var in self.check_vars.items() if var.get() in (True, 1)]

        if not selected_recipes:
            messagebox.showwarning("提示", "您尚未勾選任何食譜！\n請先在想要烹飪的料理卡片左上角打勾。")
            return

        missing_set = set()
        for rcp in self.computed_results:
            if rcp["name"] in selected_recipes:
                if rcp["missing"] != "無":
                    for item in rcp["missing"].split("、"):
                        if item.strip():
                            missing_set.add(item.strip())

        if not missing_set:
            messagebox.showinfo("提示", "太棒了！您所勾選的料理目前冰箱食材皆非常充足，無須額外採買！")
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
            defaultextension=".csv", initialfile="客製化採購清單.csv",
            title="儲存採購清單", filetypes=[("CSV 檔案", "*.csv")]
        )
        if not filepath: 
            return

        result = export_shopping_list(shopping_data, filepath)
        
        if result.get("success") or (isinstance(result, dict) and result.get("success") == True):
            messagebox.showinfo("匯出成功", f"針對您選取的 {len(selected_recipes)} 道料理\n已成功彙整並導出共 {len(missing_set)} 項缺少食材！")
        else:
            msg = result.get("message") if isinstance(result, dict) else "導出失敗，請確認該 CSV 檔案未被其他程式開啟。"
            messagebox.showerror("匯出失敗", msg)