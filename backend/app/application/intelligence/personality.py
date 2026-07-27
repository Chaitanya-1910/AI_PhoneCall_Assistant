from typing import Dict, Any
from app.application.intelligence.emotion import EmotionType, EmotionDetectionResult

class VoiceProfile:
    """Represents a specific voice identity (e.g. ElevenLabs Voice ID) and default settings."""
    def __init__(self, voice_id: str, default_speed: float, stability: float, similarity_boost: float):
        self.voice_id = voice_id
        self.default_speed = default_speed
        self.stability = stability
        self.similarity_boost = similarity_boost

class PersonalityEngine:
    """
    Dynamically adjusts the AI's speaking style and prompt based on the caller's emotion and the Tenant's brand guidelines.
    """
    def __init__(self, base_voice: VoiceProfile):
        self.base_voice = base_voice
        
    def adapt_prompt(self, base_prompt: str, emotion: EmotionDetectionResult) -> str:
        """Modifies the LLM system prompt instructions based on caller emotion."""
        style_instruction = "Be helpful and professional."
        
        if emotion.primary_emotion == EmotionType.FRUSTRATED:
            style_instruction = "The caller seems frustrated. Be extremely empathetic, concise, and prioritize resolving their issue immediately."
        elif emotion.primary_emotion == EmotionType.URGENT:
            style_instruction = "The caller is in a rush. Skip pleasantries and provide immediate, direct answers."
        elif emotion.primary_emotion == EmotionType.CONFUSED:
            style_instruction = "The caller seems confused. Speak slowly and explain things step-by-step."
            
        return f"{base_prompt}\n\n[STYLE INSTRUCTION]: {style_instruction}"

    def adapt_tts_parameters(self, emotion: EmotionDetectionResult) -> Dict[str, Any]:
        """Modifies the Text-to-Speech parameters (e.g., for ElevenLabs) based on emotion."""
        params = {
            "voice_id": self.base_voice.voice_id,
            "speed": self.base_voice.default_speed,
            "stability": self.base_voice.stability,
            "similarity_boost": self.base_voice.similarity_boost
        }
        
        if emotion.primary_emotion == EmotionType.FRUSTRATED:
            # Slower, more stable voice for empathy
            params["speed"] = max(0.8, params["speed"] - 0.15)
            params["stability"] = min(1.0, params["stability"] + 0.2)
        elif emotion.primary_emotion == EmotionType.URGENT:
            # Faster, more direct voice
            params["speed"] = min(1.5, params["speed"] + 0.2)
            
        return params
