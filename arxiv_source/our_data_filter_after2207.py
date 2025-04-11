input_file = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/info/our_data_arxiv_id_filtered.txt"
output_file = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/info/our_data_arxiv_id_filtered_equal2207.txt"

# 过滤 2207 及之后的 ID
with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        arxiv_id = line.strip()
        if arxiv_id:  # 确保非空行
            yymm = arxiv_id.split('.')[0]  # 提取 YYMM
            if len(yymm) == 4 and yymm.isdigit() and int(yymm) == 2207:
                outfile.write(arxiv_id + "\n")

print("过滤完成，结果保存在", output_file)