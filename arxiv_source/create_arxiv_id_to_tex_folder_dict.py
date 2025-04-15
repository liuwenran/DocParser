import os
import re
import json
from collections import OrderedDict

def list_arxiv_folders(root_dir):
    """
    扫描指定目录下的四个子目录，列出所有以 arXiv ID 命名的文件夹，
    去重后返回一个字典，键为 arXiv ID，值为文件夹路径。

    Args:
        root_dir (str): 根目录路径，例如 '/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_tex_processed'

    Returns:
        dict: {arxiv_id: folder_path}
    """
    # arXiv ID 的正则表达式，例如 '1234.5678' 或 '1234.5678v1'
    arxiv_id_pattern = re.compile(r'^\d{4}\.\d{4,5}$')
    
    # 子目录列表
    subdirs = [
        'paper_parse_result',
        'paper_parse_result_our_data',
        'paper_parse_result_our_data_single_tex',
        'paper_parse_result_single_tex'
    ]
    
    # 存储结果的字典
    arxiv_folders = OrderedDict()
    
    # 遍历每个子目录
    for subdir in subdirs:
        subdir_path = os.path.join(root_dir, subdir)
        if not os.path.exists(subdir_path):
            print(f"子目录 {subdir_path} 不存在，跳过")
            continue
            
        # 列出子目录下的所有文件夹
        for folder_name in os.listdir(subdir_path):
            folder_path = os.path.join(subdir_path, folder_name)
            
            # 只处理文件夹
            if not os.path.isdir(folder_path):
                continue
                
            # 检查文件夹名是否符合 arXiv ID 格式
            if arxiv_id_pattern.match(folder_name):
                # 去掉版本号（例如 '1234.5678v1' -> '1234.5678'）
                arxiv_id = folder_name.split('v')[0]
                
                # 如果 arXiv ID 已存在，跳过（优先保留较早的目录）
                if arxiv_id not in arxiv_folders:
                    arxiv_folders[arxiv_id] = folder_path
    
    return dict(arxiv_folders)

def save_arxiv_folders(arxiv_folders, output_file):
    """
    将 arXiv ID 到文件夹路径的字典保存到磁盘（JSON 格式）。

    Args:
        arxiv_folders (dict): {arxiv_id: folder_path}
        output_file (str): 保存的文件路径，例如 'arxiv_folders.json'
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(arxiv_folders, f, indent=4, ensure_ascii=False)
        print(f"字典已保存到 {output_file}")
    except Exception as e:
        print(f"保存失败: {str(e)}")

def load_arxiv_folders(input_file):
    """
    从磁盘读取 arXiv ID 到文件夹路径的字典。

    Args:
        input_file (str): 读取的文件路径，例如 'arxiv_folders.json'

    Returns:
        dict: {arxiv_id: folder_path}，如果文件不存在或读取失败，返回空字典
    """
    try:
        if not os.path.exists(input_file):
            print(f"文件 {input_file} 不存在")
            return {}
        with open(input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取失败: {str(e)}")
        return {}

if __name__ == "__main__":
    root_dir = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_tex_processed"
    output_file = "full_info/arxiv_id_to_folder.json"
    
    # 生成字典
    result = list_arxiv_folders(root_dir)
    
    # 打印结果
    print("arXiv ID 到文件夹路径的映射：")
    for arxiv_id, path in result.items():
        print(f"{arxiv_id}: {path}")
    print(f"\n共找到 {len(result)} 个唯一 arXiv ID 文件夹")
    
    # 保存到磁盘
    save_arxiv_folders(result, output_file)
    
    # 测试读取
    loaded_result = load_arxiv_folders(output_file)
    print("\n从磁盘读取的字典：")
    print(f"共 {len(loaded_result)} 个条目")
    for arxiv_id, path in list(loaded_result.items())[:5]:  # 仅打印前 5 个以节省空间
        print(f"{arxiv_id}: {path}")