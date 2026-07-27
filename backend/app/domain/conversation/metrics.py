from pydantic import BaseModel

class ConversationMetrics(BaseModel):
    session_id: str
    stt_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    tts_latency_ms: float = 0.0
    queue_wait_time_ms: float = 0.0
    processing_time_per_event_ms: float = 0.0
    average_turn_duration_ms: float = 0.0
    total_conversation_duration_ms: float = 0.0
    
    speech_segmentation_latency_ms: float = 0.0
    average_segment_duration_ms: float = 0.0
    segments_per_conversation: int = 0
    partial_transcript_count: int = 0
    final_transcript_count: int = 0
    average_llm_token_rate: float = 0.0
    average_synthesized_audio_chunk_duration_ms: float = 0.0
    
    interruption_count: int = 0
    false_interruption_count: int = 0
    average_caller_speech_duration_ms: float = 0.0
    average_ai_speech_duration_ms: float = 0.0
    clarification_rate: float = 0.0
    latency_before_response_ms: float = 0.0
    cancelled_responses: int = 0
    pause_count: int = 0
    resume_count: int = 0
    cancel_count: int = 0
    interruption_confidence: float = 0.0
    average_pause_duration_ms: float = 0.0
    grace_window_hits: int = 0

    # Phase 7.4 Extensions
    intent_latency_ms: float = 0.0
    entity_extraction_latency_ms: float = 0.0
    action_generation_latency_ms: float = 0.0
    summary_generation_latency_ms: float = 0.0
    priority_calculation_latency_ms: float = 0.0
    overall_intelligence_latency_ms: float = 0.0
