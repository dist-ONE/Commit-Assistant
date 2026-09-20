import os
import chromadb
from chromadb.utils import embedding_functions
from typing import cast
from chromadb.api.types import EmbeddingFunction

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'chroma_db')

class CommitMemory:
    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        
        self.embedding_fn = embedding_functions.OllamaEmbeddingFunction(
            url="http://localhost:11434/api/embeddings",
            model_name="nomic-embed-text"
        )
        
        self.client = chromadb.PersistentClient(path=DB_PATH)
        
        self.embedding_fn = cast(
            EmbeddingFunction, 
            embedding_functions.OllamaEmbeddingFunction(
                url="http://localhost:11434/api/embeddings",
                model_name="nomic-embed-text"
            )
        )
        
        self.collection = self.client.get_or_create_collection(
            name=f"commits_{repo_name.replace('-', '_')}",
            embedding_function=self.embedding_fn
        )

    def save_commit(self, diff: str, commit_message: str, commit_hash: str):
        """
        Embeds and saves a successful commit into the vector database.
        """

        self.collection.add(
            documents=[diff],
            metadatas=[{"message": commit_message}],
            ids=[commit_hash]
        )
        print(f"Stored commit in semantic memory.")

    def get_similar_commits(self, new_diff: str, n_results: int = 3) -> list[str]:
        """
        Queries the vector database for the most similar past diffs.
        """
        
        if self.collection.count() == 0:
            return []
        
        results = self.collection.query(
            query_texts=[new_diff],
            n_results=min(n_results, self.collection.count())
        )
        
        past_messages = []
        if results['metadatas'] and results['metadatas'][0]:
            for metadata in results['metadatas'][0]:
                past_messages.append(metadata["message"])
                
        return past_messages