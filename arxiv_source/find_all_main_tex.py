import os

def find_direct_subdirectories_with_main_tex(root_dir, output_file=None):
    """
    找到根目录下直接子目录中包含 main.tex 文件的目录，并保存结果。
    参数：
        root_dir: 根目录路径。
        output_file: 可选参数，如果提供，则将结果保存到指定文件中。
    返回：
        包含 main.tex 文件的直接子目录名列表。
    """
    directories_with_main_tex = []

    # 获取根目录下的直接子目录
    for entry in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, entry)
        if os.path.isdir(subdir_path):  # 确保是目录
            main_tex_path = os.path.join(subdir_path, "main.tex")
            if os.path.isfile(main_tex_path):  # 检查是否存在 main.tex
                directories_with_main_tex.append(subdir_path)
                print(f"Found main.tex in: {subdir_path}")

    # 如果提供了 output_file，将结果保存到文件中
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for directory in directories_with_main_tex:
                f.write(directory + '\n')
        print(f"Results saved to {output_file}")

    return directories_with_main_tex


def find_direct_subdirectories_with_main_tex_from_path(abs_path_txt, output_file=None):
    """
    找到根目录下直接子目录中包含 main.tex 文件的目录，并保存结果。
    参数：
        root_dir: 根目录路径。
        output_file: 可选参数，如果提供，则将结果保存到指定文件中。
    返回：
        包含 main.tex 文件的直接子目录名列表。
    """
    directories_with_main_tex = []

    # 获取根目录下的直接子目录
    with open(abs_path_txt, 'r', encoding='utf-8') as f1:
        for line in f1:
            subdir_path = line.strip()
            if os.path.isdir(subdir_path):  # 确保是目录
                main_tex_path = os.path.join(subdir_path, "main.tex")
                if os.path.isfile(main_tex_path):  # 检查是否存在 main.tex
                    directories_with_main_tex.append(subdir_path)
                    print(f"Found main.tex in: {subdir_path}")

    # 如果提供了 output_file，将结果保存到文件中
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for directory in directories_with_main_tex:
                f.write(directory + '\n')
        print(f"Results saved to {output_file}")

    return directories_with_main_tex


if __name__ == "__main__":
    # 输入根目录路径
    abs_path_txt = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo.txt"

    # 输出文件路径（可选）
    output_file_path = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_main_tex.txt"

    # 查找并保存包含 main.tex 的子目录
    result = find_direct_subdirectories_with_main_tex_from_path(abs_path_txt, output_file=output_file_path)

    # 打印总计数量
    print(f"Total directories containing 'main.tex': {len(result)}")