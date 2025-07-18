import PyPDF2

def extract_text_from_pdf_pypdf2(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"  # 提取每頁文字並換行
    except Exception as e:
        print(f"提取 PDF 時發生錯誤: {e}")
    return text

# 使用範例：
# 請將 'your_document.pdf' 替換為您實際的 PDF 檔案路徑
pdf_file_path = r"PDF\公告114年6月份處理化粧品違規廣告處罰案件統計表.pdf"
extracted_content = extract_text_from_pdf_pypdf2(pdf_file_path)

if extracted_content:
    print("--- 提取到的文字內容 ---")
    print(extracted_content)
    
    # 您也可以將其儲存到文字檔案
    with open('output_pypdf2.md', 'w', encoding='utf-8') as f:
        f.write(extracted_content)
    print("\n內容已儲存至 output_pypdf2.md")