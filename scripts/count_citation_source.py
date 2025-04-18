import os
import json
from collections import Counter
from typing import Dict

def count_citation_types(directory: str) -> Dict[str, int]:
    """
    统计目录下所有 .jsonl 文件中 from_type 的分布。

    Args:
        directory (str): 包含 .jsonl 文件的目录路径

    Returns:
        Dict[str, int]: from_type 到数量的映射（如 {'from_bib': X, 'from_bbl': Y}）
    """
    type_counter = Counter()
    total_files = 0
    failed_files = 0

    # 确保目录存在
    if not os.path.isdir(directory):
        print(f"错误: 目录 {directory} 不存在")
        return {}

    # 遍历 .jsonl 文件
    for filename in os.listdir(directory):
        if not filename.endswith('.jsonl'):
            continue
        total_files += 1
        file_path = os.path.join(directory, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 读取一行 JSON
                line = f.readline().strip()
                if not line:
                    print(f"警告: 文件 {filename} 为空")
                    failed_files += 1
                    continue

                # 解析 JSON
                data = json.loads(line)
                from_type = data.get('from_type', '')
                if not from_type:
                    print(f"警告: 文件 {filename} 缺少 from_type 字段")
                    failed_files += 1
                    continue

                # 计数
                type_counter[from_type] += 1

        except json.JSONDecodeError as e:
            print(f"错误: 文件 {filename} JSON 解析失败: {str(e)}")
            failed_files += 1
        except Exception as e:
            print(f"错误: 读取文件 {filename} 失败: {str(e)}")
            failed_files += 1

    # 打印统计结果
    print(f"\n统计完成:")
    print(f"总文件数: {total_files}")
    print(f"成功处理: {total_files - failed_files}")
    print(f"失败文件: {failed_files}")
    print("from_type 分布:")
    for from_type, count in type_counter.items():
        print(f"  {from_type}: {count}")

    return dict(type_counter)

if __name__ == "__main__":
    directory = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_tex_processed/citations"
    result = count_citation_types(directory)