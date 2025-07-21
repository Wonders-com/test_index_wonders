import os
import json
from datetime import datetime
import urllib.parse

# 設定路徑
KNOWLEDGE_DIR = "knowledge"              # 放 .md 的資料夾
OUTPUT_FILE = "index.json"               # 產出的索引檔
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Wonders-com/test_index_wonders/main"

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

            # 標題優先用第一行 markdown 標題，否則用檔名
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip().lstrip("#").strip()
                    title = first_line if first_line else os.path.splitext(file)[0]
            except:
                title = os.path.splitext(file)[0]

            # 建立 raw URL 連結
            raw_url = f"{GITHUB_RAW_BASE}/{urllib.parse.quote(relative_path)}"

            # 最後更新時間
            updated = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")

            index_list.append({
                "title": title,
                "file": relative_path,
                "url": raw_url,
                "category": category,
                "updated": updated
            })

# 儲存為 index.json
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(index_list, f, ensure_ascii=False, indent=2)

print(f"✅ 已成功產出 {OUTPUT_FILE}，共 {len(index_list)} 筆")
