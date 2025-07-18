## 開發者筆記 ##

這是一個結合 cloudflare(D1), gemini, github page 來實現的互動機器人。  


knowledge/ 用以放入pdf轉換後的 .md 檔案，目前pfd要自行上網下載並轉譯成md  

index.json :使用 generate_index.py 產生的知識索引，每次更新knowledge後跑一次  

generate_index.py :用以更新 index.json  

tools/generate_index.py :自動產生索引的 Python 腳本
