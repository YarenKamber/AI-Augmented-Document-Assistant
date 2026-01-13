import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity

class VectorStore:
    def __init__(self):
        """
        Initialize the VectorStore using in-memory Numpy arrays + List storage.
        """
        # Metadata storage: List of dicts
        self.chunks: List[Dict[str, Any]] = []
        
        # Vector storage: Numpy matrix (N_chunks, Embedding_Dim)
        self.embeddings_matrix: Optional[np.ndarray] = None

    def add_document(self, doc_id: str, filename: str, chunks: List[str], embeddings: List[List[float]]) -> None:
        """
        Adds document chunks and their corresponding embeddings to the store.
        
        Args:
            doc_id (str): Unique document ID.
            filename (str): Name of source file.
            chunks (List[str]): List of text chunks.
            embeddings (List[List[float]]): List of embedding vectors corresponding to chunks.
        """
        if not chunks or not embeddings:
            return
            
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match.")

        # 1. Update Metadata
        start_index = len(self.chunks)
        for i, text in enumerate(chunks):
            self.chunks.append({
                "doc_id": doc_id,
                "filename": filename,
                "chunk_index": i,
                "chunk_text": text,
                "global_index": start_index + i
            })

        # 2. Update Embeddings Matrix
        new_vecs = np.array(embeddings, dtype='float32')
        
        if self.embeddings_matrix is None:
            self.embeddings_matrix = new_vecs
        else:
            self.embeddings_matrix = np.vstack([self.embeddings_matrix, new_vecs])

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Finds the top_k most similar chunks to the query_embedding.
        
        Args:
            query_embedding (List[float]): The embedding vector of the user's question.
            top_k (int): Number of results to return.
            
        Returns:
            List[Dict]: List of result chunks with scores.
        """
        if self.embeddings_matrix is None or len(self.chunks) == 0:
            return []

        # Ensure query is 2D array (1, Dim) for scikit-learn
        query_vec = np.array([query_embedding], dtype='float32')
        
        # Calculate Cosine Similarity: Returns (1, N_chunks) array of scores
        # Values range from -1 to 1 (1 being identical)
        similarity_scores = cosine_similarity(query_vec, self.embeddings_matrix)[0]
        
        # Get indices of top_k scores (sorted descending)
        # argsort gives ascending, so we slice from end [::-1]
        top_indices = np.argsort(similarity_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = similarity_scores[idx]
            
            # Create a copy of the chunk data to avoid mutating store
            result_item = self.chunks[idx].copy()
            result_item['score'] = float(score)  # Convert numpy float to native float
            results.append(result_item)
            
        return results

    def save(self, dir_path: str) -> None:
        """
        Persist store to disk (JSON for metadata, NPY for vectors).
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            
        # 1. Save Metadata
        meta_path = os.path.join(dir_path, "metadata.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
            
        # 2. Save Vectors
        if self.embeddings_matrix is not None:
            vec_path = os.path.join(dir_path, "vectors.npy")
            np.save(vec_path, self.embeddings_matrix)

    def load(self, dir_path: str) -> None:
        """
        Load store from disk.
        """
        meta_path = os.path.join(dir_path, "metadata.json")
        vec_path = os.path.join(dir_path, "vectors.npy")
        
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
                
        if os.path.exists(vec_path):
            self.embeddings_matrix = np.load(vec_path)
