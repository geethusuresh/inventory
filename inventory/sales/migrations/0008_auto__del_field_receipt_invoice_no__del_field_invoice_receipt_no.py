# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Receipt.invoice_no'
        db.delete_column(u'sales_receipt', 'invoice_no')

        # Deleting field 'Invoice.receipt_no'
        db.delete_column(u'sales_invoice', 'receipt_no')

    def backwards(self, orm):
        # Adding field 'Receipt.invoice_no'
        db.add_column(u'sales_receipt', 'invoice_no',
                      self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Invoice.receipt_no'
        db.add_column(u'sales_invoice', 'receipt_no',
                      self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, null=True, blank=True),
                      keep_default=False)

    models = {
        u'accounting.ledger': {
            'Meta': {'object_name': 'Ledger'},
            'balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '5'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounting.Ledger']", 'null': 'True', 'blank': 'True'})
        },
        u'customers.customer': {
            'Meta': {'object_name': 'Customer'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ledger': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounting.Ledger']", 'null': 'True', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'telephone_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
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
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Brand']", 'null': 'True', 'blank': 'True'}),
            'cess': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'offer_quantity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '50', 'decimal_places': '5'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Product']", 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
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
        u'sales.invoice': {
            'Meta': {'object_name': 'Invoice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_no': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'invoice_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'sales': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sales.Sale']"})
        },
        u'sales.receipt': {
            'Meta': {'object_name': 'Receipt'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receipt_no': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'sales': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sales.Sale']"})
        },
        u'sales.sale': {
            'Meta': {'object_name': 'Sale'},
            'auto_invoice_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'bill_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'card_holder_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'card_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cheque_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cheque_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['customers.Customer']", 'null': 'True', 'blank': 'True'}),
            'discount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'do_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'grant_total': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_mode': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'sales_invoice_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'sales_invoice_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'salesman': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Salesman']", 'null': 'True', 'blank': 'True'}),
            'transaction_reference_no': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'sales.salesitem': {
            'Meta': {'object_name': 'SalesItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Item']"}),
            'mrp': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'}),
            'net_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '10'}),
            'sales': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sales.Sale']"}),
            'uom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'web.salesman': {
            'Meta': {'object_name': 'Salesman'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'contact_no': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'})
        }
    }

    complete_apps = ['sales']