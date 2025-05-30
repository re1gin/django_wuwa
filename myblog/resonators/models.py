from django.db import models

class Character(models.Model):
    RARITY_CHOICES = [
        ('4 Star', '4 Star'),
        ('5 Star', '5 Star'),
    ]

    SEX_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Unknown', 'Unknown'),
    ]

    character = models.CharField(max_length=100)
    rarity = models.CharField(max_length=10, choices=RARITY_CHOICES)
    weapon = models.CharField(max_length=50)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, default='Unknown')
    codename = models.CharField(max_length=100)
    birthday = models.CharField(max_length=20)  # Bisa disimpan string kalau format variatif
    affiliation = models.CharField(max_length=100)
    birthplace = models.CharField(max_length=100)
    attribute = models.CharField(max_length=50)
    role = models.CharField(max_length=100)
    hp = models.IntegerField()
    atk = models.IntegerField()
    defense = models.IntegerField()
    energy = models.IntegerField()
    crit_rate = models.IntegerField()
    crit_dmg = models.IntegerField()

    def __str__(self):
        return self.character
