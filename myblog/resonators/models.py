from django.db import models

class Character(models.Model):
    name = models.CharField(max_length=100)
    rarity = models.CharField(max_length=10)
    weapon = models.CharField(max_length=50)
    birthday = models.CharField(max_length=20)
    affiliation = models.CharField(max_length=100)
    birthday = models.CharField(max_length=20)
    birthplace = models.CharField(max_length=100)
    attribute = models.CharField(max_length=50)
    role = models.CharField(max_length=100)
    hp = models.PositiveIntegerField()
    atk = models.PositiveIntegerField()
    defense = models.PositiveIntegerField()


    def __str__(self):
        return self.name

