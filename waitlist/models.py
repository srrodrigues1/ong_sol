from django.db import models

from persons.models import Person
from equipments.models import Equipment

class Waitlist(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="Waitlist"
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="Waitlist"
    )
    contact_date = models.DateField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
