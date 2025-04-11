from collections import Counter
from pathlib import Path

def split_duplicate_unique_paths_by_id(txt_file: str, duplicate_file: str = "duplicate_paths.txt", unique_file: str = "unique_paths.txt") -> None:
    """
    从 txt 文件中读取路径，根据 arXiv ID 判断重复，保留一条重复路径，其余放入唯一路径文件。

    Args:
        txt_file (str): 包含路径的 txt 文件路径。
        duplicate_file (str): 保存重复 ID 的单条路径文件。
        unique_file (str): 保存不重复路径（包括重复 ID 的其余路径）的文件。
    """
    # 读取所有路径并记录 arXiv ID
    paths = []
    arxiv_ids = []
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            path = line.strip()
            if path:  # 忽略空行
                paths.append(path)
                arxiv_id = Path(path).name
                arxiv_ids.append(arxiv_id)

    # 根据 arXiv ID 统计重复
    id_counts = Counter(arxiv_ids)

    # 分离重复和不重复的路径
    seen_ids = set()  # 记录已处理的重复 ID
    duplicates = []
    uniques = []

    for path in paths:
        arxiv_id = Path(path).name
        if id_counts[arxiv_id] > 1 and arxiv_id in seen_ids:
            # 对于重复的 ID，只保留第一条路径
            duplicates.append(path)
        elif id_counts[arxiv_id] == 1 or (id_counts[arxiv_id] > 1 and arxiv_id not in seen_ids):
            # 不重复的 ID 或重复 ID 的其余路径放入 uniques
            uniques.append(path)
            seen_ids.add(arxiv_id)


    # 保存重复的路径（每个 ID 只一条）
    if duplicates:
        with open(duplicate_file, 'w', encoding='utf-8') as f:
            for path in duplicates:
                f.write(f"{path}\n")
        print(f"Saved {len(duplicates)} duplicate paths to {duplicate_file}")
    else:
        print("No duplicate paths found")

    # 保存不重复的路径（包括重复 ID 的其余路径）
    if uniques:
        with open(unique_file, 'w', encoding='utf-8') as f:
            for path in uniques:
                f.write(f"{path}\n")
        print(f"Saved {len(uniques)} unique paths to {unique_file}")
    else:
        print("No unique paths found")

# 使用示例
txt_file = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406.txt"  # 替换为你的 txt 文件路径
duplicate_file = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_duplicate.txt" 
unique_file = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique.txt"
split_duplicate_unique_paths_by_id(txt_file, duplicate_file, unique_file)