"""
utils/exporter.py
負責將購物清單與食材庫存匯出成 CSV 檔案
"""

import csv
import os
from datetime import date, datetime
from typing import List


# ─────────────────────────────────────────
#  資料結構（對應 db/database.py 回傳的格式）
#  每筆食材預期為 dict，包含以下欄位：
#    name         : str   食材名稱
#    quantity     : float 數量
#    unit         : str   單位
#    purchase_date: date  購買日期
#    expiry_date  : date  有效日期
#    status       : str   狀態 ("ok" / "soon" / "warning" / "expired")
# ─────────────────────────────────────────

STATUS_LABELS = {
    "ok":      "新鮮",
    "soon":    "7天內到期",
    "warning": "3天內到期",
    "expired": "已過期",
}


def _format_date(d) -> str:
    """將 date / datetime / str 統一轉成 YYYY-MM-DD 字串"""
    if isinstance(d, (date, datetime)):
        return d.strftime("%Y-%m-%d")
    return str(d)


def _days_until_expiry(expiry_date) -> int:
    """計算距離到期還剩幾天（負數表示已過期）"""
    if isinstance(expiry_date, str):
        expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    return (expiry_date - date.today()).days


# ─────────────────────────────────────────
#  匯出購物清單
# ─────────────────────────────────────────

def export_shopping_list(ingredients: List[dict], output_path: str) -> dict:
    """
    將「需要補購」的食材匯出成 CSV。

    判斷標準：
      - 已過期（days < 0）  → 標記「需補貨」
      - 3 天內到期（days <= 3）→ 標記「即將用完」

    Parameters
    ----------
    ingredients : List[dict]
        從資料庫取出的所有食材清單
    output_path : str
        儲存路徑，例如 "output/購物清單.csv"

    Returns
    -------
    dict
        {"success": bool, "count": int, "path": str, "message": str}
    """
    try:
        # 篩選需要補購的食材
        shopping_items = []
        for ing in ingredients:
            days = _days_until_expiry(ing["expiry_date"])
            if days <= 3:
                if days < 0:
                    note = f"已過期 {abs(days)} 天，需補貨"
                elif days == 0:
                    note = "今天到期，建議補貨"
                else:
                    note = f"還剩 {days} 天，即將用完"
                shopping_items.append({
                    **ing,
                    "days_left": days,
                    "note": note,
                })

        # 確保輸出資料夾存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 寫入 CSV（utf-8-sig 讓 Excel 正確顯示中文）
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)

            # 標題列
            writer.writerow([
                "食材名稱",
                "目前數量",
                "單位",
                "有效日期",
                "剩餘天數",
                "建議採購數量",
                "備註",
            ])

            # 資料列
            for item in shopping_items:
                writer.writerow([
                    item["name"],
                    item["quantity"],
                    item["unit"],
                    _format_date(item["expiry_date"]),
                    item["days_left"] if item["days_left"] >= 0 else f"-{abs(item['days_left'])}",
                    "",          # 建議採購數量留空，讓使用者自填
                    item["note"],
                ])

        return {
            "success": True,
            "count": len(shopping_items),
            "path": output_path,
            "message": f"成功匯出 {len(shopping_items)} 筆採購建議至 {output_path}",
        }

    except PermissionError:
        return {
            "success": False,
            "count": 0,
            "path": output_path,
            "message": f"無法寫入檔案：{output_path}，請確認檔案未被開啟",
        }
    except Exception as e:
        return {
            "success": False,
            "count": 0,
            "path": output_path,
            "message": f"匯出失敗：{e}",
        }


# ─────────────────────────────────────────
#  匯出完整食材庫存
# ─────────────────────────────────────────

def export_inventory(ingredients: List[dict], output_path: str) -> dict:
    """
    將所有食材庫存匯出成 CSV（完整紀錄）。

    Parameters
    ----------
    ingredients : List[dict]
        從資料庫取出的所有食材清單
    output_path : str
        儲存路徑，例如 "output/食材庫存.csv"

    Returns
    -------
    dict
        {"success": bool, "count": int, "path": str, "message": str}
    """
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)

            writer.writerow([
                "食材名稱",
                "數量",
                "單位",
                "購買日期",
                "有效日期",
                "剩餘天數",
                "狀態",
            ])

            for ing in ingredients:
                days = _days_until_expiry(ing["expiry_date"])
                status_text = STATUS_LABELS.get(ing.get("status", "ok"), "")
                writer.writerow([
                    ing["name"],
                    ing["quantity"],
                    ing["unit"],
                    _format_date(ing["purchase_date"]),
                    _format_date(ing["expiry_date"]),
                    days if days >= 0 else f"-{abs(days)}",
                    status_text,
                ])

        return {
            "success": True,
            "count": len(ingredients),
            "path": output_path,
            "message": f"成功匯出 {len(ingredients)} 筆食材至 {output_path}",
        }

    except PermissionError:
        return {
            "success": False,
            "count": 0,
            "path": output_path,
            "message": f"無法寫入檔案：{output_path}，請確認檔案未被開啟",
        }
    except Exception as e:
        return {
            "success": False,
            "count": 0,
            "path": output_path,
            "message": f"匯出失敗：{e}",
        }