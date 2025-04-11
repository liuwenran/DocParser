import os
from pathlib import Path

def check_tex_files(input_txt: str, output_tex: str = "single_tex_paths.txt", output_others: str = "multiple_or_no_tex.txt") -> None:
    """
    检查 txt 文件中每个 arXiv ID 对应文件夹是否只有一个 .tex 文件。
    如果是，输出 .tex 文件路径；如果不是，存入另一个文件。

    Args:
        input_txt (str): 输入 txt 文件路径，格式为 cs.类别/arXiv ID。
        base_dir (str): arXiv ID 文件夹的根目录。
        output_tex (str): 保存单一 .tex 文件路径的文件。
        output_others (str): 保存非单一 .tex 文件的行。
    """
    # 读取输入文件
    entries = []
    with open(input_txt, 'r', encoding='utf-8') as f:
        for line in f:
            entry = line.strip()
            if entry:
                entries.append(entry)

    single_tex_paths = []
    multiple_or_no_tex = []

    for entry in entries:
        # 构造文件夹路径，例如 base_dir/cs.CG/1503.03170
        # folder_path = os.path.join(base_dir, entry)
        folder_path = entry
        
        # 检查文件夹是否存在
        if not os.path.isdir(folder_path):
            multiple_or_no_tex.append(entry)
            continue

        # 查找 .tex 文件
        tex_files = [f for f in os.listdir(folder_path) if f.endswith('.tex')]
        
        if len(tex_files) == 1:
            # 只有一个 .tex 文件，输出完整路径
            tex_path = os.path.join(folder_path, tex_files[0])
            single_tex_paths.append(tex_path)
        else:
            # 没有或多个 .tex 文件，保留原始行
            multiple_or_no_tex.append(entry)

    # 保存单一 .tex 文件路径
    if single_tex_paths:
        with open(output_tex, 'w', encoding='utf-8') as f:
            for path in single_tex_paths:
                f.write(f"{path}\n")
        print(f"Saved {len(single_tex_paths)} single .tex paths to {output_tex}")

    # 保存非单一 .tex 文件的行
    if multiple_or_no_tex:
        with open(output_others, 'w', encoding='utf-8') as f:
            for entry in multiple_or_no_tex:
                f.write(f"{entry}\n")
        print(f"Saved {len(multiple_or_no_tex)} lines to {output_others}")

# 使用示例
input_txt = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_wo_main_tex.txt"  # 前一步生成的 txt 文件
# base_dir = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_uncompressed_total"  # 替换为实际的根目录
output_tex = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_wo_main_tex_single_tex.txt"
output_others = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_wo_main_tex_multiple_or_no_tex.txt"

check_tex_files(input_txt, output_tex, output_others)