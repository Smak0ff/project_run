from enum import Enum, auto


class ChallengeEvent(str, Enum):
    RUN_FINISHED = "RUN_FINISHED"
    RUN_STARTED = "RUN_STARTED"
