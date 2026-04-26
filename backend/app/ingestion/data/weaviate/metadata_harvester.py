import glob
import json
import os

import structlog
from langchain_core.documents import Document
from langchain_weaviate.vectorstores import WeaviateVectorStore

from app.services.llm_service import llm_service
from app.services.weaviate_service import weaviate_service

logger = structlog.get_logger(__name__)


class MetadataHarvester:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.embeddings = llm_service.get_embeddings()
        self.client = weaviate_service.get_client()
        self.index_name = "HiveMetastoreCatalog"

    def _load_json_files(self) -> list[dict]:
        """Recursively load all JSON files in the target directory."""
        tables = []
        search_pattern = os.path.join(self.data_dir, "**/*.json")
        files = glob.glob(search_pattern, recursive=True)

        for file_path in files:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    # Support both {"tables": [...]} format and raw [...] list formats
                    if isinstance(data, dict) and "tables" in data:
                        tables.extend(data["tables"])
                    elif isinstance(data, list):
                        tables.extend(data)
            except Exception as e:
                logger.error("failed_to_load_file", file=file_path, error=str(e))

        return tables

    def _create_documents(self, tables: list[dict]) -> list[Document]:
        """Convert raw dictionaries into LangChain Documents with tuned Metadata."""
        docs = []
        for table in tables:
            database = table.get("database", "default")
            table_name = table.get("name", "unknown")
            description = table.get("description", "")

            # Format structural arrays into LLM-friendly text
            columns = table.get("columns", [])
            cols_str = ", ".join(
                [f"{c.get('name')} ({c.get('type')})" for c in columns]
            )

            partitions = table.get("partition_keys", [])
            parts_str = ", ".join(partitions) if partitions else "None"

            # 1. Semantic Payload (What the AI reads & searches against)
            page_content = (
                f"Database Schema: {database}\n"
                f"Table Name: {table_name}\n"
                f"Description: {description}\n"
                f"Columns: {cols_str}\n"
                f"Partition Keys: {parts_str}"
            )

            # 2. Structural Payload (What Weaviate uses for hard-filtering)
            metadata = {
                "database": database,
                "table": table_name,
                "size": table.get("size", "unknown"),
            }

            docs.append(Document(page_content=page_content, metadata=metadata))
        return docs

    def run(self):
        """Extracts metadata from JSONs and ingests it into Weaviate."""
        logger.info("harvester_started", data_dir=self.data_dir)

        tables = self._load_json_files()
        if not tables:
            logger.warning("no_tables_found", data_dir=self.data_dir)
            return

        docs = self._create_documents(tables)
        logger.info("documents_created", count=len(docs))

        # Clear the index to prevent duplicates on re-runs
        if self.client.collections.exists(self.index_name):
            logger.info("dropping_existing_collection", index=self.index_name)
            self.client.collections.delete(self.index_name)

        logger.info("ingesting_to_weaviate", count=len(docs), index=self.index_name)
        WeaviateVectorStore.from_documents(
            documents=docs,
            embedding=self.embeddings,
            client=self.client,
            index_name=self.index_name,
        )
        logger.info("harvester_completed")


def run_harvester():
    # Target the 'data' directory relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")

    harvester = MetadataHarvester(data_dir=data_dir)
    harvester.run()


if __name__ == "__main__":
    run_harvester()
