import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import date

# 呼叫組員 D 開發的 API 窗口
from utils.exporter import export_inventory, export_shopping_list

class InventoryPage(ttk.Frame):
    # 🌟 注意這裡：多了一個 controller 參數，代表外面的 MainWindow
    def __init__(self, parent, controller):
        # 套用主視窗設定好的深色背景樣式 "Main.TFrame"
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller 
        
        # 客製化 Treeview (表格) 的深色主題
        self._setup_treeview_style()
        
        # 建立 UI 版面
        self._build_ui()
        
        # 原本的假資料完全保留
        self.mock_ingredients = [
            {
                "name": "鮮奶", "quantity": 1, "unit": "瓶", 
                "purchase_date": date(2026, 5, 25), "expiry_date": date(2026, 6, 5), "status": "ok"
            },
            {
                "name": "高麗菜", "quantity": 0.5, "unit": "顆", 
                "purchase_date": date(2026, 5, 28), "expiry_date": date(2026, 5, 31), "status": "warning"
            },
            {
                "name": "過期吐司", "quantity": 3, "unit": "片", 
                "purchase_date": date(2026, 5, 10), "expiry_date": date(2026, 5, 20), "status": "expired"
            }
        ]
        
        self._load_data_to_treeview()

    def _setup_treeview_style(self):
        """專屬這頁的深色表格樣式設定"""
        style = ttk.Style()
        # 設定表格內容顏色 (深藍灰底、白字)
        style.configure("Treeview", 
                        background="#1E293B", foreground="#F8FAFC", 
                        fieldbackground="#1E293B", borderwidth=0, rowheight=30)
        # 設定表格標題顏色 (更深的底、科技綠字)
        style.configure("Treeview.Heading", 
                        background="#0F172A", foreground="#10B981", 
                        font=("微軟正黑體", 11, "bold"))
        # 隱藏表格被選取時的刺眼藍色，改用低調灰色
        style.map("Treeview", background=[("selected", "#334155")])

    def _build_ui(self):
        """建構頁面上的所有元件"""
        # --- 標題區 ---
        ttk.Label(self, text="📦 食材庫存清單", style="Title.TLabel").pack(anchor="w", padx=20, pady=(20, 10))

        # --- 上方：操作按鈕區 ---
        btn_frame = ttk.Frame(self, style="Main.TFrame")
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        export_inv_btn = ttk.Button(btn_frame, text="📥 匯出完整庫存", style="Action.TButton", command=self.on_export_inventory)
        export_inv_btn.pack(side="left", padx=(0, 10))

        export_shop_btn = ttk.Button(btn_frame, text="🛒 匯出採購清單", style="Warning.TButton", command=self.on_export_shopping)
        export_shop_btn.pack(side="left")

        # --- 中央：食材顯示表格 (Treeview) ---
        table_frame = ttk.Frame(self, style="Card.TFrame", padding=2)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("name", "quantity", "unit", "purchase", "expiry", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("name", text="食材名稱")
        self.tree.heading("quantity", text="數量")
        self.tree.heading("unit", text="單位")
        self.tree.heading("purchase", text="購買日期")
        self.tree.heading("expiry", text="有效日期")
        self.tree.heading("status", text="狀態")
        
        for col in columns:
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # --- 🌟 底部：場景連動專屬區塊 ---
        action_frame = ttk.Frame(self, style="Main.TFrame")
        action_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Label(action_frame, text="食材太多不知道怎麼煮？", style="CardText.TLabel", foreground="#F8FAFC").pack(side="left")
        
        # 呼叫 controller (MainWindow) 的 show_frame 方法，跳轉至食譜頁面
        jump_btn = ttk.Button(action_frame, text="🍳 根據目前庫存生成食譜 ➔", style="Action.TButton",
                              command=lambda: self.controller.show_frame("Recipe"))
        jump_btn.pack(side="right")

    def _load_data_to_treeview(self):
        """將資料渲染到畫面上的表格 (邏輯不變)"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.mock_ingredients:
            self.tree.insert("", "end", values=(
                item["name"], item["quantity"], item["unit"], 
                item["purchase_date"].strftime("%Y-%m-%d"), 
                item["expiry_date"].strftime("%Y-%m-%d"), 
                item["status"]
            ))

    # ==========================================
    # API 匯出邏輯 (完全保留，無需更動)
    # ==========================================
    def on_export_inventory(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile="食材庫存.csv",
            title="儲存完整庫存清單", filetypes=[("CSV 檔案", "*.csv")]
        )
        if not filepath: return
        result = export_inventory(self.mock_ingredients, filepath)
        if result["success"]: messagebox.showinfo("匯出成功", result["message"])
        else: messagebox.showerror("匯出失敗", result["message"])

    def on_export_shopping(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile="採購清單.csv",
            title="儲存採購清單", filetypes=[("CSV 檔案", "*.csv")]
        )
        if not filepath: return
        result = export_shopping_list(self.mock_ingredients, filepath)
        if result["success"]: messagebox.showinfo("匯出成功", result["message"])
        else: messagebox.showerror("匯出失敗", result["message"])