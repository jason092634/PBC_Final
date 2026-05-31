import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, date

# 引入資料庫操作與匯出 API
from db.database import get_all_ingredients, add_ingredient, delete_ingredient_by_name
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

        # --- 右側：表格顯示 ---
        table_frame = ttk.Frame(content, style="Main.TFrame")
        table_frame.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("name", "qty", "unit", "p_date", "e_date", "status"), show="headings")
        self.tree.heading("name", text="食材名稱")
        self.tree.heading("qty", text="數量")
        self.tree.heading("unit", text="單位")
        self.tree.heading("p_date", text="購買日期")
        self.tree.heading("e_date", text="有效日期")
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

    def on_export_inventory(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile="食材庫存.csv",
            title="儲存完整庫存清單", filetypes=[("CSV 檔案", "*.csv")]
        )
        if not filepath: return
        result = export_inventory(self.current_ingredients, filepath)
        if result["success"]: messagebox.showinfo("匯出成功", result["message"])
        else: messagebox.showerror("匯出失敗", result["message"])