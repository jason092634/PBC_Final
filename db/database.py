#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import sqlite3

# 定義資料庫檔案路徑（會生成在專案根目錄下）
DB_PATH = "fridge.db"


def get_connection():
    """建立並回傳資料庫連線物件（供外部功能呼叫）"""
    conn = sqlite3.connect(DB_PATH)
    # 讓查詢結果可以用類似字典 (Dict) 的方式存取，方便 UI 拿欄位名稱
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """初始化 SQLite 資料庫：建立資料表，並在初次啟動時自動匯入假資料。"""
    conn = get_connection()
    cursor = conn.cursor()

    print("[DB] 正在檢查並建立資料表...")

    # 1. 建立冰箱食材管理表 (ingredients)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,  -- 修正這裡：設定為必填且不能重複
            quantity INTEGER NOT NULL,
            purchase_date TEXT NOT NULL,
            expiry_date TEXT NOT NULL
        )
    """)

    # 2. 建立智慧食譜表 (recipes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            required_ingredients TEXT NOT NULL, -- 格式範例: "雞肉|雞蛋|洋蔥"
            instructions TEXT
        )
    """)

    conn.commit()
    print("[DB] 資料表結構檢查完成。")

    # 3. 自動匯入測試假資料（由組員 D 提供的 CSV）
    _import_mock_data(conn)

    conn.close()


def _import_mock_data(conn):
    """內部函數：檢查若資料庫為空，則自動從 data/ 匯入假資料"""
    cursor = conn.cursor()

    # --- 匯入食材假資料 ---
    cursor.execute("SELECT COUNT(*) FROM ingredients")
    if cursor.fetchone()[0] == 0:
        mock_ing_path = os.path.join("data", "mock_ingredients.csv")
        if os.path.exists(mock_ing_path):
            try:
                with open(mock_ing_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader)  # 跳過標頭行
                    for row in reader:
                        if row:  # 確保不是空行
                            cursor.execute(
                                """
                                INSERT INTO ingredients (name, quantity, purchase_date, expiry_date)
                                VALUES (?, ?, ?, ?)
                            """,
                                row,
                            )
                conn.commit()
                print("[DB] 成功自 mock_ingredients.csv 匯入初始食材資料！")
            except Exception as e:
                print(f"[DB] 匯入食材假資料失敗: {e}")

    # --- 匯入食譜假資料 ---
    cursor.execute("SELECT COUNT(*) FROM recipes")
    if cursor.fetchone()[0] == 0:
        mock_rcp_path = os.path.join("data", "mock_recipes.csv")
        if os.path.exists(mock_rcp_path):
            try:
                with open(mock_rcp_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader)  # 跳過標頭行
                    for row in reader:
                        if row:
                            cursor.execute(
                                """
                                INSERT INTO recipes (title, required_ingredients, instructions)
                                VALUES (?, ?, ?)
                            """,
                                row,
                            )
                conn.commit()
                print("[DB] 成功自 mock_recipes.csv 匯入初始食譜資料！")
            except Exception as e:
                print(f"[DB] 匯入食譜假資料失敗: {e}")

# ==========================================
# 基礎食材管理 CRUD 函數 (供 UI 呼叫)
# ==========================================


def add_ingredient(name, quantity, purchase_date, expiry_date):
    """新增食材"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO ingredients (name, quantity, purchase_date, expiry_date)
            VALUES (?, ?, ?, ?)
        """,
            (name, quantity, purchase_date, expiry_date),
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"新增食材失敗: {e}")
        return False
    finally:
        conn.close()


def get_all_ingredients():
    """查詢所有食材（傳回 list，每筆食材可用 dict 方式存取）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, quantity, purchase_date, expiry_date FROM ingredients"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_ingredient(ingredient_id):
    """根據 ID 刪除食材"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))
    conn.commit()
    conn.close()


def update_ingredient_quantity(ingredient_id, new_quantity):
    """修改食材數量"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE ingredients SET quantity = ? WHERE id = ?",
        (new_quantity, ingredient_id),
    )
    conn.commit()
    conn.close()