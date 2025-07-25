import os
import json
from datetime import datetime
import urllib.parse

# 設定路徑
KNOWLEDGE_DIR = "knowledge_chunks/law_CK"              # 放 .md 的資料夾
OUTPUT_FILE = "index.json"               # 產出的索引檔
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Wonders-com/test_index_wonders/main"


# 這是關鍵的維護點，當有新產品資料夾時，需要更新這裡
PRODUCT_FOLDER_TO_NAME_MAP = {
    "product_weider_probiotic": "威德益生菌",
    "product_cranberry_probiotic": "威德蔓越莓益生菌",
    "product_other_unmatch":"無法識別產品",
    # 範例：如果未來有新產品
    # "product_xyz_vitamin": "XYZ綜合維他命",
    
}

index_list = []

# 遍歷資料夾
for root, dirs, files in os.walk(KNOWLEDGE_DIR):
    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, start=".").replace("\\", "/")

            # 分類，例如 knowledge/law/xxx.md → law
            parts = relative_path.split("/")
            category = "unknown"

            product_name = "未知產品" # 預設值

            # 根據路徑深度和命名慣例來判斷 category 和 product_name
            if len(parts) >= 2: # 至少 knowledge/something
                if parts[1] == "product" and len(parts) >= 3: # knowledge/product/product_xxx
                    category = parts[2] # 新的 category 是 product_xxx_productname
                    # 從映射中查找對應的中文產品名稱
                    product_name = PRODUCT_FOLDER_TO_NAME_MAP.get(category, "未知產品")
                elif parts[1] == "law_CK": # 如果 category 是 "law"
                    category = parts[1] # 設定 category 為 law
                    product_name = "法規" # productName 顯示為 "法規"
                elif parts[1] != "product": # knowledge/law 或者其他頂層分類
                    category = parts[1] # 保持原來的 category 提取方式
                    # 非產品類別的 product_name 可以保持預設或設定為 None

            # 標題優先用第一行 markdown 標題，否則用檔名
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip().lstrip("#").strip()
                    title = first_line if first_line else os.path.splitext(file)[0]
            except Exception: # 捕獲所有異常，避免文件讀取問題導致腳本停止
                title = os.path.splitext(file)[0]

            raw_url = f"{GITHUB_RAW_BASE}/{urllib.parse.quote(relative_path)}"

            # 最後更新時間
            updated = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")

            index_list.append({
                "title": title,
                "file": relative_path,
                "url": raw_url,
                "category": category,
                "product_name": product_name,
                "updated": updated
            })

# 儲存為 index.json
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(index_list, f, ensure_ascii=False, indent=2)

print(f"✅ 已成功產出 {OUTPUT_FILE}，共 {len(index_list)} 筆")