import argparse
import glob
import os
import shutil
from pathlib import Path
from typing import List
from tqdm import tqdm
from loguru import logger
import re
import math

from DocParser.vrdu import utils
from DocParser.vrdu import renderer
from DocParser.vrdu import preprocess
from DocParser.vrdu import layout_annotation as layout
from DocParser.vrdu import order_annotation as order
from DocParser.vrdu.config import config
from DocParser.vrdu.quality_check import generate_quality_report
from concurrent.futures import ProcessPoolExecutor

logger.add("vrdu_debug.log", mode="w")

def extract_bib_files(tex_file: Path) -> List[str]:
    """Extract .bib filenames from \bibliography in the TeX file."""
    with open(tex_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配 \bibliography{file1, file2}
    bib_match = re.search(r'\\bibliography\s*\{([^}]+)\}', content)
    if not bib_match:
        logger.warning(f"No \\bibliography found in {tex_file}")
        return []

    # 提取 bib 文件名并去除空格
    bib_names = [name.strip() for name in bib_match.group(1).split(',')]
    # 添加 .bib 扩展名
    bib_files = [f"{name}.bib" if not name.endswith('.bib') else name for name in bib_names]
    return bib_files

def copy_bib_files(bib_files: List[str], source_dir: Path, target_dir: Path) -> None:
    """Copy .bib files from source directory to target directory."""
    for bib_file in bib_files:
        source_path = source_dir / bib_file
        target_path = target_dir / bib_file
        if source_path.exists():
            if not target_path.parent.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, target_path)
            logger.info(f"Copied {bib_file} to {target_path}")
        else:
            logger.warning(f"Bib file {source_path} not found")

def copy_bbl_files(source_dir: Path, target_dir: Path) -> None:
    """
    Copy all .bbl files from the source directory to the target directory.

    Args:
        source_dir (Path): The source directory containing .bbl files.
        target_dir (Path): The target directory to copy .bbl files to.

    Returns:
        None
    """
    for file in source_dir.glob("*.bbl"):
        target_file = target_dir / file.name
        if not target_file.exists():  # 避免覆盖已有文件
            shutil.copy(file, target_file)
            logger.info(f"Copied {file} to {target_file}")


def get_redundant_folders(main_directory: Path) -> List[str]:
    """Get list of redundant folders to remove."""
    pattern = f"{main_directory}/output/paper_{config.folder_prefix}*"
    redundant_folders = glob.glob(pattern)
    redundant_folders.extend(
        [
            f"{main_directory}/output/paper_white",
            f"{main_directory}/output/paper_original",
        ]
    )
    return redundant_folders


def remove_redundant_stuff(main_directory: Path) -> None:
    """
    Remove redundant files and folders from the main directory.

    Args:
        main_directory (Path): The path of the main directory.

    Returns:
        None
    """
    # remove generated tex related files
    for file in glob.glob(f"{main_directory}/paper_*.*"):
        os.remove(file)

    # remove useless pdf and image files
    for folder in get_redundant_folders(main_directory):
        if os.path.exists(folder):
            shutil.rmtree(folder)


def check_if_already_processed(file_name: Path, output_root_path: Path) -> bool:
    output_dir = output_root_path / str(file_name).split('/')[-2]
    paper_original_tex_file = output_dir / "paper_original.tex"
    return paper_original_tex_file.exists()


def process_one_file(file_name: Path, output_root_path: Path=None) -> None:
    """
    Process a file through multiple steps including preprocessing, rendering,
    transforming into images, generating annotations, and handling exceptions.

    Args:
        file_name (str): The path to the main .tex file to be processed.

    Returns:
        None
    """
    main_directory = Path(file_name).parent
    logger.info(f"[VRDU] file: {file_name}, start processing.")

    # check if this paper has been processed
    if check_if_already_processed(file_name, output_root_path):
        logger.info(f"[VRDU] file: {file_name}, paper has been processed")
        return 1

    # make a copy of the original tex file
    original_tex = main_directory / "paper_original.tex"
    if not file_name.exists():
        logger.error(f"File not found: {file_name}")
        return 0

    shutil.copyfile(file_name, original_tex)

    # remove the output folder if it exists
    output_directory = main_directory / "output"
    if output_directory.exists():
        shutil.rmtree(output_directory)

    # change the working directory to the main directory of the paper
    cwd = os.getcwd()

    try:
        # change the working directory to the main directory of the paper
        os.chdir(main_directory)
        # create output folder and output/result folder
        result_dir = output_directory / "result"
        result_dir.mkdir(parents=True, exist_ok=True)

        # step 1: preprocess the paper
        preprocess.run_dataset_prepare(original_tex, output_root_path)

        logger.info(f"[VRDU] file: {original_tex}, successfully processed.")

        return 1

    except Exception as e:
        error_type = e.__class__.__name__
        error_info = str(e)
        logger.error(
            f"[VRDU] file: {file_name}, type: {error_type}, message: {error_info}"
        )

        output_dir = output_root_path / str(original_tex).split('/')[-2]
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        # raise e
        return 0

    finally:
        # remove redundant files
        remove_redundant_stuff(main_directory)

        # Change back to original dir
        os.chdir(cwd)


def find_and_copy_bib_files(tex_file: Path, output_root_path: Path) -> None:
    """
    Find and copy .bib files from the source directory to the target directory.

    Args:
        tex_file (Path): The path to the main .tex file.
        output_root_path (Path): The path to the output root directory.

    Returns:
        None
    """
    # Create target directory if it doesn't exist
    target_dir = output_root_path / str(tex_file).split('/')[-2]

    original_tex = target_dir / "paper_original.tex"
    main_directory = tex_file.parent

    bib_files = extract_bib_files(original_tex)
    copy_bib_files(bib_files, main_directory, target_dir)


def main(cs_main_tex_papers, output_root_path) -> None:
    # process all papers
    failed_ids = []

    for ind, cs_main_tex_paper in enumerate(cs_main_tex_papers):
        print(f"Processing {ind+1}/{len(cs_main_tex_papers)}")
        arxiv_id = Path(cs_main_tex_paper).parts[-2]
        res = process_one_file(Path(cs_main_tex_paper), Path(output_root_path))
        if res == 1:
            find_and_copy_bib_files(Path(cs_main_tex_paper), Path(output_root_path))
        else:
            failed_ids.append(arxiv_id)
    return failed_ids

def process_paper(one_task) -> None:
    failed_ids = []
    new_processed_ids = []
    for ind, task in enumerate(one_task):
        if ind % 100 == 0:
            print(f"Processing {ind}/{len(one_task)}")
        cs_main_tex_paper, output_root_path = task
        arxiv_id = Path(cs_main_tex_paper).parts[-2]

        # check if this paper has been processed
        file_name = Path(cs_main_tex_paper)
        if check_if_already_processed(file_name, Path(output_root_path)):
            logger.info(f"[VRDU] file: {file_name}, paper has been processed")
            copy_bbl_files(file_name.parent, Path(output_root_path) / str(file_name).split('/')[-2])
            continue
        else:
            logger.info(f"[VRDU] file: {file_name}, this is new processing.")
            new_processed_ids.append(arxiv_id)

        res = process_one_file(Path(cs_main_tex_paper), Path(output_root_path))
        if res == 1:
            find_and_copy_bib_files(Path(cs_main_tex_paper), Path(output_root_path))
        else:
            failed_ids.append(arxiv_id)
    return failed_ids, new_processed_ids

def main_multiple(cs_main_tex_papers, output_root_path, failed_log) -> None:
    failed_ids_set = set()
    if Path(failed_log).exists():
        with open(failed_log, 'r', encoding='utf-8') as f:
            for line in f:
                arxiv_id = line.strip()
                if arxiv_id:
                    failed_ids_set.add(arxiv_id)
        print(f"Loaded {len(failed_ids_set)} failed IDs from {failed_log}")
    else:
        print(f"No existing failed log found at {failed_log}")

    tasks = []
    for paper in cs_main_tex_papers:
        arxiv_id = Path(paper).parts[-2]
        if arxiv_id not in failed_ids_set:
            tasks.append((paper, output_root_path))
    print(f"Processing {len(tasks)} papers after filtering out {len(cs_main_tex_papers) - len(tasks)} failed IDs")

    if not tasks:
        print("No papers to process after filtering")
        return

    max_workers = 32
    chunk_size = math.ceil(len(tasks) / max_workers)
    
    failed_ids = []
    new_processed_ids = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(max_workers):
            start = i * chunk_size
            end = (i + 1) * chunk_size
            one_task = tasks[start:end]
            futures.append(executor.submit(process_paper, one_task))
        
        for future in tqdm(futures, total=len(futures), desc="Processing papers"):
            result = future.result()
            failed_ids.extend(result[0])
            new_processed_ids.extend(result[1])

    if failed_ids:
        with open(failed_log, 'a', encoding='utf-8') as f:
            for arxiv_id in failed_ids:
                f.write(arxiv_id + '\n')
        print(f"Appended {len(failed_ids)} new failed arXiv IDs to {failed_log}")
    else:
        print("No new papers failed processing")

    print(f"new processed IDs: {len(new_processed_ids)}")


if __name__ == "__main__":
    # paper_root_path = '/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_uncompressed_total'
    # cs_main_tex_papers_path = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_cs_main_tex_csAI.txt'

    # cat_root_path = True
    # root_path = '/cpfs01/shared/llm_dev/liuwenran/arxiv/arxiv_source_uncompressed_total'
    # cs_main_tex_papers_abs_path = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_cs_main_tex.txt'
    # output_root_path = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/paper_parse_result'
    # failed_log = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_cs_main_tex_process_failed.txt'

    # cat_root_path = False
    # cs_main_tex_papers_abs_path = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_main_tex.txt'
    # output_root_path = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/paper_parse_result_our_data'
    # failed_log = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_main_tex_process_failed.txt'

    # cat_root_path = False
    # cs_main_tex_papers_abs_path = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_cs_wo_main_tex_single_tex.txt'
    # output_root_path = '/cpfs01/user/liuwenran/forks/DocParser/paper_parse_result_single_tex'
    # failed_log = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/data_info/arxiv_source_uncompressed_total_arxiv_id_path_cs_wo_main_tex_single_tex_process_failed.txt'

    cat_root_path = False
    cs_main_tex_papers_abs_path = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_wo_main_tex_single_tex.txt'
    output_root_path = '/cpfs01/user/liuwenran/forks/DocParser/paper_parse_result_our_data_single_tex'
    failed_log = '/home/liuwenran/cpfs01_liuwenran/forks/DocParser/arxiv_source/our_data_info/cs_abs_path_2207_2406_unique_with_zhangbo_wo_main_tex_single_tex_process_failed.txt'

    
    cs_main_tex_papers = []
    with open(cs_main_tex_papers_abs_path, "r") as f:
        for line in f:
            if cat_root_path:
                line = os.path.join(root_path, line.strip())
            cs_main_tex_papers.append(line.strip())

    main_multiple(cs_main_tex_papers, output_root_path, failed_log)


