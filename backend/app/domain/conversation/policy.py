from enum import Enum
from app.domain.conversation.classifier import SpeechClassifier, SpeechClassification
from app.domain.conversation.confidence import ConversationConfidence
from app.domain.conversation.clarification import ClarificationManager

class PolicyAction(str, Enum):
    RESPOND = "RESPOND"
    ASK_CLARIFICATION = "ASK_CLARIFICATION"
    WAIT = "WAIT"
    END_CALL = "END_CALL"
    REQUEST_CALLBACK = "REQUEST_CALLBACK"
    ESCALATE = "ESCALATE"
    IGNORE = "IGNORE"
    PAUSE_RESPONSE = "PAUSE_RESPONSE"
    RESUME_RESPONSE = "RESUME_RESPONSE"

class ResponsePolicy:
    @staticmethod
    def evaluate(context: "ConversationContext", memory: "WorkingMemory", latest_transcript: str) -> PolicyAction:
        """
        Decides the next action based on context, memory, and the latest transcript.
        Internally consumes classifications and confidence rather than raw text.
        """
        classification = SpeechClassifier.classify(latest_transcript)
        
        # We simulate a confidence score here since it would normally come from the STT event
        confidence = ConversationConfidence() 
        
        if ClarificationManager.needs_clarification(confidence):
            return PolicyAction.ASK_CLARIFICATION
            
        if classification == SpeechClassification.SILENCE:
            return PolicyAction.WAIT
            
        if classification in (SpeechClassification.SOFT_BACKCHANNEL, SpeechClassification.HARD_BACKCHANNEL):
            # Backchannels typically mean the caller is just acknowledging, we wait for them to finish or we continue.
            # In a full dialog system, we might resume if we were paused.
            return PolicyAction.WAIT
            
        if classification == SpeechClassification.INTERRUPTION:
            # We already handle interruption cancellation via InterruptionDetector.
            # For the policy, an interruption that survives to here means we should respond to it.
            return PolicyAction.RESPOND
            
        # Hardcoded end call for demo
        if "goodbye" in latest_transcript.lower() or "bye" in latest_transcript.lower():
            return PolicyAction.END_CALL
            
        if context.urgency_level == "HIGH":
            return PolicyAction.ESCALATE
            
        return PolicyAction.RESPOND
