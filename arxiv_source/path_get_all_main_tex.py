cs_file = "/cpfs01/user/liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_clean.txt"    # cs 开头的路径文件
all_file = "/cpfs01/user/liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_clean_path.txt"  # 所有文件路径文件
output_file = "/cpfs01/user/liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_main_tex.txt"  # 结果文件

# 读取所有文件路径到集合
with open(all_file, "r") as f:
    all_paths = set(line.strip() for line in f)

# 检查每个 cs 路径
with open(cs_file, "r") as f_cs, open(output_file, "w") as f_out:
    for cs_path in f_cs:
        cs_path = cs_path.strip()
        target = f"{cs_path}/main.tex"
        if target in all_paths:
            f_out.write(f"{target}\n")
        #     f_out.write(f"{target} exists\n")
        # else:
        #     f_out.write(f"{target} does not exist\n")

print("检查完成，结果保存在", output_file)