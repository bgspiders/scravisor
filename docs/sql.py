CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    crawl_type INTEGER,
    run_type INTEGER,
    status INTEGER,
    crawl_interval_type INTEGER,
    config TEXT,
    class_name VARCHAR(50),
    main_host VARCHAR(100),
    remark VARCHAR(255),
    website_name VARCHAR(100),
    crawl_interval VARCHAR(50),
    index_url TEXT,
    crawl_start_time DATETIME,
    crawl_end_time DATETIME,
    next_crawl_time DATETIME,
    update_time DATETIME
);
"""
