import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorMemory:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.IndexFlatL2(384)
        self.texts = []

    def add(self, text: str):
        embedding = self.model.encode([text])
        self.index.add(np.array(embedding).astype("float32"))
        self.texts.append(text)

    def search(self, query: str, k: int = 3):
        if not self.texts:
            return []

        query_embedding = self.model.encode([query])
        _, indices = self.index.search(
            np.array(query_embedding).astype("float32"),
            k
        )
        return [self.texts[i] for i in indices[0]]
