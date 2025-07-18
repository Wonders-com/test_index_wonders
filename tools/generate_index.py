import os
import json
from datetime import datetime

# 設定要掃描的知識庫目錄
KNOWLEDGE_DIR = "../knowledge"
OUTPUT_FILE = "../index.json"

index_list = []

# 遍歷 knowledge 目錄
for root, dirs, files in os.walk(KNOWLEDGE_DIR):
    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, start="..").replace("\\", "/")

            # 分類：knowledge/子資料夾名
            parts = relative_path.split("/")
            category = parts[1] if len(parts) >= 3 else "unknown"

            # 標題：檔名去掉副檔名
            title = os.path.splitext(file)[0]

            # 最後更新時間（用檔案修改時間）
            updated = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")

            index_list.append({
                "title": title,
                "file": relative_path,
                "category": category,
                "updated": updated
            })

# 寫入 index.json
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(index_list, f, ensure_ascii=False, indent=2)

print(f"✅ 已產生 {OUTPUT_FILE}，共 {len(index_list)} 筆知識文件")
