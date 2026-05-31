#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import sqlite3
from datetime import datetime, date

# 定義資料庫檔案路徑（會生成在專案根目錄下）
DB_PATH = "fridge.db"

def get_connection():
    """建立並回傳資料庫連線物件（供外部功能呼叫）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # 這行能讓我們用 item["name"] 方式拿資料
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
            name TEXT NOT NULL UNIQUE,
            quantity REAL NOT NULL, -- 改成 REAL 以支援 0.5 顆這種數量
            purchase_date TEXT NOT NULL,
            expiry_date TEXT NOT NULL
        )
    """)

    # 2. 建立智慧食譜表 (recipes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            required_ingredients TEXT NOT NULL,
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
    # 匯入食材
    cursor.execute("SELECT COUNT(*) FROM ingredients")
    if cursor.fetchone()[0] == 0:
        mock_ing_path = os.path.join("data", "mock_ingredients.csv")
        if os.path.exists(mock_ing_path):
            with open(mock_ing_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if row:
                        cursor.execute("INSERT INTO ingredients (name, quantity, purchase_date, expiry_date) VALUES (?, ?, ?, ?)", row)
            conn.commit()
            print("[DB] 成功自 mock_ingredients.csv 匯入初始食材資料！")

    # 匯入食譜
    cursor.execute("SELECT COUNT(*) FROM recipes")
    if cursor.fetchone()[0] == 0:
        mock_rcp_path = os.path.join("data", "mock_recipes.csv")
        if os.path.exists(mock_rcp_path):
            with open(mock_rcp_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if row:
                        cursor.execute("INSERT INTO recipes (title, required_ingredients, instructions) VALUES (?, ?, ?)", row)
            conn.commit()
            print("[DB] 成功自 mock_recipes.csv 匯入初始食譜資料！")

# ==========================================
# 基礎食材管理 CRUD 與擴充函數
# ==========================================

def get_all_ingredients():
    """查詢所有食材，並自動計算 status 天數狀態傳回"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, purchase_date, expiry_date FROM ingredients")
    rows = cursor.fetchall()
    conn.close()

    results = []
    today = date.today()
    for row in rows:
        item = dict(row)
        # 動態計算過期狀態
        try:
            exp_date = datetime.strptime(item["expiry_date"], "%Y-%m-%d").date()
            days_left = (exp_date - today).days
            if days_left < 0:
                item["status"] = "expired"
            elif days_left <= 3:
                item["status"] = "warning"
            elif days_left <= 7:
                item["status"] = "soon"
            else:
                item["status"] = "ok"
        except Exception:
            item["status"] = "ok"
        
        # 為了相容組員設計的 UI，統一加上單位預設值
        item["unit"] = "個/瓶"
        results.append(item)
    return results

def get_all_recipes():
    """查詢所有食譜 (供推薦模組使用)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, required_ingredients, instructions FROM recipes")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_ingredient(name, quantity, purchase_date, expiry_date):
    """新增食材"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 使用 INSERT OR REPLACE，若食材名字重複就直接蓋過數量與日期
        cursor.execute("""
            INSERT OR REPLACE INTO ingredients (name, quantity, purchase_date, expiry_date)
            VALUES (?, ?, ?, ?)
        """, (name, quantity, purchase_date, expiry_date))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"新增/更新食材失敗: {e}")
        return False
    finally:
        conn.close()

def delete_ingredient_by_name(name):
    """改用名稱刪除，比較符合現有 UI 的操作"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ingredients WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def add_recipe_to_db(name, ingredients_str, instructions):
    """
    新增私房食譜 (已升級：支援自訂烹飪做法)
    - name: 食譜名稱 (例如: '番茄炒蛋')
    - ingredients_str: 所需食材字串 (例如: '番茄|雞蛋|蔥')
    - instructions: 使用者輸入的做法步驟
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 🌟 將寫死的文字替換為變數值 ?
        cursor.execute("""
            INSERT INTO recipes (title, required_ingredients, instructions)
            VALUES (?, ?, ?)
        """, (name, ingredients_str, instructions))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"[DB 警告] 食譜名稱「{name}」已存在，拒絕重複新增。")
        return False
    except sqlite3.Error as e:
        print(f"[DB 錯誤] 新增食譜失敗: {e}")
        return False
    finally:
        conn.close()

def update_recipe_in_db(old_title, new_title, ingredients_str, instructions):
    """
    🌟 新增：修改/更新現有食譜
    - old_title: 原本的食譜名稱 (用來當 WHERE 條件)
    - new_title: 新的食譜名稱
    - ingredients_str: 修改後的食材字串 (例如 '雞肉|香菇')
    - instructions: 修改後的做法步驟
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE recipes 
            SET title = ?, required_ingredients = ?, instructions = ?
            WHERE title = ?
        """, (new_title, ingredients_str, instructions, old_title))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB 錯誤] 更新食譜失敗: {e}")
        return False
    finally:
        conn.close()

def delete_recipe_by_name(title):
    """刪除指定名稱的食譜 (供 UI 呼叫)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM recipes WHERE title = ?", (title,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB 錯誤] 刪除食譜失敗: {e}")
        return False
    finally:
        conn.close()