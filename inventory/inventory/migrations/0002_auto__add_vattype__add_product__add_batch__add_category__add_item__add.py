# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VatType'
        db.create_table(u'inventory_vattype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vat_type', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('tax_percentage', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
        ))
        db.send_create_signal(u'inventory', ['VatType'])

        # Adding model 'Product'
        db.create_table(u'inventory_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Category'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Product'])

        # Adding model 'Batch'
        db.create_table(u'inventory_batch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('expiry_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Batch'])

        # Adding model 'Category'
        db.create_table(u'inventory_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Category'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Category'])

        # Adding model 'Item'
        db.create_table(u'inventory_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vat_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.VatType'], null=True, blank=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Product'])),
            ('brand', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Brand'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('uom', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('cess', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('size', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('barcode', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Item'])

        # Adding model 'BatchItem'
        db.create_table(u'inventory_batchitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('batch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Batch'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Item'])),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('selling_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('purchase_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
        ))
        db.send_create_signal(u'inventory', ['BatchItem'])

        # Adding model 'Brand'
        db.create_table(u'inventory_brand', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['Brand'])

    def backwards(self, orm):
        # Deleting model 'VatType'
        db.delete_table(u'inventory_vattype')

        # Deleting model 'Product'
        db.delete_table(u'inventory_product')

        # Deleting model 'Batch'
        db.delete_table(u'inventory_batch')

        # Deleting model 'Category'
        db.delete_table(u'inventory_category')

        # Deleting model 'Item'
        db.delete_table(u'inventory_item')

        # Deleting model 'BatchItem'
        db.delete_table(u'inventory_batchitem')

        # Deleting model 'Brand'
        db.delete_table(u'inventory_brand')

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
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Batch']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Item']"}),
            'purchase_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'selling_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'})
        },
        u'inventory.brand': {
            'Meta': {'object_name': 'Brand'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'inventory.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Category']"})
        },
        u'inventory.item': {
            'Meta': {'object_name': 'Item'},
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Brand']"}),
            'cess': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
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