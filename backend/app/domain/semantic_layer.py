import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from app.services.llm_service import llm_service

class SemanticLayer:
    def __init__(self):
        # 1. Constraint Engine: Golden Rules
        self.golden_rules = [
            "PREDICATE PUSHDOWN: Always filter by partition columns (e.g., 'event_date', 'year', 'month') BEFORE joining.",
            "BROADCAST JOINS: Use F.broadcast() for dimension tables under 10MB.",
            "COLUMN PRUNING: Select only required columns before applying transformations or joins.",
            "AVOID SHUFFLES: Minimize distinct() or groupBy() without prior filtering."
        ]
        
        # 2. Metadata Harvester (Simulated extraction from Hive/Glue)
        self.catalog = [
            Document(page_content="Table: default.sales\nDescription: Transactions of users.\nColumns: transaction_id (string), user_id (string), amount (double)\nPartition Keys: event_date (date)"),
            Document(page_content="Table: default.users\nDescription: User profiles.\nColumns: user_id (string), name (string), signup_date (date), country (string)\nProperties: Small dimension table (< 5MB)"),
            Document(page_content="Table: default.web_logs\nDescription: Clickstream data.\nColumns: session_id (string), user_id (string), url (string)\nPartition Keys: event_date (date)")
        ]
        
        # 3. Vectorized Context (ChromaDB)
        # Embeds the catalog into an ephemeral in-memory Chroma instance for RAG
        self.embeddings = llm_service.get_embeddings()
        self.vector_store = Chroma.from_documents(
            documents=self.catalog, 
            embedding=self.embeddings,
            collection_name="hive_metastore_catalog"
        )

    def get_context(self, query: str, k: int = 2) -> str:
        """Retrieve relevant tables using Vector Search and inject constraints."""
        if not query:
            return "No specific query provided to retrieve schema."

        # Retrieve top K most relevant table schemas based on user query
        docs = self.vector_store.similarity_search(query, k=k)
        
        table_schemas = "\n\n".join([doc.page_content for doc in docs])
        rules = "\n".join([f"- {rule}" for rule in self.golden_rules])
        
        return (
            "--- RELEVANT HIVE/GLUE TABLE SCHEMAS ---\n"
            f"{table_schemas}\n\n"
            "--- DATA ENGINEERING GOLDEN RULES (MANDATORY) ---\n"
            f"{rules}"
        )

# Singleton instance for the application
semantic_layer = SemanticLayer()