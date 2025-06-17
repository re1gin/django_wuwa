
from django.db import models

class Sonata(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sonata"
        verbose_name_plural = "Sonatas"

# Model untuk Echo (bidang 'skill' dihapus)
class Echo(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cost = models.IntegerField()
    sonatas = models.ManyToManyField(Sonata, related_name='echos')
    # Bidang 'skill' telah dihapus dari sini

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Echo"
        verbose_name_plural = "Echos"