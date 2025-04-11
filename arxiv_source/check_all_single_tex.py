from pathlib import Path

def filter_existing_files(input_txt: str, output_txt: str = "existing_files.txt") -> None:
    """
    检查 txt 文件中每行路径对应的文件是否存在，将存在的路径保存到新文件。

    Args:
        input_txt (str): 输入 txt 文件路径。
        output_txt (str): 保存存在文件路径的新文件。
    """
    existing_paths = []
    
    # 读取输入文件
    with open(input_txt, 'r', encoding='utf-8') as f:
        for line in f:
            path = line.strip()
            if path and Path(path).is_file():  # 检查文件是否存在
                existing_paths.append(path)
    
    # 写入存在的路径到新文件
    if existing_paths:
        with open(output_txt, 'w', encoding='utf-8') as f:
            for path in existing_paths:
                f.write(f"{path}\n")
        print(f"Saved {len(existing_paths)} existing file paths to {output_txt}")
    else:
        print(f"No existing files found in {input_txt}")

# 使用示例
# input_txt = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_wo_main_tex_single_tex.txt"
# output_txt = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_wo_main_tex_single_tex_checked.txt"

input_txt = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_cs_wo_main_tex_single_tex.txt'
output_txt = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_cs_wo_main_tex_single_tex_checked.txt'

filter_existing_files(input_txt, output_txt)