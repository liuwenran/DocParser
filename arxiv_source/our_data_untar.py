import os
import tarfile
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

def extract_tar(args: tuple) -> None:
    """
    解压单个 .tar 文件到指定目录。

    Args:
        args (tuple): (source_tar_path, target_dir)
    """
    source_tar_path, target_dir = args
    arxiv_id = Path(source_tar_path).stem  # 提取文件名，例如 "2401.00001"
    extract_path = target_dir / arxiv_id

    # 如果目标目录已存在，跳过解压
    if extract_path.exists():
        print(f"Skipping {arxiv_id}: already extracted")
        return

    try:
        # 创建目标目录
        extract_path.mkdir(parents=True, exist_ok=True)
        # 解压 .tar 文件
        with tarfile.open(source_tar_path, 'r') as tar:
            tar.extractall(path=extract_path)
        print(f"Extracted {arxiv_id} to {extract_path}")
    except Exception as e:
        print(f"Error extracting {arxiv_id}: {e}")

def extract_all_tar_files(txt_file: str, source_dir: str, target_dir: str, max_workers: int = 8) -> None:
    """
    遍历 source_dir 中的所有 .tar 文件，并解压到 target_dir。

    Args:
        source_dir (str): 包含 arXiv ID 文件夹的源目录。
        target_dir (str): 解压目标目录。
        max_workers (int): 并行进程数，默认 8。
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)

    # 确保目标目录存在
    target_path.mkdir(parents=True, exist_ok=True)

    # 读取 txt 文件中的 arXiv ID
    arxiv_ids = []
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            arxiv_id = line.strip()
            if arxiv_id:  # 忽略空行
                arxiv_ids.append(arxiv_id)

    # 构造 .tar 文件路径
    tar_files = []
    for arxiv_id in arxiv_ids:
        tar_file = source_path / arxiv_id / f"{arxiv_id}.tar"
        if os.path.exists(tar_file):  # 检查文件是否存在
            tar_files.append((str(tar_file), target_path))
        else:
            print(f"Warning: {tar_file} does not exist")
    if not tar_files:
        print("No .tar files found in source directory")
        return

    # 使用 ProcessPoolExecutor 并行解压
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        list(tqdm(executor.map(extract_tar, tar_files), total=len(tar_files), desc="Extracting tar files"))

# 使用示例
# txt_file = '/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/info/our_data_arxiv_source_2401_2406.txt'
# source_dir = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/arxiv_source_2401_2406"
# target_dir = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/arxiv_source_2401_2406_uncompressed"

# txt_file = '/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/info/our_data_arxiv_source_2309_2312.txt'
# source_dir = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/arxiv_source_2309_2312"
# target_dir = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/arxiv_source_2309_2312_uncompressed"

txt_file = '/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/info/our_data_arxiv_source_2304_2309.txt'
source_dir = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/arxiv_source_2304_2309"
target_dir = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/arxiv_source_2304_2309_uncompressed"


extract_all_tar_files(txt_file, source_dir, target_dir)
