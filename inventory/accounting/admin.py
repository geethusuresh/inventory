from django.contrib import admin

from accounting.models import Ledger, LedgerEntry, Transaction

admin.site.register(Ledger)
admin.site.register(LedgerEntry)
admin.site.register(Transaction)
