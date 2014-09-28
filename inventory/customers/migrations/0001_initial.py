# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Customer'
        db.create_table(u'customers_customer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ledger', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounting.Ledger'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('telephone_number', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'customers', ['Customer'])

    def backwards(self, orm):
        # Deleting model 'Customer'
        db.delete_table(u'customers_customer')

    models = {
        u'accounting.ledger': {
            'Meta': {'object_name': 'Ledger'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
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
        }
    }

    complete_apps = ['customers']