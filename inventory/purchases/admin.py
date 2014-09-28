from django.contrib import admin

from purchases.models import Purchase, PurchaseItem, PurchaseReturn, PurchaseReturnItem, FreightValue

class PurchaseAdmin(admin.ModelAdmin):
	search_fields = ['supplier__name']

admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(PurchaseItem)
admin.site.register(PurchaseReturn)
admin.site.register(PurchaseReturnItem)
admin.site.register(FreightValue)