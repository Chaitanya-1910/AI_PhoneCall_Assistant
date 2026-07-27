from typing import List, Dict, Any
from app.domain.conversation.multi_modal import MultiModalContextExtension
from app.domain.knowledge.models import ValidatedKnowledgeGraph
from app.application.intelligence.emotion import EmotionDetectionResult

class PromptBuilder:
    """
    Builds the final prompt sent to the LLM (e.g. GPT-4o, Claude) 
    fusing text, emotion, goals, and multi-modal attachments.
    """
    def build_system_prompt(self, 
                            base_personality: str, 
                            emotion: EmotionDetectionResult,
                            pending_goals: List[str],
                            knowledge: ValidatedKnowledgeGraph) -> str:
        
        prompt = f"System Personality:\n{base_personality}\n\n"
        
        prompt += f"Caller Emotional State: {emotion.primary_emotion.value}\n"
        prompt += f"Sentiment Score: {emotion.sentiment.model_dump()}\n\n"
        
        if pending_goals:
            prompt += "REQUIRED GOALS TO COMPLETE BEFORE ENDING CALL:\n"
            for goal in pending_goals:
                prompt += f"- {goal}\n"
        
        prompt += "\nExtracted Knowledge:\n"
        prompt += knowledge.model_dump_json()
        
        return prompt

    def build_user_message(self, transcript: str, multi_modal: MultiModalContextExtension) -> List[Dict[str, Any]]:
        """
        Constructs the user message in the standard Vision-Language-Model (VLM) format.
        """
        content = [{"type": "text", "text": transcript}]
        
        for attachment in multi_modal.attachments:
            if attachment.extracted_text:
                content.append({
                    "type": "text", 
                    "text": f"[ATTACHMENT OCR]: {attachment.extracted_text}"
                })
            elif attachment.base64_data:
                # GPT-4 Vision format
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{attachment.content_type};base64,{attachment.base64_data}"
                    }
                })
                
        return content
