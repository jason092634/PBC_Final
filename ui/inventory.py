import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, date

# 引入資料庫操作與匯出 API
from db.database import get_all_ingredients, add_ingredient, delete_ingredient_by_name, update_ingredient_quantity # 🌟 補上 update_ingredient_quantity
from utils.exporter import export_inventory, export_shopping_list

class InventoryPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller 
        self._setup_treeview_style()
        self._build_ui()
        self.refresh_data() # 初始載入真實資料

    def _setup_treeview_style(self):
        """專屬這頁的深色表格樣式設定"""
        style = ttk.Style()
        style.configure("Treeview", background="#1E293B", fieldbackground="#1E293B", foreground="#F8FAFC", rowheight=28)
        style.map("Treeview", background=[("selected", "#10B981")])

    def _build_ui(self):
        # 標題區
        header = ttk.Frame(self, style="Main.TFrame")
        header.pack(fill="x", pady=(0, 20))
        ttk.Label(header, text="📦 冰箱食材管理庫存", style="Title.TLabel").pack(side="left")
        
        # 動作按鈕
        btn_frame = ttk.Frame(header, style="Main.TFrame")
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="📥 重新整理", style="Action.TButton", command=self.refresh_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📊 匯出完整庫存", style="Action.TButton", command=self.on_export_inventory).pack(side="left", padx=5)

        # 內容區 (左邊輸入表單，右邊表格)
        content = ttk.Frame(self, style="Main.TFrame")
        content.pack(fill="both", expand=True)

        # --- 左側：輸入表單 ---
        form = ttk.Frame(content, style="Card.TFrame", padding=20)
        form.pack(side="left", fill="y", padx=(0, 20))

        ttk.Label(form, text="新增/修改食材", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 15))

        ttk.Label(form, text="食材名稱:", style="CardText.TLabel").pack(anchor="w", pady=2)
        self.name_entry = ttk.Entry(form, font=("Arial", 11))
        self.name_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="數量:", style="CardText.TLabel").pack(anchor="w", pady=2)
        self.qty_entry = ttk.Entry(form, font=("Arial", 11))
        self.qty_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="有效日期 (YYYY-MM-DD):", style="CardText.TLabel").pack(anchor="w", pady=2)
        self.date_entry = ttk.Entry(form, font=("Arial", 11))
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d")) # 預填今天日期
        self.date_entry.pack(fill="x", pady=(0, 20))

        # 表單按鈕
        ttk.Button(form, text="➕ 儲存至冰箱", style="Action.TButton", command=self.on_save_ingredient).pack(fill="x", pady=5)
        ttk.Button(form, text="❌ 刪除所選食材", style="Action.TButton", command=self.on_delete_ingredient).pack(fill="x", pady=5)
        # 🌟 新增：「修改數量」按鈕 (放在刪除按鈕旁邊)
        ttk.Button(form, text="✏️ 修改所選數量", style="Action.TButton", command=self.on_edit_ingredient_quantity).pack(fill="x", pady=5)

        # --- 右側：表格顯示 ---
        table_frame = ttk.Frame(content, style="Main.TFrame")
        table_frame.pack(side="right", fill="both", expand=True)

        # --- 原始的表格欄位定義 ---
        self.tree = ttk.Treeview(table_frame, columns=("name", "qty", "unit", "p_date", "e_date", "status"), show="headings")
        
        # 設定各欄位名稱與寬度
        self.tree.heading("name", text="食材名稱")
        self.tree.heading("qty", text="數量")
        self.tree.heading("unit", text="單位")
        self.tree.heading("p_date", text="購買日期")
        
        # 🌟 關鍵修改：將有效日期的標題綁定排序函數
        # 預設為正序 (reverse=False)
        self.tree.heading("e_date", text="有效日期 ⇅", 
                             command=lambda: self.treeview_sort_column("e_date", False))
        
        self.tree.heading("status", text="狀態")
        self.tree.pack(fill="both", expand=True)

    def refresh_data(self):
        """從資料庫抓取最新食材並渲染表格"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.current_ingredients = get_all_ingredients() # 抓取真實資料
        status_mapping = {"ok": "新鮮", "soon": "7天內到期", "warning": "🔥3天內到期", "expired": "💀已過期"}

        for item in self.current_ingredients:
            self.tree.insert("", "end", values=(
                item["name"], item["quantity"], item["unit"], 
                item["purchase_date"], item["expiry_date"], 
                status_mapping.get(item["status"], "未知")
            ))

    def on_save_ingredient(self):
        """點擊儲存按鈕的商業邏輯與例外處理"""
        name = self.name_entry.get().strip()
        qty_str = self.qty_entry.get().strip()
        exp_date_str = self.date_entry.get().strip()

        # 1. 檢查空值
        if not name or not qty_str or not exp_date_str:
            messagebox.showerror("錯誤", "所有欄位皆為必填項目！")
            return

        # 2. 例外處理：數量防呆
        try:
            qty = float(qty_str)
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("格式錯誤", "數量必須是填入大於 0 的數字！")
            return

        # 3. 例外處理：日期格式防呆
        try:
            datetime.strptime(exp_date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("格式錯誤", "有效日期格式必須為 YYYY-MM-DD\n例如：2026-06-15")
            return

        # 4. 寫入資料庫
        today_str = date.today().strftime("%Y-%m-%d")
        success = add_ingredient(name, qty, today_str, exp_date_str)
        if success:
            messagebox.showinfo("成功", f"食材「{name}」已成功儲存！")
            self.refresh_data()
            # 清空輸入框
            self.name_entry.delete(0, tk.END)
            self.qty_entry.delete(0, tk.END)
        else:
            messagebox.showerror("錯誤", "儲存失敗，請檢查資料庫連線。")

    def on_delete_ingredient(self):
        """刪除所選食材"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "請先在右側表格點選要刪除的食材！")
            return
        
        item_values = self.tree.item(selected[0], "values")
        ing_name = item_values[0]

        if messagebox.askyesno("確認刪除", f"確定要將「{ing_name}」從冰箱移除嗎？"):
            delete_ingredient_by_name(ing_name)
            self.refresh_data()

    def on_edit_ingredient_quantity(self):
        """🌟 新增：處理點擊『修改數量』按鈕，彈出小視窗"""
        # 1. 檢查使用者是否有在 Treeview 表格中選取食材
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "請先在右側表格點選想要修改數量的食材！")
            return
        
        # 2. 撈出被選中食材的名稱與目前數量
        item_values = self.tree.item(selected[0], "values")
        ing_name = item_values[0]
        current_qty = item_values[1] # 原本的數量

        # 3. 彈出精美微型修改視窗
        dialog = tk.Toplevel(self)
        dialog.title(f"修改數量 - {ing_name}")
        dialog.geometry("320x200")
        dialog.configure(bg="#1E293B")
        dialog.transient(self)
        dialog.grab_set()

        lbl_style = {"bg": "#1E293B", "fg": "#F8FAFC", "font": ("微軟正黑體", 10, "bold")}
        
        tk.Label(dialog, text=f"食材：{ing_name}", font=("微軟正黑體", 12, "bold"), bg="#1E293B", fg="#10B981").pack(pady=(20, 5))
        tk.Label(dialog, text=f"目前庫存數量：{current_qty}", **lbl_style).pack(pady=2)
        tk.Label(dialog, text="請輸入新數量：", **lbl_style).pack(anchor="w", padx=45, pady=(10, 2))
        
        # 數量輸入框
        entry_qty = ttk.Entry(dialog, font=("微軟正黑體", 10))
        entry_qty.pack(fill="x", padx=45)
        entry_qty.insert(0, current_qty) # 預設帶入舊數量方便使用者微調
        entry_qty.focus()

        def save_quantity_logic():
            raw_qty = entry_qty.get().strip()
            
            # 驗證輸入格式是否為數字
            try:
                new_qty = float(raw_qty)
                if new_qty < 0:
                    messagebox.showwarning("格式錯誤", "數量不能為負數！", parent=dialog)
                    return
            except ValueError:
                messagebox.showerror("格式錯誤", "請輸入正確的數字格式 (例如: 2 或 1.5)！", parent=dialog)
                return

            # 如果輸入 0，親切提示要不要直接刪除
            if new_qty == 0:
                if messagebox.askyesno("提示", f"數量輸入為 0，是否直接將「{ing_name}」從冰箱移除？", parent=dialog):
                    from db.database import delete_ingredient_by_name
                    delete_ingredient_by_name(ing_name)
                    dialog.destroy()
                    self.refresh_data()
                    return
                else:
                    return

            # 呼叫後台資料庫更新 API
            if update_ingredient_quantity(ing_name, new_qty):
                messagebox.showinfo("成功", f"「{ing_name}」的數量已更新為 {new_qty}！", parent=dialog)
                dialog.destroy()
                self.refresh_data() # 刷新 Treeview 表格
            else:
                messagebox.showerror("錯誤", "更新失敗，請檢查資料庫連線。", parent=dialog)

        # 儲存按鈕
        ttk.Button(dialog, text="💾 確定修改", style="Action.TButton", command=save_quantity_logic).pack(pady=15)

    def on_export_inventory(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile="食材庫存.csv",
            title="儲存完整庫存清單", filetypes=[("CSV 檔案", "*.csv")]
        )
        if not filepath: return
        result = export_inventory(self.current_ingredients, filepath)
        if result["success"]: messagebox.showinfo("匯出成功", result["message"])
        else: messagebox.showerror("匯出失敗", result["message"])

    def treeview_sort_column(self, col, reverse):
        """點擊表格標題時進行排序的函數"""
        # 1. 撈出目前表格內所有資料的 ID 與它們對應的值
        data_list = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        # 2. 進行排序 (因為日期格式是 YYYY-MM-DD 字串，直接用字串排序即可完美對齊時間先後)
        data_list.sort(reverse=reverse)
        
        # 3. 根據排序後的順序，重新調整表格中項目的位置
        for index, (val, k) in enumerate(data_list):
            self.tree.move(k, "", index)
            
        # 4. 變更標題綁定的點擊事件，讓下一次點擊時可以反向排序 (正序 ⇄ 倒序)
        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))