import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

from .config import CHROMA_PERSIST_DIRECTORY, CHROMA_COLLECTION_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentEmbedder:
    """문서를 벡터로 변환하고 ChromaDB에 저장하는 클래스"""
    
    def __init__(self, persist_directory: str = CHROMA_PERSIST_DIRECTORY):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self._get_or_create_collection()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def _get_or_create_collection(self):
        """컬렉션을 가져오거나 생성"""
        try:
            collection = self.client.get_collection(CHROMA_COLLECTION_NAME)
            logger.info(f"Using existing collection: {CHROMA_COLLECTION_NAME}")
        except:
            collection = self.client.create_collection(CHROMA_COLLECTION_NAME)
            logger.info(f"Created new collection: {CHROMA_COLLECTION_NAME}")
        return collection
    
    def embed_documents(self, documents: List[Dict[str, Any]]) -> None:
        """문서들을 임베딩하여 벡터 DB에 저장"""
        if not documents:
            logger.warning("No documents to embed")
            return
            
        texts = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(documents):
            # 긴 텍스트를 청크로 분할
            chunks = self._split_text(doc['content'])
            
            for j, chunk in enumerate(chunks):
                chunk_id = f"{doc['file_path']}_{i}_{j}"
                texts.append(chunk)
                metadatas.append({
                    'file_path': doc['file_path'],
                    'file_type': doc['file_type'],
                    'chunk_index': j,
                    'total_chunks': len(chunks)
                })
                ids.append(chunk_id)
        
        # 벡터 DB에 저장
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Embedded {len(texts)} text chunks from {len(documents)} documents")
    
    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """텍스트를 청크로 분할"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # 문장 경계에서 분할
            if end < len(text):
                # 마지막 마침표나 줄바꿈을 찾아서 분할
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                split_point = max(last_period, last_newline)
                
                if split_point > start:
                    end = split_point + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """쿼리와 유사한 문서 검색"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        documents = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return documents
    
    def get_collection_info(self) -> Dict[str, Any]:
        """컬렉션 정보 반환"""
        count = self.collection.count()
        return {
            'collection_name': CHROMA_COLLECTION_NAME,
            'document_count': count,
            'persist_directory': self.persist_directory
        }
    
    def clear_collection(self) -> None:
        """컬렉션의 모든 데이터 삭제"""
        self.client.delete_collection(CHROMA_COLLECTION_NAME)
        self.collection = self._get_or_create_collection()
        logger.info("Collection cleared") 