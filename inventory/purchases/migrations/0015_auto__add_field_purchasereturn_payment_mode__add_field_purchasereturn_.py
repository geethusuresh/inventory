# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PurchaseReturn.payment_mode'
        db.add_column(u'purchases_purchasereturn', 'payment_mode',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'PurchaseReturn.bank_name'
        db.add_column(u'purchases_purchasereturn', 'bank_name',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'PurchaseReturn.card_number'
        db.add_column(u'purchases_purchasereturn', 'card_number',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'PurchaseReturn.cheque_date'
        db.add_column(u'purchases_purchasereturn', 'cheque_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'PurchaseReturn.cheque_number'
        db.add_column(u'purchases_purchasereturn', 'cheque_number',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'PurchaseReturn.branch'
        db.add_column(u'purchases_purchasereturn', 'branch',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'PurchaseReturn.card_holder_name'
        db.add_column(u'purchases_purchasereturn', 'card_holder_name',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)


        # Changing field 'PurchaseReturn.purchase'
        db.alter_column(u'purchases_purchasereturn', 'purchase_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['purchases.Purchase'], null=True))
    def backwards(self, orm):
        # Deleting field 'PurchaseReturn.payment_mode'
        db.delete_column(u'purchases_purchasereturn', 'payment_mode')

        # Deleting field 'PurchaseReturn.bank_name'
        db.delete_column(u'purchases_purchasereturn', 'bank_name')

        # Deleting field 'PurchaseReturn.card_number'
        db.delete_column(u'purchases_purchasereturn', 'card_number')

        # Deleting field 'PurchaseReturn.cheque_date'
        db.delete_column(u'purchases_purchasereturn', 'cheque_date')

        # Deleting field 'PurchaseReturn.cheque_number'
        db.delete_column(u'purchases_purchasereturn', 'cheque_number')

        # Deleting field 'PurchaseReturn.branch'
        db.delete_column(u'purchases_purchasereturn', 'branch')

        # Deleting field 'PurchaseReturn.card_holder_name'
        db.delete_column(u'purchases_purchasereturn', 'card_holder_name')


        # User chose to not deal with backwards NULL issues for 'PurchaseReturn.purchase'
        raise RuntimeError("Cannot reverse this migration. 'PurchaseReturn.purchase' and its values cannot be restored.")
    models = {
        u'accounting.ledger': {
            'Meta': {'object_name': 'Ledger'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounting.Ledger']", 'null': 'True', 'blank': 'True'})
        },
        u'inventory.batch': {
            'Meta': {'object_name': 'Batch'},
            'created_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'inventory.brand': {
            'Meta': {'object_name': 'Brand'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'inventory.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Category']", 'null': 'True', 'blank': 'True'})
        },
        u'inventory.item': {
            'Meta': {'object_name': 'Item'},
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Brand']"}),
            'cess': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Product']"}),
            'size': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'uom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'vat_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.VatType']", 'null': 'True', 'blank': 'True'})
        },
        u'inventory.product': {
            'Meta': {'object_name': 'Product'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'inventory.vattype': {
            'Meta': {'object_name': 'VatType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tax_percentage': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'vat_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'purchases.purchase': {
            'Meta': {'object_name': 'Purchase'},
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'card_holder_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'card_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cheque_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cheque_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'discount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'do_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'grant_total': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_mode': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'purchase_invoice_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'purchase_invoice_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['suppliers.Supplier']", 'null': 'True', 'blank': 'True'})
        },
        u'purchases.purchaseitem': {
            'Meta': {'object_name': 'PurchaseItem'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Batch']", 'null': 'True', 'blank': 'True'}),
            'cost_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Item']", 'null': 'True', 'blank': 'True'}),
            'net_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'}),
            'profit': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'}),
            'purchase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['purchases.Purchase']", 'null': 'True', 'blank': 'True'}),
            'purchase_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'}),
            'selling_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'}),
            'uom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'purchases.purchasereturn': {
            'Meta': {'object_name': 'PurchaseReturn'},
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'card_holder_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'card_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cheque_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cheque_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'grant_total': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'payment_mode': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'purchase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['purchases.Purchase']", 'null': 'True', 'blank': 'True'}),
            'return_invoice_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'purchases.purchasereturnitem': {
            'Meta': {'object_name': 'PurchaseReturnItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'net_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'}),
            'purchase_item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['purchases.PurchaseItem']"}),
            'purchase_return': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['purchases.PurchaseReturn']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'})
        },
        u'suppliers.supplier': {
            'Meta': {'object_name': 'Supplier'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ledger': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounting.Ledger']", 'null': 'True', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'telephone_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['purchases']