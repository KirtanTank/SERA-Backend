import faiss
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer

VECTOR_DIR = "data/vector_memory"
INDEX_FILE = f"{VECTOR_DIR}/index.faiss"
TEXT_FILE = f"{VECTOR_DIR}/texts.pkl"


class VectorMemory:
    def __init__(self, user_id: str):
        VECTOR_DIR = f"data/vector_memory/{user_id}"
        os.makedirs(VECTOR_DIR, exist_ok=True)

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        if os.path.exists(INDEX_FILE) and os.path.exists(TEXT_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(TEXT_FILE, "rb") as f:
                self.texts = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(384)
            self.texts = []

    def _persist(self):
        faiss.write_index(self.index, INDEX_FILE)
        with open(TEXT_FILE, "wb") as f:
            pickle.dump(self.texts, f)

    def add(self, text: str):
        embedding = self.model.encode([text])
        self.index.add(np.array(embedding).astype("float32"))
        if text in self.texts:
            return
        self.texts.append(text)
        self._persist()

    def search(self, query: str, k: int = 3):
        if not self.texts:
            return []

        query_embedding = self.model.encode([query])
        _, indices = self.index.search(
            np.array(query_embedding).astype("float32"), min(k, len(self.texts))
        )

        return [self.texts[i] for i in indices[0]]
