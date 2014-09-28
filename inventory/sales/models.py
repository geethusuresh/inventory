from django.db import models

from inventory.models import Item, BatchItem
from customers.models import Customer
from web.models import Salesman

PAYMENT_MODE = (
	('cash', 'Cash'),
	('cheque', 'Cheque'),
	('card', 'Card'),
	('credit', 'Credit'),
)
INVOICE_TYPE = (
	('Tax Exclusive', 'Tax Exclusive'),
	('Tax Inclusive', 'Tax Inclusive'),
)
BILL_TYPE = (
	('Receipt', 'Receipt'),
	('Invoice', 'Invoice'),
)

class Sale(models.Model):

	customer = models.ForeignKey(Customer, null=True, blank=True)
	salesman = models.ForeignKey(Salesman, null=True, blank=True)
	do_number = models.CharField('DO Number', max_length=200, null=True, blank=True)
	bill_type = models.CharField('Bill Type', max_length=200, choices=BILL_TYPE, null=True, blank=True)	
	transaction_reference_no = models.CharField('Transaction Reference Number', null=True, blank=True, max_length=200)

	sales_invoice_number = models.CharField('Sales Invoice Number', max_length=200, null=True, blank=True)
	sales_invoice_date = models.DateField('Sales Invoice Date', null=True, blank=True)

	payment_mode = models.CharField('Payment mode', max_length=200, choices=PAYMENT_MODE, null=True, blank=True)
	bank_name = models.CharField('Bank Name', max_length=200, null=True, blank=True)
	card_number = models.CharField('Card Number', max_length=200, null=True, blank=True)
	cheque_date = models.DateField("Cheque Date", null=True, blank=True)
	cheque_number = models.CharField("Cheque Number", max_length=200, null=True, blank=True)
	branch = models.CharField("Branch", max_length=200, null=True, blank=True)
	card_holder_name = models.CharField("Card Holder Name", max_length=200, null=True, blank=True)
	
	discount = models.DecimalField('Discount', max_digits=14, decimal_places=2, default=0)
	grant_total  = models.DecimalField('Grant Total', max_digits=14, decimal_places=2, default=0)
	round_off = models.DecimalField('Round off', max_digits=14, decimal_places=2, default=0)

	def __unicode__(self):

		return self.transaction_reference_no

	class Meta:

		verbose_name_plural = 'Sales'



class SalesItem(models.Model):

	sales = models.ForeignKey(Sale)
	batch_item = models.ForeignKey(BatchItem, null=True, blank=True)

	quantity = models.DecimalField('Quantity', max_digits=20, decimal_places=10, default=0)
	uom = models.CharField('Uom', max_length=200, null=True, blank=True)
	mrp = models.DecimalField('MRP', max_digits=20, decimal_places=10, default=0)
	net_amount = models.DecimalField('Net Amount', max_digits=20, decimal_places=10, default=0)

	def __unicode__(self):

		return self.sales.sales_invoice_number

	class Meta:

		verbose_name_plural = 'Sales Item'


class Receipt(models.Model):

	sales = models.ForeignKey(Sale)

	receipt_no = models.CharField('Receipt Number', max_length=200, null=True, blank=True, unique=True)


class Invoice(models.Model):

	sales = models.ForeignKey(Sale)
	
	invoice_no = models.CharField('Invoice Number', max_length=200, null=True, blank=True, unique=True)
	invoice_type = models.CharField('Invoice Type', max_length=200, choices=INVOICE_TYPE, null=True, blank=True)	

class Estimate(models.Model):

	customer = models.ForeignKey(Customer, null=True, blank=True)
	salesman = models.ForeignKey(Salesman, null=True, blank=True)
	do_number = models.CharField('DO Number', max_length=200, null=True, blank=True)
	bill_type = models.CharField('Bill Type', max_length=200, choices=INVOICE_TYPE, null=True, blank=True)

	estimate_invoice_number = models.CharField('Estimate Invoice Number', max_length=200, null=True, blank=True)
	auto_invoice_number = models.CharField('Auto Invoice Number', max_length=200, null=True, blank=True, unique=True)
	estimate_invoice_date = models.DateField('Estimate Invoice Date', null=True, blank=True)

	payment_mode = models.CharField('Payment mode', max_length=200, choices=PAYMENT_MODE, null=True, blank=True)
	bank_name = models.CharField('Bank Name', max_length=200, null=True, blank=True)
	card_number = models.CharField('Card Number', max_length=200, null=True, blank=True)
	cheque_date = models.DateField("Cheque Date", null=True, blank=True)
	cheque_number = models.CharField("Cheque Number", max_length=200, null=True, blank=True)
	branch = models.CharField("Branch", max_length=200, null=True, blank=True)
	card_holder_name = models.CharField("Card Holder Name", max_length=200, null=True, blank=True)
	
	discount = models.DecimalField('Discount', max_digits=14, decimal_places=2, default=0)
	grant_total = models.DecimalField('Grant Total', max_digits=14, decimal_places=2, default=0)

	def __unicode__(self):

		return self.estimate_invoice_number

	class Meta:

		verbose_name_plural = 'Estimates'

class EstimateItem(models.Model):

	estimate = models.ForeignKey(Estimate, null=True, blank=True)
	item = models.ForeignKey(Item, null=True, blank=True)
	batch_item = models.ForeignKey(BatchItem, null=True, blank=True)

	quantity = models.DecimalField('Quantity', max_digits=20, decimal_places=10, default=0)
	uom = models.CharField('Uom', max_length=200, null=True, blank=True)
	mrp = models.DecimalField('MRP', max_digits=20, decimal_places=10, default=0)
	net_amount = models.DecimalField('Net Amount', max_digits=20, decimal_places=10, default=0)

	def __unicode__(self):

		return self.estimate.estimate_invoice_number + ' - ' + self.item.code

	class Meta:

		verbose_name_plural = 'Estimate Item'


class SalesReturn(models.Model):

	sales = models.ForeignKey(Sale, null=True, blank=True)
	
	transaction_reference_no = models.CharField('Transaction Reference Number', null=True, blank=True, max_length=200)
	return_invoice_number = models.CharField('Return Invoice Number', max_length=200, null=True, blank=True, unique=True)
	invoice_date = models.DateField('Invoice Date', null=True, blank=True)
	grant_total = models.DecimalField('Grant Total', max_digits=20, decimal_places=2, default=0)

	def __unicode__(self):
		return self.sales.transaction_reference_no

	class Meta:

		verbose_name_plural = 'Sales Return'


class SalesReturnItem(models.Model):

	sales_return = models.ForeignKey(SalesReturn, null=True, blank=True)
	sales_item = models.ForeignKey(SalesItem)

	uom = models.CharField('Uom', max_length=200, null=True, blank=True)
	quantity = models.DecimalField('Quantity', max_digits=20, decimal_places=10, default=0)
	net_amount = models.DecimalField('Net Amount', max_digits=20, decimal_places=10, default=0)

	def __unicode__(self):
		return self.sales_item.sales.transaction_reference_no

	class Meta:

		verbose_name_plural = 'Sales Return Item'

