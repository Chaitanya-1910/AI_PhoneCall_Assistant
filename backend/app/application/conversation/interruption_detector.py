from app.domain.conversation.interruption import InterruptionDecision
from app.domain.conversation.classifier import SpeechClassifier, SpeechClassification
import logging

logger = logging.getLogger(__name__)

class InterruptionDetector:
    """
    Evaluates whether an acoustic event (PotentialInterruptionDetected) or transcript
    actually constitutes a genuine interruption, a backchannel, or just noise.
    """
    
    @classmethod
    def evaluate(
        cls, 
        transcript: str, 
        overlap_duration_ms: float,
        vad_confidence: float = 1.0,
        stt_confidence: float = 1.0
    ) -> InterruptionDecision:
        
        # If we have no transcript yet, but overlap is very short (within grace window), we PAUSE to wait.
        if not transcript:
            if overlap_duration_ms < 200:
                # Still within grace window, pause and wait for text
                return InterruptionDecision.PAUSE
            else:
                # Too long for grace window without text, might be heavy noise. We can ignore or pause.
                return InterruptionDecision.IGNORE
                
        classification = SpeechClassifier.classify(transcript)
        
        # Combine signals into a confidence score (simplified for now)
        interruption_confidence = vad_confidence * stt_confidence
        
        if classification in (SpeechClassification.SOFT_BACKCHANNEL, SpeechClassification.HARD_BACKCHANNEL):
            return InterruptionDecision.CONTINUE
            
        if classification == SpeechClassification.INTERRUPTION:
            if interruption_confidence > 0.6:
                return InterruptionDecision.CANCEL
            return InterruptionDecision.PAUSE
            
        if classification == SpeechClassification.NEW_REQUEST:
            if overlap_duration_ms > 200 and interruption_confidence > 0.5:
                return InterruptionDecision.CANCEL
            return InterruptionDecision.PAUSE
            
        return InterruptionDecision.IGNORE
