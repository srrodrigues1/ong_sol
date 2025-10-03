from django.db import models
from simple_history.models import HistoricalRecords

from persons.models import Person

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
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name="loans")
    requester = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="loans")
    loan_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = [
        (0, 'Ativo'),
        (1, 'Devolvido'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.equipment.name} - {self.requester}"