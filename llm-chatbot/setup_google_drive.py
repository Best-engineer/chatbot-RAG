#!/usr/bin/env python3
"""
Google Drive API 설정 스크립트
교육 과정 데이터를 Google Drive에서 자동으로 동기화하는 설정
"""

import os
import json
from pathlib import Path
from src.gdrive_sync import GoogleDriveSync
from src.loader import DocumentLoader
from src.embedding import DocumentEmbedder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_google_drive():
    """Google Drive API 설정 및 데이터 동기화"""
    
    print("=" * 50)
    print("Google Drive API 설정")
    print("=" * 50)
    
    # 1. credentials.json 파일 확인
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json 파일이 없습니다.")
        print("다음 단계를 따라주세요:")
        print("1. Google Cloud Console에서 프로젝트 생성")
        print("2. Google Drive API 활성화")
        print("3. 서비스 계정 키 생성 및 다운로드")
        print("4. credentials.json 파일을 프로젝트 루트에 배치")
        return False
    
    print("✅ credentials.json 파일 확인됨")
    
    # 2. Google Drive 폴더 ID 입력
    folder_id = input("Google Drive 폴더 ID를 입력하세요: ").strip()
    
    if not folder_id:
        print("❌ 폴더 ID가 필요합니다.")
        return False
    
    try:
        # 3. Google Drive 동기화
        print("\n📁 Google Drive에서 파일 동기화 중...")
        gdrive = GoogleDriveSync()
        files = gdrive.sync_folder(folder_id)
        
        if files:
            print(f"✅ {len(files)}개의 파일을 동기화했습니다:")
            for file in files:
                print(f"  - {file}")
        else:
            print("❌ 동기화할 파일이 없습니다.")
            return False
        
        # 4. 문서 로드 및 벡터 DB 구축
        print("\n📚 문서 로딩 및 벡터 DB 구축 중...")
        loader = DocumentLoader()
        embedder = DocumentEmbedder()
        
        documents = loader.load_documents()
        
        if documents:
            embedder.embed_documents(documents)
            info = embedder.get_collection_info()
            print(f"✅ 벡터 DB 구축 완료: {info['document_count']}개 청크")
        else:
            print("❌ 로드할 문서가 없습니다.")
            return False
        
        print("\n🎉 Google Drive 연동 설정이 완료되었습니다!")
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def test_chatbot():
    """챗봇 테스트"""
    print("\n" + "=" * 50)
    print("챗봇 테스트")
    print("=" * 50)
    
    from src.search import ChatbotSearch
    from src.embedding import DocumentEmbedder
    
    embedder = DocumentEmbedder()
    search = ChatbotSearch(embedder)
    
    # 테스트 질문들
    test_questions = [
        "머신러닝 과정이 있나요?",
        "데이터 사이언스 과정의 커리큘럼을 알려주세요",
        "Python 프로그래밍 과정의 수강료는 얼마인가요?",
        "온라인 강의도 제공하나요?"
    ]
    
    for question in test_questions:
        print(f"\n질문: {question}")
        response = search.search_and_respond(question)
        print(f"답변: {response}")
        print("-" * 50)

if __name__ == "__main__":
    success = setup_google_drive()
    
    if success:
        test_chatbot()
    else:
        print("\n설정을 완료한 후 다시 실행해주세요.") 