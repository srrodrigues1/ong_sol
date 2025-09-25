from django.db import models
from simple_history.models import HistoricalRecords


class Documents(models.Model):
    image = models.ImageField(upload_to='documents/')
    create_date = models.DateTimeField(auto_now_add=True)

class Person(models.Model):
    name = models.CharField(max_length=50)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=20)
    ddd = models.CharField(max_length=10)
    state = models.CharField(max_length=30)
    city = models.CharField(max_length=40)
    district = models.CharField(max_length=30)
    street = models.CharField(max_length=40)
    st_number = models.CharField(max_length=10)
    cep = models.CharField(max_length=8)
    STATUS_CHOICES = [
        (0, 'Inativo'),
        (1, 'Ativo'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    create_date = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()
    
    def __str__(self):
        return self.name