import os
import re
import json

# 配置路徑
# 假設此腳本位於 tools/chunk_md.py
# 原始 Markdown 檔案的根目錄
SOURCE_MD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'knowledge', 'law')
# 切割後的 chunks 存儲的目錄
# 建議存儲到一個新的目錄，例如 knowledge_chunks
OUTPUT_CHUNKS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'knowledge_chunks', 'law_CK')

def chunk_markdown_by_headings(filepath):
    """
    優化後的 Markdown 文件切割函數。
    它會識別所有級別的標題，但主要以 ## (H2) 或更低級別的標題進行分塊。
    H1 標題會被提取作為文件的元數據，不會重複添加到每個子塊中。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
    except FileNotFoundError:
            print(f"錯誤：檔案未找到 - {filepath}")
            return []

    chunks = []
    file_title = "" # 用來存儲 H1 標題

    # 嘗試提取第一個 H1 標題作為文件總標題
    h1_match = re.match(r'^(#\s*.*)\n([\s\S]*)', content)
    if h1_match:
        file_title = h1_match.group(1).strip() # 獲取 H1 標題
        content = h1_match.group(2).strip() # 剩餘內容 (去掉 H1 標題)
        # 如果文件只有 H1 標題沒有其他內容，或者 H1 標題後只有空白，則將 H1 標題本身作為一個 chunk
        if not content.strip():
            chunks.append(file_title)
            return chunks
    elif content.strip().startswith('# '): # 如果沒有匹配到 H1 且內容以 H1 開頭，說明只有 H1 標題
        file_title = content.strip().split('\n')[0].strip()
        content = '\n'.join(content.strip().split('\n')[1:])
        if not content.strip(): # 僅有H1時
            chunks.append(file_title)
            return chunks


    # 使用正則表達式分割內容。
    # (?m) 讓 ^ 匹配每行的開頭。
    # (^##+\s.*) 匹配以 ## 或 ### 等開頭的標題行，作為分割點。
    # 使用 re.split()，匹配到的分隔符 (標題本身) 也會被包含在結果列表中。
    # 例如：['前言內容', '## 標題1', '內容1', '## 標題2', '內容2']
    sections = re.split(r'(?m)(^##+\s.*)', content)

    # 處理分割結果
    current_chunk_content = ""
    # 如果 sections 第一個元素不是標題，則它是前言部分或 H1 之後的內容
    if sections and not sections[0].strip().startswith('##'):
        current_chunk_content = sections[0].strip()
        # 如果有文件總標題，將其添加到第一個 chunk 的開頭
        if file_title:
            current_chunk_content = file_title + '\n\n' + current_chunk_content

        if current_chunk_content.strip(): # 確保不添加空 chunk
            chunks.append(current_chunk_content.strip())
        sections = sections[1:] # 移除已處理的前言部分

    # 迭代處理剩餘的部分
    for i in range(0, len(sections), 2):
        if i + 1 < len(sections):
            heading = sections[i].strip() # 這是分割出來的標題
            section_body = sections[i+1].strip() # 這是標題後的內容
                
            # 將當前標題和其內容組合成一個 chunk
            chunk_content = heading
            if section_body:
                chunk_content += '\n' + section_body
                
            # 如果有文件總標題，可以在這裡選擇性地加到每個子 chunk 的開頭
            # 依據您想在每個分塊中重複多少上下文決定。
            # 通常對於子分塊，重複文件總標題不是必須的，因為它會導致冗餘。
            # 如果您希望每個 chunk 都能獨立理解，可以這樣做：
            # if file_title:
            # chunk_content = file_title + '\n\n' + chunk_content
                
            if chunk_content.strip():
                chunks.append(chunk_content.strip())
        elif sections[i].strip(): # 如果是奇數個元素，表示最後一個元素是未處理的內容
            # 這通常不應該發生，除非正則表達式或內容格式有異常
            if file_title and not sections[i].strip().startswith('# '): # 如果是 H1 之後的剩餘內容
                chunks.append(file_title + '\n\n' + sections[i].strip())
            else:
                chunks.append(sections[i].strip())


    # 如果整個文件沒有找到任何 ## 標題，但有內容，則將整個內容作為一個 chunk
    # 如果有 H1 標題，將 H1 標題也包含進去
    if not chunks and content.strip():
        final_chunk_content = ""
        if file_title:
            final_chunk_content += file_title + '\n\n'
        final_chunk_content += content.strip()
        if final_chunk_content.strip():
            chunks.append(final_chunk_content.strip())

    return chunks


#單一處理指定md檔
def process_single_markdown_file(filepath):
    """
    處理單一 Markdown 檔案，對其進行分塊處理，
    並將切割後的 chunks 保存到指定的輸出目錄。
    """
    if not os.path.exists(filepath):
        print(f"錯誤：指定的檔案不存在 - {filepath}")
        return

    print(f"正在處理單一檔案: {filepath}")
    chunks = chunk_markdown_by_headings(filepath)

    if not chunks:
        print(f"警告：檔案 {filepath} 沒有產生任何分塊。可能沒有找到標題或內容為空。")
        return

    # 確定相對於 SOURCE_MD_DIR 的相對路徑，以在輸出目錄中重建相似的結構
    # 如果 filepath 不在 SOURCE_MD_DIR 之下，這個相對路徑會包含 '../' 或其他非預期的部分
    # 我們需要更穩健的方式來處理單一檔案的輸出路徑
    
    # 獲取檔案所在的目錄名稱，作為輸出子目錄的一部分
    file_dir_name = os.path.basename(os.path.dirname(filepath))
    # 獲取專案根目錄到檔案路徑之間的相對路徑部分 (例如 'knowledge/law')
    # 這一步比較複雜，為了簡化，我們可以這樣做：
    # 假設所有要處理的檔案都在 SOURCE_MD_DIR 之下
    relative_to_base_source = os.path.relpath(filepath, SOURCE_MD_DIR)
    # 輸出目錄應該是 OUTPUT_CHUNKS_DIR + 原始檔案的相對路徑目錄
    output_target_dir = os.path.join(OUTPUT_CHUNKS_DIR, os.path.dirname(relative_to_base_source))
    
    # 如果 OUTPUT_CHUNKS_DIR 不存在則創建
    if not os.path.exists(output_target_dir):
        os.makedirs(output_target_dir)

    base_filename = os.path.splitext(os.path.basename(filepath))[0]
    
    # 將每個 chunk 保存為一個新的 Markdown 檔案
    for i, chunk_content in enumerate(chunks):
        chunk_filename = f"{base_filename}_chunk_{i+1}.md"
        output_filepath = os.path.join(output_target_dir, chunk_filename)
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            outfile.write(chunk_content)
        print(f"  - 已生成 chunk: {output_filepath}")

    print(f"檔案 '{os.path.basename(filepath)}' 已處理完畢並分塊保存。")

#一次處理所有md檔案
def process_all_markdown_files():
    """
    遍歷指定目錄下的所有 Markdown 檔案，對其進行分塊處理，
    並將切割後的 chunks 保存到指定的輸出目錄。
    """
    if not os.path.exists(OUTPUT_CHUNKS_DIR):
        os.makedirs(OUTPUT_CHUNKS_DIR)

    for root, _, files in os.walk(SOURCE_MD_DIR):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, SOURCE_MD_DIR) # 獲取相對於 SOURCE_MD_DIR 的路徑

                print(f"正在處理檔案: {filepath}")
                chunks = chunk_markdown_by_headings(filepath)

                # 為這個檔案創建對應的輸出子目錄
                output_subdir = os.path.join(OUTPUT_CHUNKS_DIR, os.path.dirname(relative_path))
                if not os.path.exists(output_subdir):
                    os.makedirs(output_subdir)

                base_filename = os.path.splitext(file)[0]
                
                # 將每個 chunk 保存為一個新的 Markdown 檔案
                for i, chunk_content in enumerate(chunks):
                    chunk_filename = f"{base_filename}_chunk_{i+1}.md"
                    output_filepath = os.path.join(output_subdir, chunk_filename)
                    with open(output_filepath, 'w', encoding='utf-8') as outfile:
                        outfile.write(chunk_content)
                    print(f"  - 已生成 chunk: {output_filepath}")

    print("\n所有 Markdown 檔案已處理完畢並分塊保存。")
    print(f"Chunks 已保存到目錄: {OUTPUT_CHUNKS_DIR}")

if __name__ == "__main__":
    # --- 選擇以下其中一種方式執行 ---

    # 1. 處理指定單一檔案
    # 請根據您的實際路徑修改這個範例路徑
    single_file_to_chunk = os.path.join(SOURCE_MD_DIR, '臺北市政府衛生局114年6月份處理化粧品違規廣告處罰案件統計表.md')
    # 或者如果您知道絕對路徑：
    # single_file_to_chunk = r"C:\Users\YourUser\test_index_wonders\knowledge\law\臺北市政府衛生局114年6月份處理化粧品違規廣告處罰案件統計表.md"

    process_single_markdown_file(single_file_to_chunk)

    # 2. 處理預設目錄下的所有 Markdown 檔案 (如果需要，請取消註解)
    # process_all_markdown_files_in_dir()