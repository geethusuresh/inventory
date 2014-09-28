# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BatchItem.smallest_uom_quantity'
        db.add_column(u'inventory_batchitem', 'smallest_uom_quantity',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2),
                      keep_default=False)

        # Adding field 'BatchItem.smallest_uom_selling_price'
        db.add_column(u'inventory_batchitem', 'smallest_uom_selling_price',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2),
                      keep_default=False)

        # Adding field 'BatchItem.smallest_uom_purchase_price'
        db.add_column(u'inventory_batchitem', 'smallest_uom_purchase_price',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2),
                      keep_default=False)

        # Adding field 'BatchItem.smallest_uom'
        db.add_column(u'inventory_batchitem', 'smallest_uom',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)


        # Changing field 'BatchItem.batch'
        db.alter_column(u'inventory_batchitem', 'batch_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Batch'], null=True))

        # Changing field 'BatchItem.item'
        db.alter_column(u'inventory_batchitem', 'item_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Item'], null=True))
    def backwards(self, orm):
        # Deleting field 'BatchItem.smallest_uom_quantity'
        db.delete_column(u'inventory_batchitem', 'smallest_uom_quantity')

        # Deleting field 'BatchItem.smallest_uom_selling_price'
        db.delete_column(u'inventory_batchitem', 'smallest_uom_selling_price')

        # Deleting field 'BatchItem.smallest_uom_purchase_price'
        db.delete_column(u'inventory_batchitem', 'smallest_uom_purchase_price')

        # Deleting field 'BatchItem.smallest_uom'
        db.delete_column(u'inventory_batchitem', 'smallest_uom')


        # User chose to not deal with backwards NULL issues for 'BatchItem.batch'
        raise RuntimeError("Cannot reverse this migration. 'BatchItem.batch' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'BatchItem.item'
        raise RuntimeError("Cannot reverse this migration. 'BatchItem.item' and its values cannot be restored.")
    models = {
        u'inventory.batch': {
            'Meta': {'object_name': 'Batch'},
            'created_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'inventory.batchitem': {
            'Meta': {'object_name': 'BatchItem'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Batch']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Item']", 'null': 'True', 'blank': 'True'}),
            'purchase_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'selling_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'smallest_uom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'smallest_uom_purchase_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'smallest_uom_quantity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'smallest_uom_selling_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'uom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
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
        }
    }

    complete_apps = ['inventory']