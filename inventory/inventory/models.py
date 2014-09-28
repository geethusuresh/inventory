from django.db import models

# Create your models here.

class Category(models.Model):

    parent = models.ForeignKey('self', null=True, blank=True)
    name = models.CharField('Name', max_length=200, null=True, blank=True, unique=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Category'
    

class Product(models.Model):

    category = models.ForeignKey(Category)
    name = models.CharField('Name', max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Product'
    

class Brand(models.Model):

    name = models.CharField('Name', max_length=200, null=True, blank=True, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Brand'


class VatType(models.Model):

    vat_type = models.CharField('Vat Type', max_length=200, null=True, blank=True)
    tax_percentage = models.DecimalField('Tax Percentage', max_digits=14, decimal_places=2, default=0)

    def __unicode__(self):
        return self.vat_type

    class Meta:
        verbose_name_plural = 'Vat Type'


class Item(models.Model):

    vat_type = models.ForeignKey(VatType, null=True, blank=True)
    product = models.ForeignKey(Product, null=True, blank=True)
    brand = models.ForeignKey(Brand, null=True, blank=True)

    name = models.CharField('Name', max_length=200, null=True, blank=True)
    code = models.CharField('Code', max_length=200, unique=True, blank=True)
    cess = models.DecimalField('Cess', max_digits=14, decimal_places=2, default=0)
    size = models.CharField('Size', max_length=200, null=True, blank=True)
    barcode = models.CharField('Barcode', max_length=200, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    offer_quantity = models.DecimalField('Quantity', default=0, max_digits=50, decimal_places=5)
    
    def save(self, *args, **kwargs):
        if self.product and self.brand and self.name:
            self.code = self.product.name[:3] + self.brand.name[:3] + self.name[:3]
        else:
            self.code = self.name[:3] + self.pk
        try:
            if self.pk == None:
                super(Item, self).save()
            self.code = self.product.name[:3] + self.brand.name[:3] + self.name[:3] + str(self.pk)
            super(Item, self).save()
        except Exception as ex:
            print str(ex)
    def __unicode__(self):
        return str(self.code)

    class Meta:
        verbose_name_plural = 'Item'

class Batch(models.Model):

    name = models.CharField('Batch name', max_length=200)
    created_date = models.DateField('Created', null=True, blank=True)
    expiry_date = models.DateField('Expiry date', null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Batch'



UOM_STATUS_CHOICES = (
    ('used', 'used'),
    ('not used', 'not used')
)
class UOMConversion(models.Model):

    purchase_unit = models.CharField('Purchase Unit', max_length=50)
    selling_unit = models.CharField('Selling Unit', max_length=50)
    relation = models.DecimalField('Relation with selling unit', default=0, max_digits=50, decimal_places=5)
    status = models.CharField('Status', default='not used', choices=UOM_STATUS_CHOICES, max_length=15)
    
    def __unicode__(self):
        return self.purchase_unit + '-' + self.selling_unit + "-" + str(self.relation)

    class Meta:
        verbose_name_plural = 'UOM Conversions'


class BatchItem(models.Model):

    batch = models.ForeignKey(Batch, null=True, blank=True)
    item = models.ForeignKey(Item, null=True, blank=True)

    quantity = models.DecimalField('Quantity', default=0, max_digits=50, decimal_places=5)
    purchase_price = models.DecimalField('Purchase Price', default=0, max_digits=50, decimal_places=5)
    cost_price = models.DecimalField('Cost Price', default=0, max_digits=50, decimal_places=5)
    uom_conversion = models.ForeignKey(UOMConversion, null=True, blank=True)
    uom = models.CharField('UOM', max_length=200, null=True, blank=True)
    whole_sale_price = models.DecimalField('Whole Sale Price', max_digits=20, decimal_places=5, default=0)
    retail_price = models.DecimalField('Retail Price', max_digits=20, decimal_places=5, default=0)
    freight_charge = models.DecimalField('Freight charge', max_digits=20, decimal_places=5, default=0)

    def __unicode__(self):
        return self.batch.name + ' - ' + self.item.code+ ' - ' + self.item.name

    class Meta:
        verbose_name_plural = 'Batch Item'

class OpeningStock(models.Model):

    date = models.DateField('Date',null=True, blank=True)
    transaction_reference_no = models.CharField('Transaction Reference Number', null=True, blank=True, max_length=200)

    def __unicode__(self):
        return str(self.date)+ ' - ' + self.transaction_reference_no

    class Meta:
        verbose_name_plural = 'Opening Stock'


class OpeningStockItem(models.Model):

    opening_stock = models.ForeignKey(OpeningStock, null=True, blank=True)
    batch_item = models.ForeignKey(BatchItem, null=True, blank=True)

    quantity = models.DecimalField('Quantity', max_digits=20, decimal_places=5, default=0)
    uom = models.CharField('Uom', max_length=200, null=True, blank=True)
    purchase_price = models.DecimalField('Purchase Price', max_digits=20, decimal_places=5, default=0)
    whole_sale_price = models.DecimalField('Whole Sale Price', max_digits=20, decimal_places=5, default=0)
    retail_price = models.DecimalField('Retail Price', max_digits=20, decimal_places=5, default=0)
    net_amount = models.DecimalField('Net Amount', max_digits=20, decimal_places=5, default=0)
    
    def __unicode__(self):
        return str(self.opening_stock.date) + ' - ' + self.opening_stock.transaction_reference_no

    class Meta:
        verbose_name_plural = 'Opening Stock Item'

class StockValue(models.Model):

    stock_by_value = models.DecimalField('Balance', max_digits=20, null=True, blank=True, decimal_places=5)

    def __unicode__(self):
        return str(self.stock_by_value)
    class Meta:
        verbose_name_plural = 'Stock Value'

class OpeningStockValue(models.Model):

    stock_by_value = models.DecimalField('Balance', max_digits=20, null=True, blank=True, decimal_places=5)

    def __unicode__(self):
        return str(self.stock_by_value)
    class Meta:
        verbose_name_plural = 'Opening Stock Value'