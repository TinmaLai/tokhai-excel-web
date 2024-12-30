from enum import Enum
from django.db import models

class ModeEnum(Enum):
    ADD = 1
    UPDATE = 2