from django.contrib import admin

from inventory.models import Category, Product, Brand, VatType, Item, BatchItem, Batch, UOMConversion, \
OpeningStock, OpeningStockItem, StockValue, OpeningStockValue

admin.site.register(VatType)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Batch)
admin.site.register(BatchItem)
admin.site.register(Item)
admin.site.register(UOMConversion)
admin.site.register(OpeningStock)
admin.site.register(OpeningStockItem)
admin.site.register(StockValue)
admin.site.register(OpeningStockValue)