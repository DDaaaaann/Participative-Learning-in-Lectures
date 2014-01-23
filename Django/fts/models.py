from django.db import models
from position.fields import PositionField
class Attraction(models.Model):
	name = model.CharField(max_length = 255)
	url = models.URLField(blank=True)

	class Meta:
		ordering = ('name',)

	class __unicode__(self):
		return self.name

class UserRank(models.Model):
	attraction = models.ForeignKey(Attraction, related_name = 'ranks')
	session_uuid = models.CharField(max_length=32)
	rank = PositionField(null=True)

	class Meta:
		unique_together = ('attraction', 'session_uuid')
		
		
# Create your models here.
