import os
import json
from datetime import datetime
import urllib.parse

# 設定路徑
KNOWLEDGE_DIR = "knowledge"              # 放 .md 的資料夾
OUTPUT_FILE = "index.json"               # 產出的索引檔
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Wonders-com/test_index_wonders/main"


# 這是關鍵的維護點，當有新產品資料夾時，需要更新這裡
PRODUCT_FOLDER_TO_NAME_MAP = {
    "product_weider_probiotic": "威德益生菌",
    "product_cranberry_probiotic": "威德蔓越莓益生菌",
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
            category = parts[1] if len(parts) >= 3 else "unknown"

            product_name = "未知產品" # 預設值

            # 根據資料夾名稱來推斷產品名稱
            # 這裡假設你的產品知識文件都放在 knowledge/product_xxx_productname/ 下
            if category.startswith("product_"):
                # 從映射中查找對應的中文產品名稱
                product_name = PRODUCT_FOLDER_TO_NAME_MAP.get(category, "未知產品")

            # 標題優先用第一行 markdown 標題，否則用檔名
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip().lstrip("#").strip()
                    title = first_line if first_line else os.path.splitext(file)[0]
            except Exception: # 捕獲所有異常，避免文件讀取問題導致腳本停止
                title = os.path.splitext(file)[0]

            # 建立 raw URL 連結
            # 注意：這裡使用了 urllib.parse.quote 對路徑進行 URL 編碼，確保特殊字元處理正確
            raw_url = f"{GITHUB_RAW_BASE}/{urllib.parse.quote(relative_path)}"

            # 最後更新時間
            updated = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")

            index_list.append({
                "title": title,
                "file": relative_path,
                "url": raw_url,
                "category": category,
                "product_name": product_name, # <-- 新增的產品名稱欄位
                "updated": updated
            })

# 儲存為 index.json
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(index_list, f, ensure_ascii=False, indent=2)

print(f"✅ 已成功產出 {OUTPUT_FILE}，共 {len(index_list)} 筆")