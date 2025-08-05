import openai
from typing import List, Dict, Any
import logging
from .config import OPENAI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE, TOP_K_RESULTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotSearch:
    """검색 및 LLM 응답 처리를 담당하는 클래스"""
    
    def __init__(self, embedder):
        self.embedder = embedder
        openai.api_key = OPENAI_API_KEY
        
    def search_and_respond(self, query: str, top_k: int = TOP_K_RESULTS) -> str:
        """쿼리를 검색하고 LLM으로 응답 생성"""
        try:
            # 유사한 문서 검색
            similar_docs = self.embedder.search_similar(query, top_k)
            
            if not similar_docs:
                return "죄송합니다. 관련된 교육 과정 정보를 찾을 수 없습니다. 다른 질문을 해주시거나 상담원에게 문의해주세요."
            
            # 컨텍스트 구성
            context = self._build_context(similar_docs)
            
            # LLM 응답 생성
            response = self._generate_response(query, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in search_and_respond: {e}")
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def _build_context(self, similar_docs: List[Dict[str, Any]]) -> str:
        """검색된 문서들을 컨텍스트로 구성"""
        context_parts = []
        
        for i, doc in enumerate(similar_docs, 1):
            content = doc['content']
            metadata = doc['metadata']
            
            # 문서 정보 추가
            context_part = f"[교육 자료 {i} - {metadata.get('file_path', 'Unknown')}]\n{content}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _generate_response(self, query: str, context: str) -> str:
        """OpenAI API를 사용하여 교육 서비스 특화 응답 생성"""
        try:
            system_prompt = f"""당신은 교육 서비스 회사의 공손하고 전문적인 상담원입니다. 
다음 교육 과정 정보를 기반으로 고객의 질문에 답변해주세요.

**응답 스타일:**
- 공손하고 친절한 톤으로 답변
- "~입니다", "~하시면 됩니다" 등의 존댓말 사용
- 교육 과정 정보가 없으면 "해당 정보는 현재 제공되지 않습니다"라고 답변
- 가능하면 구체적인 과정명, 커리큘럼, 수강료, 기간 등을 포함
- 추가 문의사항이 있으면 언제든 연락주시라고 안내

**교육 과정 정보:**
{context}

**고객 질문:** {query}

**답변:**"""

            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "죄송합니다. 응답 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def get_relevant_documents(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict[str, Any]]:
        """쿼리와 관련된 문서들 반환 (디버깅용)"""
        return self.embedder.search_similar(query, top_k)
    
    def chat_with_history(self, query: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """대화 히스토리를 고려한 채팅"""
        if conversation_history is None:
            conversation_history = []
        
        try:
            # 유사한 문서 검색
            similar_docs = self.embedder.search_similar(query, TOP_K_RESULTS)
            
            if not similar_docs:
                return "죄송합니다. 관련된 교육 과정 정보를 찾을 수 없습니다. 다른 질문을 해주시거나 상담원에게 문의해주세요."
            
            # 컨텍스트 구성
            context = self._build_context(similar_docs)
            
            # 대화 히스토리와 함께 응답 생성
            response = self._generate_response_with_history(query, context, conversation_history)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat_with_history: {e}")
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def _generate_response_with_history(self, query: str, context: str, history: List[Dict[str, str]]) -> str:
        """대화 히스토리를 고려한 교육 서비스 특화 응답 생성"""
        try:
            system_prompt = f"""당신은 교육 서비스 회사의 공손하고 전문적인 상담원입니다. 
다음 교육 과정 정보를 기반으로 고객의 질문에 답변해주세요.
이전 대화 내용도 참고하여 일관성 있고 친절한 답변을 제공하세요.

**응답 스타일:**
- 공손하고 친절한 톤으로 답변
- "~입니다", "~하시면 됩니다" 등의 존댓말 사용
- 교육 과정 정보가 없으면 "해당 정보는 현재 제공되지 않습니다"라고 답변
- 가능하면 구체적인 과정명, 커리큘럼, 수강료, 기간 등을 포함
- 추가 문의사항이 있으면 언제든 연락주시라고 안내

**교육 과정 정보:**
{context}

**고객 질문:** {query}

**답변:**"""

            messages = [{"role": "system", "content": system_prompt}]
            
            # 대화 히스토리 추가
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # 현재 질문 추가
            messages.append({"role": "user", "content": query})
            
            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response with history: {e}")
            return "죄송합니다. 응답 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요." 