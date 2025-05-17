from django.db import models

class BaseStat(models.Model):
    hp = models.IntegerField()
    atk = models.IntegerField()
    defense = models.IntegerField()
    energy = models.FloatField()
    crit_rate = models.FloatField()
    crit_dmg = models.FloatField()

class FinalStat(models.Model):
    hp = models.IntegerField()
    atk = models.IntegerField()
    defense = models.IntegerField()
    energy = models.FloatField()
    crit_rate = models.FloatField()
    crit_dmg = models.FloatField()

class Character(models.Model):
    name = models.CharField(max_length=100)
    element = models.CharField(max_length=50)
    weapon_type = models.CharField(max_length=50)

    base_stat = models.OneToOneField(BaseStat, on_delete=models.CASCADE)
    final_stat = models.OneToOneField(FinalStat, on_delete=models.CASCADE)

    icon = models.ImageField(upload_to='character/icon/')
    splash = models.ImageField(upload_to='character/splash/')
    banner_sprite = models.ImageField(upload_to='character/banner_sprite/')
    profile = models.ImageField(upload_to='character/profile/')

    def __str__(self):
        return self.name
