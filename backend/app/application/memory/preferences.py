from typing import List
from app.domain.memory.models import CallerProfile
from app.domain.intelligence.models import ConversationSummary

class PreferenceManager:
    """
    Learns and updates CallerProfile preferences based on conversation summaries.
    """
    
    @classmethod
    def update_preferences(cls, profile: CallerProfile, summary: ConversationSummary) -> CallerProfile:
        # Example heuristic: if a specific language is frequently used, update it.
        # If they called for an appointment, record it.
        profile.previous_topics.append(summary.short_summary)
        # Keeps list bounded
        if len(profile.previous_topics) > 5:
            profile.previous_topics.pop(0)
            
        return profile
