import asyncio
from typing import AsyncGenerator
import logging
from app.domain.conversation.ai_services import LanguageModelService
from app.domain.conversation.prompt_builder import Prompt
from app.domain.conversation.cancellation import CancellationToken
from app.domain.conversation.events import LLMTokenGenerated, LLMResponseCompleted
from app.infrastructure.ai.groq.adapter import GroqAdapter

logger = logging.getLogger(__name__)

class StreamingGroqAdapter(LanguageModelService):
    """
    Thin wrapper over GroqAdapter to adapt it to the streaming protocol.
    Converts Groq streams into LLMTokenGenerated and LLMResponseCompleted events.
    Respects cooperative cancellation.
    """
    def __init__(self, groq_adapter: GroqAdapter):
        self._adapter = groq_adapter

    async def generate_response(
        self, 
        prompt: Prompt, 
        session_id: str,
        cancellation_token: CancellationToken
    ) -> AsyncGenerator[LLMTokenGenerated | LLMResponseCompleted, None]:
        
        full_text = ""
        system_prompt = f"{prompt.system_instructions}\nIdentity: {prompt.assistant_identity}\nConstraints: {prompt.safety_constraints}"
        
        # Build the user prompt string from the Prompt structure
        user_prompt = f"Context: {prompt.conversation_context}\n"
        user_prompt += f"Caller: {prompt.caller_profile}\n"
        user_prompt += f"Goals: {prompt.conversation_goals}\n"
        if prompt.transcript_history:
            user_prompt += f"History: {' | '.join(prompt.transcript_history)}\n"
        user_prompt += f"Latest: {prompt.latest_transcript}"
        
        try:
            stream = self._adapter.generate_response_stream(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            async for token in stream:
                if cancellation_token.is_cancelled:
                    logger.info(f"Groq generation cancelled for session {session_id}")
                    break
                    
                full_text += token
                yield LLMTokenGenerated(session_id=session_id, token=token)
                
                # Yield control to allow cancellation checks
                await asyncio.sleep(0)
                
            if not cancellation_token.is_cancelled:
                yield LLMResponseCompleted(session_id=session_id, full_text=full_text)
                
        except Exception as e:
            logger.error(f"Groq streaming failed for session {session_id}: {e}")
            raise
