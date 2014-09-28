from django.db import models

from accounting.models import Ledger

class Customer(models.Model):
	ledger = models.ForeignKey(Ledger, null=True, blank=True)
	name = models.CharField("Customer Name", max_length=200, null=True,blank=True, unique=True)
	address = models.TextField("Address", null=True, blank=True)
	mobile = models.CharField("Mobile", max_length=200, null=True,blank=True)
	telephone_number = models.CharField("Telephone Number", max_length=200, null=True,blank=True)
	email = models.CharField("Email", max_length=200, null=True,blank=True)

	def __unicode__(self):
		return self.name
