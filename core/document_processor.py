# -*- coding: utf-8 -*-
"""
@Time ： 2026/10/30 17:02
@Author ：Peter Peng
@File ：document_processor.py
@Desc ：
"""
# 1. 导入模块
# 1.1 加载os模块，用于遍历指定文件夹，获取所有文件
import os
# 1.2 加载langchain框架中的文本文档加载器与MarkDown文件加载器
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
# 1.3 加载langchain框架中的文本切割模块 => Markdown需要切割，切割成若干个文档块
from langchain_text_splitters import MarkdownTextSplitter
# 1.4 加载datetime模块，用于获取当前时间，将来写入到文本块的元数据中
from datetime import datetime
# 1.5 加载自定义文本加载器与文件切割器
# 1.5.1 PDF/DOC/PPT/IMG等文件加载器
from rag_qa.edu_document_loaders import OCRPDFLoader, OCRDOCLoader, OCRPPTLoader, OCRIMGLoader
# 1.5.2 自定义文本切割器ChineseRecursiveTextSplitter中文文本切割器、AliTextSplitter阿里文本切割器（需要有模型的支持）
from rag_qa.edu_text_spliter import ChineseRecursiveTextSplitter
from rag_qa.edu_text_spliter import AliTextSplitter
# 1.6 加载配置文件与日志模块
from base import Config, setup_logging

# 2. 初始化配置
conf = Config()
logger = setup_logging('document_processor')

# 定义一个文档加载器字典，用于存储所有文件加载器
document_loaders = {
    ".txt": TextLoader,
    ".pdf": OCRPDFLoader,
    ".doc": OCRDOCLoader,
    ".docx": OCRDOCLoader,
    ".ppt": OCRPPTLoader,
    ".pptx": OCRPPTLoader,
    ".jpg": OCRIMGLoader,
    ".png": OCRIMGLoader,
    ".md": UnstructuredMarkdownLoader
}


# 3. 封装一个load_documents_from_directory函数，用于从指定目录加载文档，返回documents文档对象
def load_documents_from_directory(directory_path):
    # 3.1 定义一个documents列表，用于存储所有文档对象 => [Document(), Document(), Document()]
    documents = []
    # 3.2 定义支持的文件后缀列表
    supported_extensions = document_loaders.keys()
    # 3.3 获取学科信息 => basename代表获取一个路径中的最后一部分（文件夹名称）
    source = os.path.basename(directory_path).replace('_data', "")
    # 3.4 遍历目录下的所有文件
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension in supported_extensions:
                try:
                    loader_class = document_loaders[file_extension]
                    if file_extension == '.txt':
                        loader = loader_class(file_path, encoding='utf-8')
                    else:
                        loader = loader_class(file_path)
                    # 调用load方法加载文档对象
                    loaded_docs = loader.load()  # [Document(), Document()]
                    # 遍历文档对象，添加元数据
                    for doc in loaded_docs:
                        doc.metadata["source"] = source
                        doc.metadata["file_path"] = file_path
                        doc.metadata["timestamp"] = datetime.now().isoformat()
                        # print(doc.metadata)
                    # 把文档对象添加到documents列表中 => documents = []、loaded_docs = [Document(), Document()]
                    documents.extend(loaded_docs)
                    logger.info(f'成功加载文件：{file_path}')
                except Exception as e:
                    print(f"加载文件时发生错误！错误信息：{e}")
            else:
                logger.warning(f"不支持的文件类型：{file_path}")
    return documents


# 4. 封装一个process_documents函数，用于处理文档对象，返回切割后的所有子块信息
def process_documents(directory_path, parent_chunk_size=conf.PARENT_CHUNK_SIZE, child_chunk_size=conf.CHILD_CHUNK_SIZE,
                      chunk_overlap=conf.CHUNK_OVERLAP):
    # 4.1 获取指定路径下所有文档对象
    documents = load_documents_from_directory(directory_path)
    logger.info(f'成功加载了{len(documents)}个文档对象！')
    # 4.2 创建一个文本切割器对象 => 通用文档切割器 与 MarkDown文档切割器
    # 通用文档切割器
    parent_splitter = ChineseRecursiveTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=chunk_overlap)
    child_splitter = ChineseRecursiveTextSplitter(chunk_size=child_chunk_size, chunk_overlap=chunk_overlap)
    # MarkDown文档切割器
    markdown_parent_splitter = MarkdownTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=chunk_overlap)
    markdown_child_splitter = MarkdownTextSplitter(chunk_size=child_chunk_size, chunk_overlap=chunk_overlap)

    # 4.3 创建一个子块列表，用于存储所有子块对象
    child_chunks = []
    for i, doc in enumerate(documents):  # [(0, doc), (1, doc)]
        # 4.4 获取文件后缀
        file_extension = os.path.splitext(doc.metadata["file_path"])[1]
        # 4.5 根据文件后缀，选择合适的文本切割器
        is_markdown = (file_extension == '.md')  # True or False
        parent_splitter_to_use = markdown_parent_splitter if is_markdown else parent_splitter
        child_splitter_to_use = markdown_child_splitter if is_markdown else child_splitter
        logger.info(
            f"处理文档: {doc.metadata['file_path']}, 使用切分器: {'Markdown' if is_markdown else 'ChineseRecursive'}")
        # 4.6 切割文档，返回父文档对象
        parent_docs = parent_splitter_to_use.split_documents([doc])
        # 4.7 对父文档对象进行切割，返回子文档对象
        for j, parent_doc in enumerate(parent_docs):
            parent_id = f"doc_{i}_parent_{j}"
            parent_doc.metadata["parent_id"] = parent_id
            parent_doc.metadata["parent_content"] = parent_doc.page_content
            # 切割父块，返回子块对象
            sub_chunks = child_splitter_to_use.split_documents([parent_doc])
            for k, sub_chunk in enumerate(sub_chunks):
                sub_chunk.metadata["parent_id"] = parent_id
                sub_chunk.metadata["parent_content"] = parent_doc.page_content
                sub_chunk.metadata["id"] = f"{parent_id}_child_{k}"
                child_chunks.append(sub_chunk)

    logger.info(f"子块数量：{len(child_chunks)}")
    return child_chunks


if __name__ == '__main__':
    for sub_chunk in process_documents('../data/ai_data'):
        print(sub_chunk)
        print('-' * 80)
