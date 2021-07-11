from django.db import models

class Drv(models.Model):
  name = models.CharField('drv', max_length=16, unique=True)

  class Meta:
    verbose_name = "Direction Régionale des Ventes"

  def __str__(self) ->str:
    return self.name

class Agent(models.Model):
  name = models.CharField('agent', max_length=64, unique=True)
  drv = models.ForeignKey('Drv', on_delete=models.CASCADE, blank=False)

  class Meta:
    verbose_name = "Agent"

  def __str__(self) ->str:
    return self.name

class AgentFinitions(models.Model):
  name = models.CharField('agent_finition', max_length=64, unique=True)
  drv = models.ForeignKey('Drv', on_delete=models.CASCADE, blank=False)

  class Meta:
    verbose_name = "Agent Finitions"

  def __str__(self) ->str:
    return self.name

class Dep(models.Model):
  name = models.CharField('dep', max_length=2, unique=True)

  class Meta:
    verbose_name = "Département"

  def __str__(self) ->str:
    return self.name

class Bassin(models.Model):
  name = models.CharField('bassin', max_length=64, unique=True)

  class Meta:
    verbose_name = "Bassin"

  def __str__(self) ->str:
    return self.name

class Ville(models.Model):
  name = models.CharField('ville', max_length=128, unique=True)

  class Meta:
    verbose_name = "Ville"

  def __str__(self) ->str:
    return self.name
