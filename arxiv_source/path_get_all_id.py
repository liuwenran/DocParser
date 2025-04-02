input_file = "/cpfs01/user/liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_clean_path.txt"
output_file = "/cpfs01/user/liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id.txt"

# 用集合去重
unique_paths = set()

with open(input_file, "r") as infile:
    for line in infile:
        # 分割路径，取前两部分
        parts = line.strip().split('/')
        if len(parts) >= 2:
            path = f"{parts[0]}/{parts[1]}"
            unique_paths.add(path)

# 写入结果
with open(output_file, "w") as outfile:
    for path in sorted(unique_paths):  # 可选排序
        outfile.write(path + "\n")

print("处理完成，结果保存在", output_file)