import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 벡터 DB 설정
CHROMA_PERSIST_DIRECTORY = "db/chroma"
CHROMA_COLLECTION_NAME = "documents"

# 파일 업로드 설정
UPLOAD_FOLDER = "data"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'xls', 'csv'}

# LLM 설정
MODEL_NAME = "gpt-3.5-turbo"
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# 검색 설정
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7 