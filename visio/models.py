from django.db import models

class Drv(models.Model):
  name = models.CharField('drv', max_length=16, unique=True)

  class Meta:
    verbose_name = "Direction Régionale des Ventes"

  def __str__(self) ->str:
    return self.name

class Agent(models.Model):
  name = models.CharField('drv', max_length=64, unique=True)
  drv = models.ForeignKey('Drv', on_delete=models.CASCADE)

  class Meta:
    verbose_name = "Agent"

  def __str__(self) ->str:
    return self.name
