from django.db import models
from django.contrib.auth.models import User

class Permission(models.Model):

	accounts_permission = models.BooleanField('Accounts Permission', default=False)
	inventory_permission = models.BooleanField('Inventory Permission', default=False)
	purchase_permission = models.BooleanField('Purchase Permission', default=False)
	sales_permission = models.BooleanField('Sales Permission', default=False)
	suppliers = models.BooleanField('Suppliers Permission', default=False)
	customers = models.BooleanField('Customers Permission', default=False)

	class Meta:
		verbose_name_plural = 'Permission'


class Staff(models.Model):

	user = models.ForeignKey(User, null=True, blank=True)
	designation = models.CharField('Designation', max_length=200, null=True, blank=True)
	address = models.TextField('Address', null=True, blank=True)
	contact_no = models.CharField('Contact No', max_length=15, null=True)
	permission = models.ForeignKey(Permission, null=True, blank=True)

	def __unicode__(self):
		return self.user.first_name + str(' - ') + self.user.first_name

	class Meta:
		verbose_name_plural = 'Staff'


class Salesman(models.Model):

	first_name = models.CharField('First Name', max_length=200, null=True)
	last_name = models.CharField('Last Name', max_length=200, null=True)
	address = models.TextField('Address', null=True, blank=True)
	contact_no = models.CharField('Contact No', max_length=15, null=True)
	email = models.CharField("Email", max_length=200, null=True,blank=True)

	def __unicode__(self):
		return self.first_name + " " + self.last_name

	class Meta:
		verbose_name_plural = 'Salesman'

class Shope(models.Model):

	name = models.CharField('Shope Name', max_length=200, null=True)
	address = models.TextField('Address', null=True, blank=True)
	contact_no = models.CharField('Contact No', max_length=15, null=True)
	email = models.CharField("Email", max_length=200, null=True,blank=True)

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Shope'