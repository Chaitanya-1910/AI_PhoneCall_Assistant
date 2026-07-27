from app.domain.conversation.interruption import InterruptionDecision
from app.domain.conversation.cancellation import CancellationToken
import logging

logger = logging.getLogger(__name__)

class TurnManager:
    """
    The absolute authority on turn-taking execution.
    Executes InterruptionDecision actions onto the CancellationToken.
    """
    
    @classmethod
    def execute_decision(cls, decision: InterruptionDecision, token: CancellationToken) -> None:
        if decision == InterruptionDecision.CONTINUE:
            if token.is_paused:
                logger.info("TurnManager: Resuming playback (backchannel detected).")
                token.resume()
                
        elif decision == InterruptionDecision.PAUSE:
            if not token.is_paused and not token.is_cancelled:
                logger.info("TurnManager: Pausing playback (evaluating interruption).")
                token.pause()
                
        elif decision == InterruptionDecision.CANCEL:
            if not token.is_cancelled:
                logger.info("TurnManager: Cancelling generation (genuine interruption).")
                token.cancel()
                
        elif decision == InterruptionDecision.IGNORE:
            pass
