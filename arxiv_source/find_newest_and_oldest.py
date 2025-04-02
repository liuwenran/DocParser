import re
input_file = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path.txt"
output_file = "/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_clean.txt"

# 读取所有 arXiv ID
# 正则表达式匹配 arXiv 路径
# pattern = r'^[a-zA-Z.-]+/[0-1][0-9][0-1][0-9]\.[0-9]{4}$'
pattern = r'^[a-zA-Z.-]+/[0-2][0-9][0-1][0-9]\.[0-9]{4,5}$'

ids = []

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        line = line.strip()
        if re.match(pattern, line):
            outfile.write(line + "\n")
            arxiv_id = line.split('/')[1]  # 提取第二个字段
            ids.append(arxiv_id)

# 排序并获取最老和最新
ids.sort()  # 按时间顺序排序
oldest = ids[0]
newest = ids[-1]

print(f"最老的论文 ID: {oldest}")
print(f"最新的论文 ID: {newest}")