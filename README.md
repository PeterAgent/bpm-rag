bpm-rag/
├── config.ini                 # 配置文件，包含所有模块的配置
├── base/
│   ├── config.py              # 配置管理，加载 config.ini
│   ├── logger.py              # 日志设置
├── rag_qa/
│   ├── core/
│   │   ├── prompts.py         # RAG 提示模板
│   │   ├── query_classifier.py # 查询分类器
│   │   ├── strategy_selector.py # 检索策略选择器
│   │   ├── vector_store.py    # 向量存储与检索
│   │   ├── rag_system.py      # RAG 系统核心逻辑
│   ├── main.py                # RAG 系统独立入口，支持存储和查询
├── mysql_qa/
│   ├── db/
│   │   ├── mysql_client.py    # MySQL 数据库操作
│   ├── cache/
│   │   ├── redis_client.py    # Redis 缓存操作
│   ├── retrieval/
│   │   ├── bm25_search.py     # BM25 搜索
│   ├── utils/
│   │   ├── preprocess.py      # 文本预处理
│   ├── main.py                # MySQL 系统独立入口，支持查询
├── main.py                    # 集成系统入口，结合 RAG 和 MySQL
├── requirements.txt           # 依赖文件
└── logs/
    └── app.log                # 日志文件