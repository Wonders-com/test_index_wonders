import pandas as pd
import os
from pathlib import Path
from typing import Optional
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 產品識別與資料夾映射（維護點：新增產品時只需更新這裡）
PRODUCT_FOLDER_MAP = {
    "威德益生菌": "product_weider_probiotic",
    "蔓越莓益生菌": "product_cranberry_probiotic",
    # 未來新增產品時在這裡添加
    # "膠原蛋白": "product_collagen",
}

def get_product_folder(csv_filename: str) -> str:
    """
    根據CSV檔名判斷應該輸出到哪個產品資料夾
    
    Args:
        csv_filename: CSV檔案名稱
        
    Returns:
        產品資料夾名稱，如果無法識別則使用預設資料夾
    """
    for product_key, folder_name in PRODUCT_FOLDER_MAP.items():
        if product_key in csv_filename:
            logger.info(f"識別產品: {product_key} -> {folder_name}")
            return folder_name
    
    # 如果無法識別，使用預設資料夾
    logger.warning(f"無法識別產品類型，使用預設資料夾: {csv_filename}")
    return "product_csv_data"

def convert_csv_to_md(csv_file_path: str, base_output_dir: str, 
                      fill_na: bool = True, encoding: str = 'utf-8') -> bool:
    """
    將單個 CSV 檔案轉換為 Markdown 檔案。
    
    Args:
        csv_file_path: CSV 檔案路徑
        base_output_dir: 基礎輸出目錄 (knowledge/)
        fill_na: 是否填充 NaN 值
        encoding: 檔案編碼
        
    Returns:
        bool: 轉換是否成功
    """
    csv_path = Path(csv_file_path)
    
    if not csv_path.exists():
        logger.error(f"CSV 檔案不存在: {csv_path}")
        return False
    
    # 根據檔名決定輸出資料夾
    product_folder = get_product_folder(csv_path.name)
    output_dir = Path(base_output_dir) / product_folder
    
    try:
        # 讀取 CSV，優先使用指定編碼
        df = pd.read_csv(csv_path, encoding=encoding)
        logger.info(f"成功讀取 CSV: {csv_path.name} (共 {len(df)} 行)")
        
    except UnicodeDecodeError:
        # 嘗試其他常見編碼
        encodings_to_try = ['utf-8-sig', 'big5', 'gb2312', 'cp1252', 'iso-8859-1']
        df = None
        
        for alt_encoding in encodings_to_try:
            try:
                df = pd.read_csv(csv_path, encoding=alt_encoding)
                logger.info(f"使用 {alt_encoding} 編碼成功讀取: {csv_path.name}")
                break
            except (UnicodeDecodeError, Exception):
                continue
        
        if df is None:
            logger.error(f"嘗試多種編碼均失敗: {csv_path}")
            return False
            
    except Exception as e:
        logger.error(f"讀取 CSV 檔案失敗 {csv_path.name}: {e}")
        return False
    
    # 處理空 DataFrame
    if df.empty:
        logger.warning(f"CSV 檔案為空: {csv_path}")
        return False
    
    # 填充 NaN 值 - 修正 pandas 新版本的語法
    if fill_na:
        df = df.ffill().fillna('')  # 使用新版本的 ffill() 語法
    
    # 生成 Markdown 內容
    md_content = _generate_markdown_content(df, csv_path.stem)
    
    # 確保輸出目錄存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 輸出檔案路徑與檔名
    output_file = output_dir / f"{csv_path.stem}.md"
    
    try:
        # 寫入檔案
        output_file.write_text(md_content, encoding='utf-8')
        logger.info(f"成功轉換: {csv_path.name} -> {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"寫入檔案失敗 {output_file}: {e}")
        return False

def _generate_markdown_content(df: pd.DataFrame, base_name: str) -> str:
    """生成 Markdown 內容"""
    content_parts = []
    
    for index, row in df.iterrows():
        # 添加標題
        content_parts.append(f"## {base_name} - 條目 {index + 1}\n")
        
        # 添加欄位內容
        for column, value in row.items():
            if pd.notna(value) and str(value).strip():  # 檢查非空且非空白
                # 處理換行符號，讓 Markdown 格式更美觀
                clean_value = str(value).replace('\n', ' ').replace('\r', '')
                content_parts.append(f"**{column}**: {clean_value}")
        
        content_parts.append("---\n")  # 分隔線
    
    return '\n'.join(content_parts)

def batch_convert_csv_to_md(input_dir: str, base_output_dir: str, 
                           pattern: str = "*.csv") -> dict:
    """
    批次轉換目錄中的所有 CSV 檔案
    
    Args:
        input_dir: 輸入目錄
        base_output_dir: 基礎輸出目錄 (knowledge/)
        pattern: 檔案匹配模式
        
    Returns:
        dict: 轉換結果統計
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        logger.error(f"輸入目錄不存在: {input_path}")
        return {"success": 0, "failed": 0, "total": 0}
    
    # 找到所有 CSV 檔案 - 使用遞迴搜尋並處理路徑格式
    csv_files = []
    
    # 如果是單一檔案路徑且是 CSV
    if input_path.is_file() and input_path.suffix.lower() == '.csv':
        csv_files = [input_path]
    else:
        # 遞迴搜尋所有 CSV 檔案
        csv_files = list(input_path.rglob("*.csv"))
    
    if not csv_files:
        logger.warning(f"在 {input_path} 中找不到 CSV 檔案")
        # 列出目錄內容以供調試
        if input_path.is_dir():
            all_files = [f.name for f in input_path.iterdir() if f.is_file()]
            logger.info(f"目錄中的檔案: {all_files[:10]}...")  # 只顯示前10個檔案
        return {"success": 0, "failed": 0, "total": 0}
    
    logger.info(f"找到 {len(csv_files)} 個 CSV 檔案")
    
    # 批次處理
    results = {"success": 0, "failed": 0, "total": len(csv_files)}
    
    for csv_file in csv_files:
        logger.info(f"處理檔案: {csv_file.name}")
        
        if convert_csv_to_md(str(csv_file), base_output_dir):
            results["success"] += 1
        else:
            results["failed"] += 1
    
    return results

def main():
    """主程式"""
    # 設定路徑
    csv_input_dir = 'original_file/csvs/'
    base_output_dir = 'knowledge/'  # 改為基礎目錄，讓程式自動分配子資料夾
    
    logger.info("開始 CSV 轉 Markdown 處理")
    logger.info(f"輸入目錄: {csv_input_dir}")
    logger.info(f"輸出基礎目錄: {base_output_dir}")
    logger.info("產品資料夾映射:")
    for product, folder in PRODUCT_FOLDER_MAP.items():
        logger.info(f"  {product} -> {base_output_dir}{folder}/")
    
    # 執行批次轉換
    results = batch_convert_csv_to_md(csv_input_dir, base_output_dir)
    
    # 輸出結果
    logger.info("=" * 50)
    logger.info("轉換完成!")
    logger.info(f"總檔案數: {results['total']}")
    logger.info(f"成功: {results['success']}")
    logger.info(f"失敗: {results['failed']}")
    
    if results['failed'] > 0:
        logger.warning(f"有 {results['failed']} 個檔案轉換失敗，請檢查日誌")

if __name__ == "__main__":
    main()