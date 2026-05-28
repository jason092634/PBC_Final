#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox

# 引入你們自訂的模組（對應你們最終決定的資料夾與檔案名稱）
from db.database import initialize_db
from ui.window import MainWindow


def main():
    """專案的主程式進入點"""
    print("正在啟動智慧型冰箱食材與食譜管理系統...")

    # 1. 初始化資料庫
    try:
        # 呼叫你在 db/database.py 寫好的初始化函數（例如建立 SQLite 檔案與資料表）
        initialize_db()
        print("資料庫初始化成功。")
    except Exception as e:
        # 如果資料庫連線或建立失敗，跳出錯誤提示並中斷程式
        print(f"資料庫初始化失敗: {e}")
        # 建立一個臨時的隱藏視窗來彈出錯誤訊息
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "系統錯誤", f"無法初始化資料庫，程式即將關閉。\n錯誤訊息: {e}"
        )
        return

    # 2. 初始化 GUI 主視窗
    # 這裡建立 Tkinter 的 root 視窗
    root = tk.Tk()

    # 3. 設定主視窗的基本屬性（可以跟同學 B 討論調整）
    root.title("智慧型冰箱食材與食譜管理系統")
    root.geometry("1000x600")  # 設定預視窗大小
    root.minsize(800, 500)  # 設定最小視窗限制

    # 4. 實例化主畫面類別
    # 將 root 視窗傳進去，讓 ui/window.py 可以在裡面畫介面
    app = MainWindow(root)

    # 5. 啟動 Tkinter 事件監聽迴圈
    print("系統 GUI 啟動成功，進入主要迴圈。")
    root.mainloop()


if __name__ == "__main__":
    main()