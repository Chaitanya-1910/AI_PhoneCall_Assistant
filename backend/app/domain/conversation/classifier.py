from enum import Enum
import re

class SpeechClassification(str, Enum):
    NEW_REQUEST = "NEW_REQUEST"
    SOFT_BACKCHANNEL = "SOFT_BACKCHANNEL"
    HARD_BACKCHANNEL = "HARD_BACKCHANNEL"
    UNCERTAIN = "UNCERTAIN"
    INTERRUPTION = "INTERRUPTION"
    FILLER = "FILLER"
    SILENCE = "SILENCE"
    AGREEMENT = "AGREEMENT"
    DISAGREEMENT = "DISAGREEMENT"

class SpeechClassifier:
    """Classifies speech transcripts into conversation actions."""
    
    SOFT_BACKCHANNELS = re.compile(r"^(uh-huh|hmm|mhm|oh|ah)$", re.IGNORECASE)
    HARD_BACKCHANNELS = re.compile(r"^(yeah|right|okay|sure|i see)$", re.IGNORECASE)
    AGREEMENTS = re.compile(r"^(yes|exactly|absolutely|correct)$", re.IGNORECASE)
    DISAGREEMENTS = re.compile(r"^(no|not really|incorrect|wrong)$", re.IGNORECASE)
    INTERRUPTIONS = re.compile(r"^(wait|stop|actually|hold on|excuse me)$", re.IGNORECASE)
    
    @classmethod
    def classify(cls, transcript: str) -> SpeechClassification:
        clean_transcript = transcript.strip().lower()
        
        if not clean_transcript:
            return SpeechClassification.SILENCE
            
        if cls.SOFT_BACKCHANNELS.match(clean_transcript):
            return SpeechClassification.SOFT_BACKCHANNEL
            
        if cls.HARD_BACKCHANNELS.match(clean_transcript):
            return SpeechClassification.HARD_BACKCHANNEL
            
        if cls.AGREEMENTS.match(clean_transcript):
            return SpeechClassification.AGREEMENT
            
        if cls.DISAGREEMENTS.match(clean_transcript):
            return SpeechClassification.DISAGREEMENT
            
        if cls.INTERRUPTIONS.match(clean_transcript):
            return SpeechClassification.INTERRUPTION
            
        # For now, default to NEW_REQUEST if it has substantive content
        if len(clean_transcript.split()) > 2:
            return SpeechClassification.NEW_REQUEST
            
        return SpeechClassification.UNCERTAIN
