SCHEMA = """
CREATE TABLE IF NOT EXISTS document_maps (
    document_id TEXT NOT NULL, knowledge_base_id TEXT NOT NULL, payload TEXT NOT NULL,
    PRIMARY KEY (document_id, knowledge_base_id)
);
CREATE TABLE IF NOT EXISTS document_map_pages (
    document_id TEXT NOT NULL, knowledge_base_id TEXT NOT NULL, pdf_page INTEGER NOT NULL,
    payload TEXT NOT NULL, PRIMARY KEY (document_id, knowledge_base_id, pdf_page)
);
CREATE TABLE IF NOT EXISTS document_map_sections (
    document_id TEXT NOT NULL, knowledge_base_id TEXT NOT NULL, section_id TEXT NOT NULL,
    parent_section_id TEXT, section_type TEXT NOT NULL, start_page INTEGER, end_page INTEGER,
    status TEXT NOT NULL, payload TEXT NOT NULL,
    PRIMARY KEY (document_id, knowledge_base_id, section_id)
);
CREATE INDEX IF NOT EXISTS map_section_parents ON document_map_sections(document_id, knowledge_base_id, parent_section_id);
CREATE TABLE IF NOT EXISTS document_map_topics (
    document_id TEXT NOT NULL, knowledge_base_id TEXT NOT NULL, topic_id TEXT NOT NULL,
    section_id TEXT, chapter_id TEXT, payload TEXT NOT NULL,
    PRIMARY KEY (document_id, knowledge_base_id, topic_id)
);
"""
