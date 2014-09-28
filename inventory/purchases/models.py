from django.db import models

from inventory.models import Item, Batch, BatchItem, UOMConversion
from suppliers.models import Supplier

PAYMENT_MODE = (
	('cash', 'Cash'),
	('cheque', 'Cheque'),
	('card', 'Card'),
	('credit', 'Credit'),
)


class Purchase(models.Model):

	supplier = models.ForeignKey(Supplier, null=True, blank=True)
	do_number = models.CharField('DO Number', max_length=200, null=True, blank=True)
	transaction_reference_no = models.CharField('Transaction Reference Number', null=True, blank=True, max_length=200)

	purchase_invoice_number = models.CharField('Purchase Invoice Number', max_length=200, null=True, blank=True, unique=True)
	purchase_invoice_date = models.DateField('Purchase Invoice Date', null=True, blank=True)

	payment_mode = models.CharField('Payment mode', max_length=200, choices=PAYMENT_MODE, null=True, blank=True)
	bank_name = models.CharField('Bank Name', max_length=200, null=True, blank=True)
	card_number = models.CharField('Card Number', max_length=200, null=True, blank=True)
	cheque_date = models.DateField("Cheque Date", null=True, blank=True)
	cheque_number = models.CharField("Cheque Number", max_length=200, null=True, blank=True)
	branch = models.CharField("Branch", max_length=200, null=True, blank=True)
	card_holder_name = models.CharField("Card Holder Name", max_length=200, null=True, blank=True)
	
	discount = models.DecimalField('Discount', max_digits=14, decimal_places=2, default=0)
	purchase_tax = models.DecimalField('Purchase Tax', max_digits=20, decimal_places=5, default=0)
	grant_total = models.DecimalField('Grant Total', max_digits=14, decimal_places=2, default=0)

	def __unicode__(self):

		return self.purchase_invoice_number

	class Meta:

		verbose_name_plural = 'Purchase'



class PurchaseItem(models.Model):

	purchase = models.ForeignKey(Purchase, null=True, blank=True)
	batch_item = models.ForeignKey(BatchItem, null=True, blank=True)

	quantity = models.DecimalField('Quantity', max_digits=20, decimal_places=5, default=0)
	purchase_price = models.DecimalField('Purchase Price', max_digits=20, decimal_places=5, default=0)
	
	cost_price = models.DecimalField('Cost Price', max_digits=20, decimal_places=5, default=0)
	net_amount = models.DecimalField('Net Amount', max_digits=20, decimal_places=5, default=0)
	uom_conversion = models.ForeignKey(UOMConversion, null=True, blank=True)
	uom = models.CharField('Purchase Unit', max_length=200, null=True, blank=True)
	whole_sale_price = models.DecimalField('Whole Sale Price', max_digits=20, decimal_places=5, default=0)
	retail_price = models.DecimalField('Retail Price', max_digits=20, decimal_places=5, default=0)
	unit_discount = models.DecimalField('Unit Discount', max_digits=20, decimal_places=5, default=0)
	unit_freight = models.DecimalField('Unit Freight', max_digits=20, decimal_places=5, default=0)

	def __unicode__(self):

		return self.purchase.purchase_invoice_number + ' - ' + self.batch_item.item.code

	class Meta:

		verbose_name_plural = 'Purchase Item'

class PurchaseReturn(models.Model):

	purchase = models.ForeignKey(Purchase, null=True, blank=True)
	return_invoice_number = models.CharField('Return Invoice Number', max_length=200, null=True, blank=True, unique=True)
	invoice_date = models.DateField('Invoice Date', null=True, blank=True)
	grant_total = models.DecimalField('Grant Total', max_digits=20, decimal_places=2, default=0)

	discount = models.DecimalField('Discount', max_digits=20, decimal_places=2, default=0)
	purchase_tax = models.DecimalField('Return Tax', max_digits=20, decimal_places=5, default=0)
	transaction_reference_no = models.CharField('Transaction Reference Number', null=True, blank=True, max_length=200)

	def __unicode__(self):
		return self.purchase.purchase_invoice_number

	class Meta:

		verbose_name_plural = 'Purchase Return'

class PurchaseReturnItem(models.Model):

	purchase_return = models.ForeignKey(PurchaseReturn)
	purchase_item = models.ForeignKey(PurchaseItem)

	quantity = models.DecimalField('Quantity', max_digits=20, decimal_places=10, default=0)
	net_amount = models.DecimalField('Net Amount', max_digits=20, decimal_places=10, default=0)

	def __unicode__(self):
		return self.purchase_item.purchase.purchase_invoice_number 

	class Meta:

		verbose_name_plural = 'Purchase Return Item'


class FreightValue(models.Model):

	freight_value = models.DecimalField('Freight', max_digits=20, decimal_places=5, null=True, blank=True)


	def __unicode__(self):
		return str(self.freight_value)

	class Meta:

		verbose_name_plural = 'Freight Value'