#!/usr/bin/env python3
"""
LLM Chatbot Main Application
문서를 로드하고 벡터 DB에 저장한 후, 챗봇과 대화할 수 있는 메인 애플리케이션
"""

import os
import sys
import logging
from pathlib import Path

# src 모듈 import를 위한 경로 추가
sys.path.append(str(Path(__file__).parent / "src"))

from src.loader import DocumentLoader
from src.embedding import DocumentEmbedder
from src.search import ChatbotSearch
from src.config import UPLOAD_FOLDER

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMChatbot:
    """LLM 챗봇 메인 클래스"""
    
    def __init__(self):
        self.loader = DocumentLoader()
        self.embedder = DocumentEmbedder()
        self.search = ChatbotSearch(self.embedder)
        self.conversation_history = []
    
    def load_and_embed_documents(self, file_paths: list = None):
        """문서를 로드하고 벡터 DB에 저장"""
        logger.info("문서 로딩 시작...")
        
        # 문서 로드
        documents = self.loader.load_documents(file_paths)
        
        if not documents:
            logger.warning("로드할 문서가 없습니다.")
            return False
        
        logger.info(f"{len(documents)}개의 문서를 로드했습니다.")
        
        # 벡터 DB에 저장
        logger.info("벡터 DB에 임베딩 시작...")
        self.embedder.embed_documents(documents)
        
        # 컬렉션 정보 출력
        info = self.embedder.get_collection_info()
        logger.info(f"벡터 DB 정보: {info}")
        
        return True
    
    def chat(self, query: str) -> str:
        """챗봇과 대화"""
        if not query.strip():
            return "질문을 입력해주세요."
        
        logger.info(f"사용자 질문: {query}")
        
        # 응답 생성
        response = self.search.search_and_respond(query)
        
        # 대화 히스토리에 추가
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # 히스토리가 너무 길어지면 앞부분 제거
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        return response
    
    def get_relevant_docs(self, query: str):
        """쿼리와 관련된 문서들 반환 (디버깅용)"""
        return self.search.get_relevant_documents(query)
    
    def clear_database(self):
        """벡터 DB 초기화"""
        self.embedder.clear_collection()
        logger.info("벡터 DB가 초기화되었습니다.")

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("LLM Chatbot - 문서 기반 챗봇")
    print("=" * 50)
    
    chatbot = LLMChatbot()
    
    # 문서 로드 및 임베딩
    print("\n1. 문서 로딩 및 벡터 DB 구축...")
    success = chatbot.load_and_embed_documents()
    
    if not success:
        print("문서 로딩에 실패했습니다. data 폴더에 문서를 추가해주세요.")
        return
    
    print("\n2. 챗봇과 대화를 시작합니다.")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("-" * 50)
    
    # 대화 루프
    while True:
        try:
            query = input("\n질문: ").strip()
            
            if query.lower() in ['quit', 'exit', '종료']:
                print("챗봇을 종료합니다.")
                break
            
            if not query:
                continue
            
            # 응답 생성
            response = chatbot.chat(query)
            print(f"\n답변: {response}")
            
        except KeyboardInterrupt:
            print("\n\n챗봇을 종료합니다.")
            break
        except Exception as e:
            logger.error(f"오류 발생: {e}")
            print("오류가 발생했습니다. 다시 시도해주세요.")

def interactive_mode():
    """대화형 모드 - 문서 로딩 없이 바로 대화"""
    print("=" * 50)
    print("LLM Chatbot - 대화형 모드")
    print("=" * 50)
    
    chatbot = LLMChatbot()
    
    # 기존 벡터 DB 확인
    info = chatbot.embedder.get_collection_info()
    if info['document_count'] == 0:
        print("벡터 DB에 문서가 없습니다. 먼저 문서를 로드해주세요.")
        return
    
    print(f"벡터 DB에 {info['document_count']}개의 문서 청크가 저장되어 있습니다.")
    print("\n챗봇과 대화를 시작합니다.")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("-" * 50)
    
    # 대화 루프
    while True:
        try:
            query = input("\n질문: ").strip()
            
            if query.lower() in ['quit', 'exit', '종료']:
                print("챗봇을 종료합니다.")
                break
            
            if not query:
                continue
            
            # 응답 생성
            response = chatbot.chat(query)
            print(f"\n답변: {response}")
            
        except KeyboardInterrupt:
            print("\n\n챗봇을 종료합니다.")
            break
        except Exception as e:
            logger.error(f"오류 발생: {e}")
            print("오류가 발생했습니다. 다시 시도해주세요.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM Chatbot")
    parser.add_argument("--interactive", action="store_true", 
                       help="대화형 모드 (문서 로딩 없이 바로 대화)")
    parser.add_argument("--clear-db", action="store_true",
                       help="벡터 DB 초기화")
    
    args = parser.parse_args()
    
    if args.clear_db:
        chatbot = LLMChatbot()
        chatbot.clear_database()
        print("벡터 DB가 초기화되었습니다.")
    elif args.interactive:
        interactive_mode()
    else:
        main() 