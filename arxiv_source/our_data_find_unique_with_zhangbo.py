from pathlib import Path

def filter_paths_by_id(file1: str, file2: str, output_file: str = "filtered_paths.txt") -> None:
    """
    从 file2 中过滤路径，只保留 arXiv ID 在 file1 中不存在的行。

    Args:
        file1 (str): 第一个 txt 文件路径，包含参考 arXiv ID。
        file2 (str): 第二个 txt 文件路径，要过滤的路径。
        output_file (str): 保存过滤后路径的文件路径。
    """
    # 读取 file1 中的 arXiv ID
    ids_file1 = set()
    with open(file1, 'r', encoding='utf-8') as f1:
        for line in f1:
            path = line.strip()
            if path:
                arxiv_id = Path(path).name  # 提取 arXiv ID
                ids_file1.add(arxiv_id)

    # 过滤 file2，只保留 ID 不在 file1 中的路径
    filtered_paths = []
    with open(file2, 'r', encoding='utf-8') as f2:
        for line in f2:
            path = line.strip()
            if path:
                arxiv_id = Path(path).name
                if arxiv_id not in ids_file1:
                    filtered_paths.append(path)

    # 保存过滤后的路径
    if filtered_paths:
        with open(output_file, 'w', encoding='utf-8') as f:
            for path in filtered_paths:
                f.write(f"{path}\n")
        print(f"Saved {len(filtered_paths)} filtered paths to {output_file}")
    else:
        print("No paths remaining after filtering")

# 使用示例
file1 = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_cs.txt"  # 第一个 txt 文件路径
file2 = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique.txt"  # 第二个 txt 文件路径
output_file = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo.txt"  # 输出文件路径

filter_paths_by_id(file1, file2, output_file)