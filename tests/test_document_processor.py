import unittest
import os
from modules.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor()
        # Create a dummy text file
        self.test_file_path = "test_doc.txt"
        with open(self.test_file_path, "w") as f:
            f.write("Hello World. This is a test document.\n" * 10)

    def tearDown(self):
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_chunk_text_basic(self):
        text = "1234567890"
        # chunk size 4, overlap 0 -> "1234", "5678", "90"
        chunks = self.processor.chunk_text(text, chunk_size=4, overlap=0)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], "1234")
        self.assertEqual(chunks[2], "90")

    def test_chunk_text_overlap(self):
        text = "123456"
        # chunk size 4, overlap 2 -> "1234", "3456"
        chunks = self.processor.chunk_text(text, chunk_size=4, overlap=2)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], "1234")
        self.assertEqual(chunks[1], "3456")

    def test_extract_txt(self):
        doc = self.processor.build_document(self.test_file_path)
        self.assertTrue(len(doc.text) > 0)
        self.assertEqual(doc.filename, "test_doc.txt")
        self.assertTrue("Hello World" in doc.text)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.processor.build_document("non_existent_file.pdf")

    def test_unsupported_extension(self):
        bad_file = "test.xyz"
        with open(bad_file, "w") as f:
            f.write("content")
        try:
            with self.assertRaises(ValueError):
                self.processor.build_document(bad_file)
        finally:
            if os.path.exists(bad_file):
                os.remove(bad_file)

if __name__ == '__main__':
    unittest.main()
