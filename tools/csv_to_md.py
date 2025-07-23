import pandas as pd
import os

def convert_csv_to_md(csv_file_path, output_dir):
    df = pd.read_csv(csv_file_path)
    base_name = os.path.splitext(os.path.basename(csv_file_path))[0]

    for index, row in df.iterrows():
        md_content = f"## {base_name} - 條目 {index + 1}\n\n"
        for column, value in row.items():
            md_content += f"**{column}**: {value}\n"
        md_content += "---\n\n" # 分隔不同條目

        output_md_path = os.path.join(output_dir, f"{base_name}_{index + 1}.md")
        with open(output_md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    print(f"Converted {csv_file_path} to Markdown files in {output_dir}")

if __name__ == "__main__":
    # 假設您的 CSV 檔案放在一個新的 'csvs/' 目錄中
    # 您需要根據實際路徑修改這裡
    csv_input_dir = 'original_file/csvs/' # 假設新增一個 csvs/ 目錄來存放原始 CSV
    output_knowledge_dir = 'knowledge/product_csv_data/' 

    if not os.path.exists(output_knowledge_dir):
        os.makedirs(output_knowledge_dir)

    for filename in os.listdir(csv_input_dir):
        if filename.endswith(".csv"):
            csv_path = os.path.join(csv_input_dir, filename)
            convert_csv_to_md(csv_path, output_knowledge_dir)