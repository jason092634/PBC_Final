# ui/window.py
import tkinter as tk
from tkinter import ttk


class MainWindow:

    def __init__(self, root):
        """主視窗建構子。

        (這裡之後由同學 B 來實作主畫面、分頁切換等細節)
        """
        self.root = root

        # 先塞一個簡單的標籤，證明介面有成功串上
        self.label = ttk.Label(
            root,
            text="智慧冰箱管理系統 - 開發中骨架",
            font=("Arial", 16),
        )
        self.label.pack(pady=50)

        print("[UI] 執行 window.py 中的 MainWindow 初始化...")