import os
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from docx import Document
import logging

from .config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentLoader:
    """다양한 파일 형식을 텍스트로 변환하는 로더"""
    
    def __init__(self, upload_folder: str = UPLOAD_FOLDER):
        self.upload_folder = Path(upload_folder)
        
    def load_documents(self, file_paths: List[str] = None) -> List[Dict[str, Any]]:
        """여러 문서를 로드하여 텍스트로 변환"""
        documents = []
        
        if file_paths is None:
            # data 폴더의 모든 파일 로드
            file_paths = self._get_all_files()
        
        for file_path in file_paths:
            try:
                text = self._load_single_document(file_path)
                if text:
                    documents.append({
                        'file_path': file_path,
                        'content': text,
                        'file_type': Path(file_path).suffix.lower()
                    })
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                
        return documents
    
    def _get_all_files(self) -> List[str]:
        """data 폴더의 모든 허용된 파일 반환"""
        files = []
        for ext in ALLOWED_EXTENSIONS:
            files.extend(self.upload_folder.glob(f"*.{ext}"))
        return [str(f) for f in files]
    
    def _load_single_document(self, file_path: str) -> str:
        """단일 문서를 텍스트로 변환"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self._load_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self._load_docx(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            return self._load_excel(file_path)
        elif file_extension == '.csv':
            return self._load_csv(file_path)
        elif file_extension == '.txt':
            return self._load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _load_pdf(self, file_path: Path) -> str:
        """PDF 파일을 텍스트로 변환"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
        return text.strip()
    
    def _load_docx(self, file_path: Path) -> str:
        """DOCX 파일을 텍스트로 변환"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {e}")
        return text.strip()
    
    def _load_excel(self, file_path: Path) -> str:
        """Excel 파일을 텍스트로 변환"""
        text = ""
        try:
            df = pd.read_excel(file_path)
            text = df.to_string(index=False)
        except Exception as e:
            logger.error(f"Error reading Excel {file_path}: {e}")
        return text.strip()
    
    def _load_csv(self, file_path: Path) -> str:
        """CSV 파일을 텍스트로 변환"""
        text = ""
        try:
            df = pd.read_csv(file_path)
            text = df.to_string(index=False)
        except Exception as e:
            logger.error(f"Error reading CSV {file_path}: {e}")
        return text.strip()
    
    def _load_txt(self, file_path: Path) -> str:
        """텍스트 파일을 읽기"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error reading TXT {file_path}: {e}")
            return "" 