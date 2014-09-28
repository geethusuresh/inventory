from django.db import models

CHOICES = (
    ('cash', 'Cash'),
    ('card', 'Card'),
    ('cheque', 'Cheque'),
    ('credit', 'Credit'),
)

class Ledger(models.Model):
	parent = models.ForeignKey("self", null=True, blank=True)
	name = models.CharField("Name", max_length=200, null=True, blank=True, unique=False)
	description = models.CharField("Description", max_length=200, null=True, blank=True)
	balance = models.DecimalField('Balance', max_digits=20, default=0, decimal_places=5)

	def __unicode__(self):
		return self.name


class LedgerEntry(models.Model):
	ledger = models.ForeignKey(Ledger)
	credit_amount = models.DecimalField("Credit Amount", max_digits=14, null=True, blank=True, decimal_places=2)
	debit_amount = models.DecimalField("Debit Amount", max_digits=14, null=True, blank=True, decimal_places=2)
	date = models.DateField("Date", null=True, blank=True)
	transaction_reference_number = models.CharField("Transaction Reference", max_length=200, null=True, blank=True)
	
	def __unicode__(self):
		return self.ledger.name + (('-' + self.transaction_reference_number) if self.transaction_reference_number else '')


class Transaction(models.Model):
	transaction_ref = models.CharField("Transaction Reference", max_length=200, null=True, blank=True)
	debit_ledger = models.ForeignKey(LedgerEntry, related_name="debit_ledger", null=True, blank=True)
	credit_ledger = models.ForeignKey(LedgerEntry, related_name="credit_ledger", null=True, blank=True)
	transaction_date = models.DateField("Date of Transaction", null=True, blank=True)
	debit_amount = models.DecimalField("Debit Amount", max_digits=14, null=True, blank=True, decimal_places=2)
	credit_amount = models.DecimalField("Credit Amount", max_digits=14, null=True, blank=True, decimal_places=2)
	narration = models.TextField("Narration", null=True, blank=True)
	payment_mode = models.CharField("Payment Mode", max_length=200, choices=CHOICES)
	bank_name = models.CharField("Bank Name", max_length=200, null=True, blank=True)
	cheque_date = models.DateField("Cheque Date", null=True, blank=True)
	cheque_number = models.CharField("Cheque Number", max_length=200, null=True, blank=True)
	branch = models.CharField("Branch", max_length=200, null=True, blank=True)
	card_holder_name = models.CharField("Card Holder Name", max_length=200, null=True, blank=True)
	card_no = models.CharField("Card Number", max_length=200,null=True, blank=True)

	def __unicode__(self):
		return (self.debit_ledger.ledger.name) if self.debit_ledger else self.credit_ledger.ledger.name


