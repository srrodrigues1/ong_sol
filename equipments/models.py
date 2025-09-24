from django.db import models
from simple_history.models import HistoricalRecords

class Equipment(models.Model):
    name = models.CharField(max_length=50)
    TYPE_CHOICES = [
        (0, 'Cadeira de Rodas'),
        (1, 'Muletas'),
        (2, 'Cama Hospitalar'),
    ]
    type = models.IntegerField(choices=TYPE_CHOICES)
    create_date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        (0, 'Inativo'),
        (1, 'Disponível'),
        (2, 'Emprestado'),
        (3, 'Em conserto'),
        (4, 'Extraviado'),
        (5, 'Avariado'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    location = models.CharField(max_length=50)
    history = HistoricalRecords()

    def __str__(self):
        return self.name
    
class Loans(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="loans")
    requester = models.CharField(max_length=50)  # futuramente -> models.ForeignKey(Person, ...)
    loan_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="ativo")  # ativo, devolvido, atrasado
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.equipment.name} - {self.requester}"