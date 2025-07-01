from django.db import models
from simple_history.models import HistoricalRecords

class Role(models.Model):
    name = models.CharField(max_length=50)
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name

class User(models.Model):
    username = models.CharField(max_length=50)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    STATUS_CHOICES = [
        (0, 'Inativo'),
        (1, 'Ativo'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    create_date = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=254)
    history = HistoricalRecords()

    def __str__(self):
        return self.username