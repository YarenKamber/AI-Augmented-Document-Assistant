import unittest
import numpy as np
from modules.vector_store import VectorStore

class TestVectorStore(unittest.TestCase):
    def setUp(self):
        self.store = VectorStore()

    def test_add_and_search(self):
        chunks = ["This is a test document.", "Another chunk."]
        # Mock embeddings: 2 chunks, 4 dimensions
        embeddings = [
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8]
        ]
        
        self.store.add_document("doc1", "test.txt", chunks, embeddings)
        
        # Check chunks were added
        self.assertTrue(len(self.store.chunks) == 2)
        
        # Test Search
        query_vec = [0.1, 0.2, 0.3, 0.4] # Matches first chunk exactly
        results = self.store.search(query_vec, top_k=1)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['doc_id'], "doc1")
        self.assertEqual(results[0]['chunk_text'], "This is a test document.")
        
if __name__ == '__main__':
    unittest.main()
