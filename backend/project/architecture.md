                         ┌──────────────────────┐
                         │       FRONTEND       │
                         │     React / Vite     │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │       API LAYER      │
                         │        FastAPI       │
                         └──────────┬───────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
 ┌────────────────┐        ┌────────────────┐        ┌────────────────┐
 │ PDF Management │        │ Practice Engine│        │  Chat / Query  │
 │ Upload / Delete│        │ MCQ / Topics   │        │    Engine      │
 └───────┬────────┘        └───────┬────────┘        └───────┬────────┘
         │                         │                         │
         ▼                         ▼                         ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │                    DOCUMENT INTELLIGENCE                        │
 ├─────────────────────────────────────────────────────────────────┤
 │ PDF Parser → Layout Detection → Cleaning → Chunking             │
 │                         ↓                                       │
 │              Structure / Hierarchy Extraction                   │
 │                         ↓                                       │
 │       Chapter → Section → Subsection → Concept → Page           │
 └──────────────────────────────┬──────────────────────────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              │                 │                  │
              ▼                 ▼                  ▼
       ┌─────────────┐   ┌─────────────┐   ┌──────────────┐
       │  Metadata   │   │   Embedding  │   │   Summaries  │
       │   Store     │   │   Generation │   │  Page/Topic  │
       └──────┬──────┘   └──────┬──────┘   └──────┬───────┘
              │                 │                  │
              ▼                 ▼                  ▼
       ┌─────────────────────────────────────────────────┐
       │                  STORAGE LAYER                  │
       │ PostgreSQL + pgvector                           │
       │                                                 │
       │ Documents | Pages | Chunks | Hierarchy         │
       │ Embeddings | Questions | Attempts | Evidence   │
       └────────────────────────┬────────────────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │    RETRIEVAL ENGINE    │
                    ├────────────────────────┤
                    │ Semantic Search         │
                    │ BM25                   │
                    │ Hybrid Retrieval        │
                    │ Metadata Filtering      │
                    │ Neighbor Expansion      │
                    │ Reranking               │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │       LLM LAYER        │
                    ├────────────────────────┤
                    │ Answer Generation      │
                    │ MCQ Generation         │
                    │ Explanation             │
                    │ Topic Extraction        │
                    │ Structured Output       │
                    └───────────┬────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
       ┌────────────┐    ┌────────────┐    ┌──────────────┐
       │   Answer   │    │   MCQ      │    │   Evidence   │
       │ + Sources  │    │  Practice  │    │    Chain     │
       └────────────┘    └────────────┘    └──────────────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                    ┌────────────────────────┐
                    │   LEARNING ANALYTICS   │
                    │                        │
                    │ Accuracy               │
                    │ Weak Topics            │
                    │ Progress               │
                    │ Difficulty             │
                    │ Adaptive Practice      │
                    └────────────────────────┘