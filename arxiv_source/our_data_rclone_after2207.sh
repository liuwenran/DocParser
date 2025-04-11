#!/bin/bash

input_file="/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/info/our_data_arxiv_id_filtered_equal2207.txt"
dest_root="/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_our_data/arxiv_source_2207"

mkdir -p "$dest_root"

while IFS= read -r arxiv_id; do
    echo "Downloading $arxiv_id..."
    rclone copy --progress "OSS://pjlab-shpai-lol/mm_lol/arxiv_papers/arxiv-uncompressed/$arxiv_id" "$dest_root/$arxiv_id" 
done < "$input_file"

echo "下载完成"