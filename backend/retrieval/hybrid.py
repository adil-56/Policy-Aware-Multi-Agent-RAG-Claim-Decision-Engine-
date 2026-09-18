from typing import List, Dict, Any
import numpy as np
from rank_bm25 import BM25Okapi
import chromadb
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from flashrank import Ranker, RerankRequest
from backend.core.config import settings
from backend.core.exceptions import RetrievalException
from backend.models.state import EvidenceItem, Citation
import logging

logger = logging.getLogger(__name__)

class HybridRetriever:
    """
    Implements a Hybrid Retrieval Engine:
    1. Dense Vector Search (ChromaDB + OpenAI)
    2. Sparse Keyword Search (BM25)
    3. Reciprocal Rank Fusion (RRF)
    """
    def __init__(self, persist_directory: str = settings.CHROMA_PERSIST_DIRECTORY):
        self.embeddings = FastEmbedEmbeddings()
        # Initialize a lightweight, free ONNX CPU reranker
        self.ranker = Ranker()
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.chroma_client.get_or_create_collection(name="policy_chunks")
        
        # BM25 internal state (in-memory for this implementation)
        self.corpus: List[Dict[str, Any]] = []
        self.bm25: BM25Okapi = None

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Adds documents to Chroma and rebuilds the BM25 index."""
        if not documents:
            return
            
        ids = [doc["chunk_id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = [{"page": doc["page"], "source": doc["source"], "section": doc.get("section", "Unknown")} for doc in documents]
        
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        
        self.corpus.extend(documents)
        tokenized_corpus = [doc["text"].lower().split() for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info(f"Added {len(documents)} documents to HybridRetriever.")

    def _dense_search(self, query: str, k: int = 15) -> List[Dict[str, Any]]:
        query_embedding = self.embeddings.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        docs = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                docs.append({
                    "chunk_id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "dense_score": results['distances'][0][i]  # L2 distance
                })
        return docs

    def _sparse_search(self, query: str, k: int = 15) -> List[Dict[str, Any]]:
        if not self.bm25:
            return []
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        top_n = np.argsort(scores)[::-1][:k]
        
        docs = []
        for idx in top_n:
            if scores[idx] > 0:
                doc = self.corpus[idx]
                docs.append({
                    "chunk_id": doc["chunk_id"],
                    "text": doc["text"],
                    "metadata": {"page": doc["page"], "source": doc["source"], "section": doc.get("section", "Unknown")},
                    "sparse_score": float(scores[idx])
                })
        return docs
        
    def _reciprocal_rank_fusion(self, dense_results: List[Dict], sparse_results: List[Dict], k: int = 60) -> List[Dict]:
        """Fuses dense and sparse results using RRF (Reciprocal Rank Fusion)."""
        rrf_scores = {}
        docs_dict = {}
        
        def _add_to_rrf(results):
            for rank, doc in enumerate(results):
                doc_id = doc["chunk_id"]
                docs_dict[doc_id] = doc
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = 0.0
                rrf_scores[doc_id] += 1.0 / (k + rank + 1)

        _add_to_rrf(dense_results)
        _add_to_rrf(sparse_results)
        
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        return [docs_dict[doc_id] for doc_id in sorted_ids]

    def retrieve(self, query: str, top_k: int = 5) -> List[EvidenceItem]:
        """
        Executes Hybrid retrieval: Dense + BM25 -> RRF -> Return top_k.
        Returns typed EvidenceItem objects.
        """
        try:
            dense_res = self._dense_search(query, k=15)
            sparse_res = self._sparse_search(query, k=15)
            
            fused = self._reciprocal_rank_fusion(dense_res, sparse_res)
            if not fused:
                return []
                
            # Rerank the fused results using FlashRank
            passages = []
            for doc in fused:
                passages.append({
                    "id": doc["chunk_id"],
                    "text": doc["text"],
                    "meta": doc["metadata"]
                })
                
            request = RerankRequest(query=query, passages=passages)
            reranked_results = self.ranker.rerank(request)
            
            # reranked_results is a list of dicts sorted by relevance, with a "score" key
            final_top = reranked_results[:top_k]
            
            evidence_items = []
            for doc in final_top:
                citation = Citation(
                    page=doc["meta"].get("page", "Unknown"),
                    section=doc["meta"].get("section", "Unknown"),
                    chunk_id=doc["id"],
                    source=doc["meta"].get("source", "Unknown"),
                    text=doc["text"]
                )
                evidence_items.append(EvidenceItem(
                    category="HybridSearch",
                    content=doc["text"],
                    citation=citation,
                    relevance_score=float(doc["score"])
                ))
            return evidence_items
            
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            raise RetrievalException(f"Hybrid retrieval failed: {str(e)}")
