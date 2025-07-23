import os
import PyPDF2

# PDF 來源與 .md 輸出位置（可自訂分類）
PDF_DIR = "original_file/pdfs"
MD_OUTPUT_DIR = "knowledge/law"

# 確保輸出資料夾存在
os.makedirs(MD_OUTPUT_DIR, exist_ok=True)

def extract_text_from_pdf_pypdf2(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"  # 提取每頁文字並換行
    except Exception as e:
        print(f"❌ 無法處理 PDF 檔案：{pdf_path}，錯誤：{e}")
    return text

# 遍歷 pdfs 資料夾
pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]

if not pdf_files:
    print("⚠️ 沒有找到任何 PDF 檔案。")
else:
    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        md_filename = os.path.splitext(pdf_file)[0] + ".md"
        md_path = os.path.join(MD_OUTPUT_DIR, md_filename)

        # 跳過已轉換的 PDF
        if os.path.exists(md_path):
            print(f"⏭️ 已存在，略過：{md_filename}")
            continue

        content = extract_text_from_pdf_pypdf2(pdf_path)

        if content:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已轉換：{pdf_file} ➝ {md_filename}")
        else:
            print(f"⚠️ 無法提取內容：{pdf_file}")

# 使用範例：
# 請將 'your_document.pdf' 替換為您實際的 PDF 檔案路徑
#pdf_file_path = r"PDF\公告114年6月份處理化粧品違規廣告處罰案件統計表.pdf"
#extracted_content = extract_text_from_pdf_pypdf2(pdf_file_path)

#if extracted_content:
#    print("--- 提取到的文字內容 ---")
#    print(extracted_content)
    
    # 您也可以將其儲存到文字檔案
#    with open('output_pypdf2.md', 'w', encoding='utf-8') as f:
#        f.write(extracted_content)
#    print("\n內容已儲存至 output_pypdf2.md")