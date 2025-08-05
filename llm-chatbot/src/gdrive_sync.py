import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import logging
from typing import List, Dict, Any
from pathlib import Path

from .config import GOOGLE_API_KEY, UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleDriveSync:
    """Google Drive와 동기화하는 클래스"""
    
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Google Drive API 인증"""
        creds = None
        
        # 토큰 파일이 있으면 로드
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # 유효한 인증 정보가 없으면 새로 생성
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 토큰 저장
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        logger.info("Google Drive API 인증 완료")
    
    def list_files(self, folder_id: str = None) -> List[Dict[str, Any]]:
        """Google Drive의 파일 목록 조회"""
        try:
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files in Google Drive")
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def download_file(self, file_id: str, filename: str = None) -> bool:
        """Google Drive에서 파일 다운로드"""
        try:
            # 파일 정보 가져오기
            file_metadata = self.service.files().get(fileId=file_id).execute()
            
            if not filename:
                filename = file_metadata['name']
            
            # 다운로드 경로 설정
            download_path = Path(UPLOAD_FOLDER) / filename
            
            # 파일 다운로드
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f"Download {int(status.progress() * 100)}%")
            
            # 파일 저장
            with open(download_path, 'wb') as f:
                f.write(fh.getvalue())
            
            logger.info(f"Downloaded {filename} to {download_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            return False
    
    def sync_folder(self, folder_id: str) -> List[str]:
        """폴더의 모든 파일을 동기화"""
        downloaded_files = []
        
        try:
            files = self.list_files(folder_id)
            
            for file in files:
                if file['mimeType'] != 'application/vnd.google-apps.folder':
                    success = self.download_file(file['id'], file['name'])
                    if success:
                        downloaded_files.append(file['name'])
            
            logger.info(f"Synced {len(downloaded_files)} files from Google Drive")
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Error syncing folder: {e}")
            return []
    
    def search_files(self, query: str) -> List[Dict[str, Any]]:
        """Google Drive에서 파일 검색"""
        try:
            results = self.service.files().list(
                q=f"name contains '{query}' and trashed=false",
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files matching '{query}'")
            return files
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """파일 정보 조회"""
        try:
            file_info = self.service.files().get(fileId=file_id).execute()
            return file_info
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {} 