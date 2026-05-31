import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import date

from db.database import get_all_ingredients, get_all_recipes, add_recipe_to_db, delete_recipe_by_name
from utils.recommender import recommend_recipes
from utils.exporter import export_shopping_list

class RecipePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
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

        # 🌟 補回遺失的管理按鈕
        ttk.Button(header_frame, text="📖 管理食譜庫", style="Action.TButton", 
                   command=self.open_manage_recipe_window).pack(side="right", padx=5)

        # 捲動顯示區 (食譜卡片容器)
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

        # 底部跳轉與匯出區
        action_frame = ttk.Frame(self, style="Main.TFrame", padding=(0, 20, 0, 0))
        action_frame.pack(fill="x", side="bottom")

        ttk.Button(action_frame, text="📝 匯出缺少食材(採購清單)", style="Action.TButton",
                   command=self.on_export_shopping_list).pack(side="left")
        
        ttk.Button(action_frame, text="🛒 前往庫存管理 ➔", style="Action.TButton",
                   command=lambda: self.controller.show_frame("Inventory")).pack(side="right")

    def load_and_calculate_recipes(self):
        """重新載入資料並計算推薦食譜"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        fridge_ingredients = get_all_ingredients()
        all_recipes = get_all_recipes()

        self.computed_results = recommend_recipes(fridge_ingredients, all_recipes)

        if not self.computed_results:
            ttk.Label(self.scrollable_frame, text="目前無食譜資料，請點擊「新增私房食譜」建立。", 
                      style="CardText.TLabel").pack(pady=20)
            return

        for rcp in self.computed_results:
            self._create_recipe_card(rcp)

    def _create_recipe_card(self, recipe):
        """渲染單筆食譜卡片"""
        card = ttk.Frame(self.scrollable_frame, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=10, padx=5)
        
        title_row = ttk.Frame(card, style="Card.TFrame")
        title_row.pack(fill="x")
        
        ttk.Label(title_row, text=recipe["name"], style="CardTitle.TLabel").pack(side="left")
        
        match_color = "#10B981" if recipe["match_rate"] >= 70 else "#F43F5E"
        match_label = tk.Label(title_row, text=f"{recipe['match_rate']}% 匹配", 
                              bg=match_color, fg="white", font=("Arial", 10, "bold"), padx=10)
        match_label.pack(side="right")
        
        info_text = f"所需食材：{recipe['ingredients']}\n目前缺少：{recipe['missing']}"
        ttk.Label(card, text=info_text, style="CardText.TLabel").pack(anchor="w", pady=(10, 5))
        ttk.Label(card, text=f"💡 烹飪提示：{recipe['status']}", style="CardText.TLabel", foreground="#94A3B8").pack(anchor="w")

# ==========================================
    # 彈出視窗：管理與刪除食譜 (修復按鈕消失版)
    # ==========================================
    def open_manage_recipe_window(self):
        mgr_window = tk.Toplevel(self)
        mgr_window.title("管理食譜庫")
        mgr_window.geometry("550x450")  # 💡 修正 1：把視窗拉高一點
        mgr_window.configure(bg="#0F172A")
        
        mgr_window.transient(self.winfo_toplevel())
        mgr_window.grab_set()

        ttk.Label(mgr_window, text="📖 現有食譜列表", style="CardTitle.TLabel").pack(pady=(20, 10), padx=20, anchor="w")

        # 💡 修正 2：先建立一個專屬的「底部區塊」並釘死在最下面 (side="bottom")
        bottom_frame = ttk.Frame(mgr_window, style="Main.TFrame")
        bottom_frame.pack(side="bottom", fill="x", pady=15)

        # 💡 修正 3：然後再放入表格，這樣表格再怎麼長大，都不會蓋掉底部區塊
        table_frame = ttk.Frame(mgr_window, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        columns = ("title", "ingredients")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        tree.heading("title", text="食譜名稱")
        tree.heading("ingredients", text="所需食材")
        tree.column("title", width=150, anchor="w")
        tree.column("ingredients", width=300, anchor="w")
        tree.pack(fill="both", expand=True)

        def refresh_table():
            for row in tree.get_children():
                tree.delete(row)
            for rcp in get_all_recipes():
                tree.insert("", "end", values=(rcp["title"], rcp["required_ingredients"]))

        refresh_table()

        def delete_selected():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("提示", "請先選取要刪除的食譜", parent=mgr_window)
                return
            
            recipe_title = tree.item(selected_item[0])["values"][0]
            confirm = messagebox.askyesno("確認刪除", f"確定要刪除食譜「{recipe_title}」嗎？", parent=mgr_window)
            
            if confirm:
                success = delete_recipe_by_name(recipe_title)
                if success:
                    refresh_table()
                    self.load_and_calculate_recipes()
                    messagebox.showinfo("成功", "食譜已刪除", parent=mgr_window)
                else:
                    messagebox.showerror("錯誤", "刪除失敗", parent=mgr_window)

        # 把刪除按鈕放進剛剛釘死的底部區塊裡
        ttk.Button(bottom_frame, text="❌ 刪除選取的食譜", style="Warning.TButton", 
                   command=delete_selected).pack()

    # ==========================================
    # 彈出視窗：新增私房食譜
    # ==========================================
    def open_add_recipe_window(self):
        add_window = tk.Toplevel(self)
        add_window.title("新增私房食譜")
        add_window.geometry("450x500") 
        add_window.configure(bg="#0F172A")
        
        add_window.transient(self.winfo_toplevel())
        add_window.grab_set()

        ttk.Label(add_window, text="食譜名稱：", style="CardText.TLabel").pack(pady=(20, 5), padx=20, anchor="w")
        name_entry = ttk.Entry(add_window, font=("微軟正黑體", 12))
        name_entry.pack(fill="x", padx=20)

        ttk.Label(add_window, text="所需食材 (只需填寫名稱)：", style="CardText.TLabel").pack(pady=(20, 5), padx=20, anchor="w")
        
        ingredients_container = ttk.Frame(add_window, style="Main.TFrame")
        ingredients_container.pack(fill="both", expand=True, padx=20)
        
        row_entries = []

        def add_ingredient_row():
            row_frame = ttk.Frame(ingredients_container, style="Main.TFrame")
            row_frame.pack(fill="x", pady=5)

            n_ent = ttk.Entry(row_frame, width=25, font=("微軟正黑體", 11))
            n_ent.pack(side="left", padx=(0, 10))

            def remove_row():
                row_frame.destroy()
                row_entries.remove(n_ent)

            ttk.Button(row_frame, text="❌", width=3, command=remove_row).pack(side="left")
            row_entries.append(n_ent)

        for _ in range(3):
            add_ingredient_row()

        ttk.Button(add_window, text="➕ 新增一項食材", command=add_ingredient_row).pack(pady=10)

        def save_new_recipe():
            recipe_name = name_entry.get().strip()
            
            collected_names = [n_ent.get().strip() for n_ent in row_entries if n_ent.get().strip()]
            ingredients_str = "|".join(collected_names)

            if not recipe_name or not ingredients_str:
                messagebox.showwarning("格式錯誤", "食譜名稱與至少一項食材都不能為空！", parent=add_window)
                return

            try:
                success = add_recipe_to_db(recipe_name, ingredients_str)
                if success:
                    messagebox.showinfo("成功", f"食譜「{recipe_name}」已新增", parent=add_window)
                    add_window.destroy()
                    self.load_and_calculate_recipes()
                else:
                    messagebox.showwarning("名稱重複", f"食譜「{recipe_name}」已存在。", parent=add_window)
            except Exception as e:
                messagebox.showerror("錯誤", f"儲存失敗：{e}", parent=add_window)

        ttk.Button(add_window, text="💾 儲存並寫入資料庫", style="Action.TButton", command=save_new_recipe).pack(pady=15)

    # ==========================================
    # 匯出缺少食材功能
    # ==========================================
    def on_export_shopping_list(self):
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
        if not filepath: return

        result = export_shopping_list(shopping_data, filepath)
        
        if result.get("success") or (isinstance(result, dict) and result.get("success") == True): 
            messagebox.showinfo("匯出成功", result.get("message", "已成功導出採購清單"))
        else: 
            msg = result.get("message") if isinstance(result, dict) else "導出失敗"
            messagebox.showerror("匯出失敗", msg)