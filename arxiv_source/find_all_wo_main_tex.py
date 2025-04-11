from pathlib import Path

def filter_unique_arxiv_ids(file1: str, file2: str, output_file: str = "filtered_ids.txt") -> None:
    """
    从 file1 中过滤出 arXiv ID 在 file2 中不存在的行，保留原始格式。

    Args:
        file1 (str): 第一个 txt 文件路径，格式为 cs.类别/arXiv ID。
        file2 (str): 第二个 txt 文件路径，格式为 cs.类别/arXiv ID/main.tex。
        output_file (str): 保存过滤结果的文件路径。
    """
    # 读取 file2 中的 arXiv ID
    ids_file2 = set()
    with open(file2, 'r', encoding='utf-8') as f2:
        for line in f2:
            path = line.strip()
            if path:
                # 提取 arXiv ID，例如从 cs.AI/1011.4632/main.tex 中提取 1011.4632
                arxiv_id = Path(path).parent.name.split('/')[-1]
                ids_file2.add(arxiv_id)

    # 过滤 file1，保留 ID 不在 file2 中的行
    filtered_lines = []
    with open(file1, 'r', encoding='utf-8') as f1:
        for line in f1:
            entry = line.strip()
            if entry:
                # 提取 arXiv ID，例如从 cs.CG/1503.01837 中提取 1503.01837
                arxiv_id = entry.split('/')[-1]
                if arxiv_id not in ids_file2:
                    filtered_lines.append(entry)

    # 保存结果
    if filtered_lines:
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in filtered_lines:
                f.write(f"{line}\n")
        print(f"Saved {len(filtered_lines)} filtered lines to {output_file}")
    else:
        print("No lines remaining after filtering")

# 使用示例
file1 = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo.txt"  # 第一个 txt 文件路径
file2 = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_main_tex_fullpath.txt"  # 第二个 txt 文件路径
output_file = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_wo_main_tex.txt"  # 输出文件路径

filter_unique_arxiv_ids(file1, file2, output_file)