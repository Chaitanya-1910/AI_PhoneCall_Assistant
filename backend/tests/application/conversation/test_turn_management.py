import pytest
from app.domain.conversation.classifier import SpeechClassifier, SpeechClassification
from app.domain.conversation.interruption import InterruptionDecision
from app.application.conversation.interruption_detector import InterruptionDetector

def test_speech_classifier_backchannels():
    assert SpeechClassifier.classify("uh-huh") == SpeechClassification.SOFT_BACKCHANNEL
    assert SpeechClassifier.classify("hmm") == SpeechClassification.SOFT_BACKCHANNEL
    assert SpeechClassifier.classify("yeah") == SpeechClassification.HARD_BACKCHANNEL
    assert SpeechClassifier.classify("right") == SpeechClassification.HARD_BACKCHANNEL
    
def test_speech_classifier_interruptions():
    assert SpeechClassifier.classify("wait") == SpeechClassification.INTERRUPTION
    assert SpeechClassifier.classify("stop") == SpeechClassification.INTERRUPTION
    assert SpeechClassifier.classify("actually") == SpeechClassification.INTERRUPTION
    assert SpeechClassifier.classify("hold on") == SpeechClassification.INTERRUPTION

def test_speech_classifier_agreements():
    assert SpeechClassifier.classify("yes") == SpeechClassification.AGREEMENT
    assert SpeechClassifier.classify("no") == SpeechClassification.DISAGREEMENT

def test_speech_classifier_noise_and_new_requests():
    assert SpeechClassifier.classify("") == SpeechClassification.SILENCE
    assert SpeechClassifier.classify("what about the other thing") == SpeechClassification.NEW_REQUEST

def test_interruption_detector_grace_window():
    # Inside grace window (<200ms) with no text (could be breathing/cough) -> PAUSE
    decision = InterruptionDetector.evaluate(transcript="", overlap_duration_ms=100)
    assert decision == InterruptionDecision.PAUSE
    
    # Outside grace window with no text -> IGNORE
    decision = InterruptionDetector.evaluate(transcript="", overlap_duration_ms=300)
    assert decision == InterruptionDecision.IGNORE

def test_interruption_detector_backchannels():
    # Backchannels should allow CHAYA to continue speaking
    decision = InterruptionDetector.evaluate(transcript="uh-huh", overlap_duration_ms=300)
    assert decision == InterruptionDecision.CONTINUE
    
    decision = InterruptionDetector.evaluate(transcript="yeah", overlap_duration_ms=400)
    assert decision == InterruptionDecision.CONTINUE

def test_interruption_detector_genuine_interruption():
    # A strong interruption
    decision = InterruptionDetector.evaluate(
        transcript="wait stop", 
        overlap_duration_ms=500, 
        vad_confidence=1.0, 
        stt_confidence=1.0
    )
    assert decision == InterruptionDecision.CANCEL

def test_interruption_detector_uncertain_new_request():
    # A new request during speech should cancel if it's past the grace window and confident
    decision = InterruptionDetector.evaluate(
        transcript="can you book a flight", 
        overlap_duration_ms=500, 
        vad_confidence=0.9, 
        stt_confidence=0.9
    )
    assert decision == InterruptionDecision.CANCEL
    
    # If confidence is low, we might just pause instead of full cancel
    decision = InterruptionDetector.evaluate(
        transcript="can you book a flight", 
        overlap_duration_ms=500, 
        vad_confidence=0.5, 
        stt_confidence=0.4
    )
    assert decision == InterruptionDecision.PAUSE
