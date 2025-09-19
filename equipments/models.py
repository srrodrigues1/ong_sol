from django.db import models
from simple_history.models import HistoricalRecords

class Equipment(models.model):
    name = models.CharField(max_length=50)
    create_date = 
    history = HistoricalRecords()