import os
import re
import json
from typing import Optional, List, Dict
import bibtexparser
from bibtexparser.bparser import BibTexParser
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexNode, LatexMacroNode
from pylatexenc.latex2text import LatexNodes2Text

def load_arxiv_folders(input_file: str) -> Dict[str, str]:
    """
    从磁盘读取 arXiv ID 到文件夹路径的字典。

    Args:
        input_file (str): JSON 文件路径，例如 'arxiv_id_to_folder.json'

    Returns:
        dict: {arxiv_id: folder_path}，如果文件不存在或读取失败，返回空字典
    """
    try:
        if not os.path.exists(input_file):
            print(f"文件 {input_file} 不存在")
            return {}
        with open(input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取失败: {str(e)}")
        return {}

def scan_processed_ids(output_dir: str) -> set:
    """
    扫描输出文件夹，获取已处理的 arXiv ID 集合。

    Args:
        output_dir (str): 输出文件夹路径

    Returns:
        set: 已处理的 arXiv ID 集合
    """
    processed_ids = set()
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建输出文件夹: {output_dir}")
            return processed_ids
        for file in os.listdir(output_dir):
            if file.endswith('.jsonl'):
                arxiv_id = file[:-6]  # 移除 '.jsonl'
                processed_ids.add(arxiv_id)
        print(f"找到 {len(processed_ids)} 个已处理的 arXiv ID")
        return processed_ids
    except Exception as e:
        print(f"扫描 {output_dir} 失败: {str(e)}")
        return processed_ids

def find_env_node_by_name(nodes: List[LatexNode], env_name: str) -> Optional[LatexEnvironmentNode]:
    """
    递归查找指定环境的 LatexEnvironmentNode。

    Args:
        nodes: LaTeX 节点列表
        env_name: 环境名称，例如 'thebibliography'

    Returns:
        LatexEnvironmentNode 或 None
    """
    for node in nodes:
        if isinstance(node, LatexEnvironmentNode) and node.environmentname == env_name:
            return node
        sub_nodes = getattr(node, 'nodelist', [])
        if hasattr(node, 'nodeargd') and node.nodeargd is not None:
            sub_nodes += node.nodeargd.argnlist
        env_node = find_env_node_by_name(sub_nodes, env_name)
        if env_node is not None:
            return env_node
    return None


def parse_bbl(bbl_node: LatexEnvironmentNode) -> List[Dict]:
    """
    解析 thebibliography 环境的节点，提取 citation 信息。
    - 有 \newblock：提取 id, author（第一个 \newblock 前）, title（第一个到第二个 \newblock）。
    - 无 \newblock：提取 id，其余存入 content（保留原始 LaTeX 格式）。

    Args:
        bbl_node: thebibliography 环境的节点

    Returns:
        list: 包含 citation 信息的字典列表
    """
    citations = []
    current_citation = None
    text_buffer = []
    newblock_count = 0

    for node in bbl_node.nodelist:
        if isinstance(node, LatexMacroNode) and node.macroname == "bibitem":
            # 保存上一个 citation
            if current_citation:
                content = "".join(text_buffer)
                # 清理 \bibitem 和 id，保留原始 LaTeX
                content = re.sub(r'\\bibitem\s*(?:\[[^\]]*\])?\s*\{.*?\}\s*', '', content)
                content = re.sub(rf'\b{re.escape(current_citation["id"])}\b\s*', '', content, flags=re.IGNORECASE)
                # 清理多余 {} 和换行
                content = re.sub(r'^\{\}\s*[\r\n]*', '', content)
                content = re.sub(r'\n\s*\n+', '\n', content).strip()

                if newblock_count >= 1:
                    # 有 \newblock，转换 author 和 title
                    from pylatexenc.latex2text import LatexNodes2Text
                    parts = re.split(r'\\newblock\s*', content)
                    converter = LatexNodes2Text(
                        keep_comments=False,
                        keep_braced_groups=True,
                        math_mode='text'
                    )
                    current_citation["author"] = converter.latex_to_text(parts[0]).strip() if parts else ""
                    current_citation["title"] = converter.latex_to_text(parts[1]).strip() if len(parts) > 1 else ""
                else:
                    current_citation["content"] = content

                citations.append(current_citation)
                text_buffer = []
                newblock_count = 0

            # 开始新的 citation
            citation = {"id": ""}
            # 提取 id
            key = None
            if node.nodeargs and node.nodeargs[0]:
                try:
                    key = node.nodeargs[0].latex_verbatim().strip('{}')
                    print(f"提取 ID 成功 (nodeargs): {key}")
                except Exception as e:
                    print(f"提取 bibitem ID 失败 (nodeargs): {str(e)}")
            else:
                print(f"nodeargs 为空，尝试备用提取: {node.latex_verbatim()}")

            # 备用正则提取 id
            if not key:
                temp_nodes = bbl_node.nodelist[bbl_node.nodelist.index(node):][:10]
                temp_content = "".join(n.latex_verbatim() for n in temp_nodes)
                key_match = re.search(r'\\bibitem\s*(?:\[[^\]]*\])?\s*\{(.*?)\}', temp_content)
                if key_match:
                    key = key_match.group(1).strip()
                    print(f"备用提取 ID 成功: {key}")
                else:
                    print(f"备用提取 ID 失败: {temp_content[:100]}...")

            citation["id"] = key if key else ""
            current_citation = citation

        elif current_citation:
            # 仅收集非 \bibitem 内容
            if not (isinstance(node, LatexMacroNode) and node.macroname == "bibitem"):
                if isinstance(node, LatexMacroNode) and node.macroname == "newblock":
                    newblock_count += 1
                text_buffer.append(node.latex_verbatim())

    # 保存最后一个 citation
    if current_citation and text_buffer:
        content = "".join(text_buffer)
        content = re.sub(r'\\bibitem\s*(?:\[[^\]]*\])?\s*\{.*?\}\s*', '', content)
        content = re.sub(rf'\b{re.escape(current_citation["id"])}\b\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'^\{\}\s*[\r\n]*', '', content)
        content = re.sub(r'\n\s*\n+', '\n', content).strip()

        if newblock_count >= 1:
            from pylatexenc.latex2text import LatexNodes2Text
            parts = re.split(r'\\newblock\s*', content)
            converter = LatexNodes2Text(
                keep_comments=False,
                keep_braced_groups=True,
                math_mode='text'
            )
            current_citation["author"] = converter.latex_to_text(parts[0]).strip() if parts else ""
            current_citation["title"] = converter.latex_to_text(parts[1]).strip() if len(parts) > 1 else ""
        else:
            current_citation["content"] = content

        citations.append(current_citation)

    return citations


def parse_bib(bib_path: str) -> List[Dict]:
    """
    解析 .bib 文件，提取 citation 信息。

    Args:
        bib_path: .bib 文件路径

    Returns:
        list: 包含 citation 信息的字典列表
    """
    try:
        with open(bib_path, 'r', encoding='utf-8', errors='ignore') as f:
            # 配置 BibTexParser 以接受非标准条目类型（如 @online）
            parser = BibTexParser(
                common_strings=True,
                ignore_nonstandard_types=False  # 允许非标准类型
            )
            bib_database = bibtexparser.load(f, parser)
        citations = []
        for entry in bib_database.entries:
            citations.append({
                "id": entry.get("ID", ""),
                "author": entry.get("author", ""),
                "title": entry.get("title", "")
            })
        return citations
    except Exception as e:
        print(f"解析 {bib_path} 失败: {str(e)}")
        return []

def parse_bib_files(tex_path: str) -> List[str]:
    """
    解析 .tex 文件，提取 \bibliography{...} 中引用的 .bib 文件名。

    Args:
        tex_path: .tex 文件路径

    Returns:
        list: 引用的 .bib 文件名列表（不含 .bib 扩展名）
    """
    bib_files = []
    bibliography_pattern = re.compile(r'\\bibliography\s*\{([^}]*)\}')
    
    try:
        with open(tex_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        matches = bibliography_pattern.findall(content)
        for match in matches:
            bib_names = [name.strip() for name in match.split(',')]
            bib_files.extend(bib_names)
        bib_files = list(dict.fromkeys([name for name in bib_files if name]))
    except FileNotFoundError:
        print(f"文件 {tex_path} 不存在")
    except Exception as e:
        print(f"解析 {tex_path} 失败: {str(e)}")
    return bib_files


def parse_citation(latex_path: Optional[str] = None, latex_folder: Optional[str] = None) -> List[Dict]:
    """
    解析 citation 信息，优先级：.bib > .bbl > thebibliography in .tex。
    如果 .bib 解析失败（返回空或异常），继续尝试 .bbl 和 thebibliography。

    Args:
        latex_path: .tex 文件路径（可选）
        latex_folder: 文件夹路径，用于查找 .bbl 或 .bib 文件（可选）

    Returns:
        list: 包含 citation 信息的字典列表
    """
    citations = []

    # 1. 从 .tex 文件查找 \bibliography 引用的 .bib 文件
    if latex_path and os.path.exists(latex_path):
        bib_files = parse_bib_files(latex_path)
        if bib_files and latex_folder:
            for bib_name in bib_files:
                bib_path = os.path.join(latex_folder, f"{bib_name}.bib")
                if os.path.exists(bib_path):
                    try:
                        citations = parse_bib(bib_path)
                        if citations:
                            print(f"成功从 {bib_path} 解析到 {len(citations)} 个 citation")
                            return 'from_bib', citations
                        else:
                            print(f"{bib_path} 解析结果为空，继续尝试 .bbl")
                    except Exception as e:
                        print(f"解析 {bib_path} 失败: {str(e)}, 继续尝试 .bbl")
    
    # 2. 查找 .bbl 文件
    if latex_folder:
        import ipdb;ipdb.set_trace();
        for file in os.listdir(latex_folder):
            if file.endswith(".bbl"):
                bbl_path = os.path.join(latex_folder, file)
                try:
                    with open(bbl_path, 'r', encoding='utf-8', errors='ignore') as f:
                        latex = f.read()
                    walker = LatexWalker(latex)
                    nodes, _, _ = walker.get_latex_nodes()
                    for node in nodes:
                        if isinstance(node, LatexEnvironmentNode) and node.environmentname == "thebibliography":
                            citations = parse_bbl(node)
                            if citations:
                                print(f"成功从 {bbl_path} 解析到 {len(citations)} 个 citation")
                                return 'from_bbl', citations
                            else:
                                print(f"{bbl_path} 解析结果为空，继续尝试 .tex")
                    print(f"{bbl_path}: 未找到 thebibliography 环境")
                except Exception as e:
                    print(f"解析 {bbl_path} 失败: {str(e)}, 继续尝试 .tex")
    
    # 3. 从 .tex 文件的 thebibliography 环境解析
    if latex_path and os.path.exists(latex_path):
        try:
            with open(latex_path, 'r', encoding='utf-8', errors='ignore') as f:
                latex = f.read()
            # 限制 LatexWalker 的解析深度，避免复杂文档卡住
            walker = LatexWalker(latex, tolerant_parsing=True)
            try:
                nodes = walker.get_latex_nodes(max_nodes=10000)  # 设置节点上限
            except Exception as parse_error:
                print(f"LatexWalker 解析 {latex_path} 失败: {str(parse_error)}，跳过 thebibliography")
                return []
            bbl_node = find_env_node_by_name(nodes, "thebibliography")
            if bbl_node:
                citations = parse_bbl(bbl_node)
                if citations:
                    print(f"成功从 {latex_path} 的 thebibliography 解析到 {len(citations)} 个 citation")
                    return 'from_tex', citations
                else:
                    print(f"{latex_path} 的 thebibliography 解析结果为空")
            else:
                print(f"{latex_path} 未找到 thebibliography 环境")
        except Exception as e:
            print(f"解析 {latex_path} 的 thebibliography 失败: {str(e)}")

    return []



def save_citation_for_arxiv_id(arxiv_id: str, from_type: str, citations: List[Dict], output_dir: str):
    """
    将单个 arXiv ID 的 citation 数据保存到以 arXiv ID 命名的 .jsonl 文件。

    Args:
        arxiv_id (str): arXiv ID
        citations (list): citation 信息列表
        output_dir (str): 输出文件夹路径
    """
    try:
        output_file = os.path.join(output_dir, f"{arxiv_id}.jsonl")
        with open(output_file, 'w', encoding='utf-8') as f:
            json_line = {"arxiv_id": arxiv_id, "from_type": from_type, "citations": citations}
            f.write(json.dumps(json_line, ensure_ascii=False) + '\n')
        print(f"已保存 {arxiv_id} 的 citation 到 {output_file}")
    except Exception as e:
        print(f"保存 {arxiv_id} 的 citation 失败: {str(e)}")

def get_arxiv_citation_mapping(arxiv_folders: Dict[str, str], output_dir: str) -> None:
    """
    根据 arXiv ID 到文件夹路径的字典，解析每个文件夹的 citation 信息，并逐个保存。

    Args:
        arxiv_folders: {arxiv_id: folder_path}
        output_dir: 输出文件夹路径，存储每个 arXiv ID 的 .jsonl 文件
    """
    # 扫描已处理的 arXiv ID
    processed_ids = scan_processed_ids(output_dir)
    print(f"已处理的 arXiv ID: {len(processed_ids)}")
    
    for arxiv_id, folder_path in arxiv_folders.items():
        if arxiv_id in processed_ids:
            continue
        
        tex_path = os.path.join(folder_path, 'paper_original.tex')
        from_type, citations = parse_citation(latex_path=tex_path, latex_folder=folder_path)
        
        # 立即保存结果
        if len(citations) > 0:
            save_citation_for_arxiv_id(arxiv_id, from_type, citations, output_dir)
        
        # 打印进度
        if citations:
            print(f"{arxiv_id}: 解析到 {len(citations)} 个 citation")
        else:
            print(f"{arxiv_id}: 未找到 citation 信息")

if __name__ == "__main__":
    input_file = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_tex_processed/info/arxiv_id_to_folder.json"
    output_dir = "/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_tex_processed/citations"
    
    # 读取 arXiv ID 到文件夹路径的映射
    arxiv_folders = load_arxiv_folders(input_file)
    if not arxiv_folders:
        print("无 arXiv ID 映射，退出")
        exit(1)
    
    # 筛选指定 arXiv ID
    # arxiv_ids = ['2003.12471', '2104.07926', '1501.05828', '1705.02307', '2105.07443', 
    #               '2012.02297', '1702.01160', '2104.03800', '2003.07915', '1901.00591']
    # arxiv_folders = {arxiv_id: arxiv_folders[arxiv_id] for arxiv_id in arxiv_ids if arxiv_id in arxiv_folders}
    
    # 解析 citation 信息并逐个保存
    get_arxiv_citation_mapping(arxiv_folders, output_dir)
    
    print(f"\n处理完成，输出保存在 {output_dir}")