from enum import Enum

class InterruptionDecision(str, Enum):
    CONTINUE = "CONTINUE"
    PAUSE = "PAUSE"
    CANCEL = "CANCEL"
    IGNORE = "IGNORE"
