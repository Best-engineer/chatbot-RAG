RAG 기반 챗봇 프로젝트

### 📝 프로젝트 개요

이 프로젝트는 RAG(Retrieval-Augmented Generation) 기술을 활용하여 정확하고 최신 정보를 제공하는 챗봇을 구축합니다. 미리 준비된 지식 문서에서 관련 정보를 검색하여, LLM(Large Language Model)이 답변을 생성하는 방식으로 동작합니다.

### ✨ 주요 기능

- **문서 기반 답변**: 사용자 질문에 대해 특정 문서에서 검색된 정보를 바탕으로 답변합니다.
- **환각(Hallucination) 감소**: LLM이 사실과 다른 내용을 생성하는 문제를 최소화합니다.
- **최신 정보 활용**: 모델 학습 시점 이후의 새로운 문서 내용을 반영할 수 있습니다.
- **출처 투명성**: 답변의 근거가 되는 문서 출처를 제공하여 신뢰성을 높입니다.

### 🛠️ 기술 스택

- **언어**: Python
- **프레임워크/라이브러리**: LangChain
- **임베딩 모델**: OpenAIEmbeddings
- **벡터 데이터베이스**: FAISS 또는 ChromaDB (선택 가능)
- **LLM**: OpenAI GPT 모델

### 🚀 설치 및 실행 방법

1.  **환경 설정**:

    ```bash
    git clone [레포지토리 URL]
    cd [레포지토리 이름]
    pip install -r requirements.txt
    ```

2.  **문서 준비**:
    `your_document.txt` 파일에 챗봇이 학습할 문서를 넣어주세요.

3.  **코드 실행**:
    ```bash
    python main.py
    ```
