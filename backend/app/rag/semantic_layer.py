from langchain_weaviate.vectorstores import WeaviateVectorStore

from app.services.llm_service import llm_service
from app.services.weaviate_service import weaviate_service


class SemanticLayer:
    def __init__(self):
        # 1. Constraint Engine: Golden Rules
        self.golden_rules = [
            "PREDICATE PUSHDOWN: Always filter by partition columns (e.g., 'event_date', 'year', 'month') BEFORE joining.",
            "BROADCAST JOINS: Use F.broadcast() for dimension tables under 10MB.",
            "COLUMN PRUNING: Select only required columns before applying transformations or joins.",
            "AVOID SHUFFLES: Minimize distinct() or groupBy() without prior filtering.",
        ]

        # 2. Vectorized Context (WeaviateDB) - Read Only Connection
        self.embeddings = llm_service.get_embeddings()

        client = weaviate_service.get_client()

        self.vector_store = WeaviateVectorStore(
            client=client,
            embedding=self.embeddings,
            index_name="HiveMetastoreCatalog",
            text_key="text",
        )

    def get_context(
        self, query: str, k: int = 10, database_schemas: list[str] = None
    ) -> str:
        """
        Retrieve relevant tables using Vector Search and inject constraints.
        Optionally pre-filters the vector database by a list of Hive schema/database names.
        """
        if not query:
            return "No specific query provided to retrieve schema."

        search_kwargs = {"k": k}

        # If the user's query is targeted at specific schemas, filter Weaviate metadata
        if database_schemas:
            from weaviate.classes.query import Filter

            search_kwargs["filters"] = Filter.by_property("database").contains_any(
                database_schemas
            )

        # Retrieve top K most relevant table schemas
        docs = self.vector_store.similarity_search(query, **search_kwargs)

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
