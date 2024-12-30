from enum import Enum
from django.db import models

class ModeEnum(models.TextEnum):
    ADD = '1', 'Add'
    UPDATE = '2', 'Update'