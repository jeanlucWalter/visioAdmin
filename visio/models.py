from django.db import models

class Drv(models.Model):
  name = models.CharField('drv', max_length=16, unique=True)

  class Meta:
    verbose_name = "Direction Régionale des Ventes"

  def __str__(self) ->str:
    return self.name

class Agent(models.Model):
  name = models.CharField('agent', max_length=64, unique=True)
  drv = models.ForeignKey('drv', on_delete=models.PROTECT, blank=False)

  class Meta:
    verbose_name = "Agent"

  def __str__(self) ->str:
    return self.name

class AgentFinitions(models.Model):
  name = models.CharField('agent_finitions', max_length=64, unique=True)
  drv = models.ForeignKey('drv', on_delete=models.PROTECT, blank=False)

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

class SegmentMarketing(models.Model):
  name = models.CharField('segment_marketing', max_length=32, unique=True)

  class Meta:
    verbose_name = "Segment Marketing"

  def __str__(self) ->str:
    return self.name

class SegmentCommercial(models.Model):
  name = models.CharField('segment_commercial', max_length=16, unique=True)

  class Meta:
    verbose_name = "Segment Commercial"

  def __str__(self) ->str:
    return self.name

class Enseigne(models.Model):
  name = models.CharField('name', max_length=64, unique=True, blank=False, default="Inconnu")

  class Meta:
    verbose_name = "Ensseigne"

  def __str__(self) ->str:
    return self.name

class Ensemble(models.Model):
  name = models.CharField('name', max_length=64, unique=True, blank=False, default="Inconnu")
  enseigne = models.ForeignKey('enseigne', on_delete=models.PROTECT, blank=False, default=7)

  class Meta:
    verbose_name = "Ensemble"

  def __str__(self) ->str:
    return self.name

class Pdv(models.Model):
  drv = models.ForeignKey('drv', on_delete=models.PROTECT,  blank=False)
  agent = models.ForeignKey('agent', on_delete=models.PROTECT, blank=False)
  dep = models.ForeignKey("dep", on_delete=models.PROTECT, blank=False)
  bassin = models.ForeignKey("bassin", on_delete=models.PROTECT, blank=False)
  ville = models.ForeignKey("ville", on_delete=models.PROTECT, blank=False)
  code = models.CharField('code', max_length=10, blank=False, default="Inconnu")
  name = models.CharField('name', max_length=64, blank=False, default="Inconnu")
  latitude = models.FloatField('latitude', unique=False, blank=False, default=0.0)
  longitude = models.FloatField('longitude', unique=False, blank=False, default=0.0)
  segment_commercial = models.ForeignKey("segmentcommercial", on_delete=models.PROTECT, blank=False, default=1)
  segment_marketing = models.ForeignKey("segmentmarketing", on_delete=models.PROTECT, blank=False, default=1)
  enseigne = models.ForeignKey('enseigne', on_delete=models.PROTECT, blank=False, default=1)
  ensemble = models.ForeignKey('ensemble', on_delete=models.PROTECT, blank=False, default=1)

  class Meta:
    verbose_name = "Point de Vente"

  def __str__(self) ->str:
    return self.name + " " + self.code