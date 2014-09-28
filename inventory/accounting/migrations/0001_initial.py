# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Ledger'
        db.create_table(u'accounting_ledger', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounting.Ledger'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'accounting', ['Ledger'])

        # Adding model 'LedgerEntry'
        db.create_table(u'accounting_ledgerentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ledger', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounting.Ledger'])),
            ('credit_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2, blank=True)),
            ('debit_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'accounting', ['LedgerEntry'])

        # Adding model 'Transaction'
        db.create_table(u'accounting_transaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('debit_ledger', self.gf('django.db.models.fields.related.ForeignKey')(related_name='debit_ledger', to=orm['accounting.Ledger'])),
            ('credit_ledger', self.gf('django.db.models.fields.related.ForeignKey')(related_name='credit_ledger', to=orm['accounting.Ledger'])),
            ('transaction_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('narration', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('payment_mode', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('bank_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('cheque_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('cheque_number', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('branch', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('card_holder_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('card_no', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'accounting', ['Transaction'])

    def backwards(self, orm):
        # Deleting model 'Ledger'
        db.delete_table(u'accounting_ledger')

        # Deleting model 'LedgerEntry'
        db.delete_table(u'accounting_ledgerentry')

        # Deleting model 'Transaction'
        db.delete_table(u'accounting_transaction')

    models = {
        u'accounting.ledger': {
            'Meta': {'object_name': 'Ledger'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounting.Ledger']", 'null': 'True', 'blank': 'True'})
        },
        u'accounting.ledgerentry': {
            'Meta': {'object_name': 'LedgerEntry'},
            'credit_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'debit_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ledger': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounting.Ledger']"})
        },
        u'accounting.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'card_holder_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'card_no': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cheque_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cheque_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'credit_ledger': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'credit_ledger'", 'to': u"orm['accounting.Ledger']"}),
            'debit_ledger': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'debit_ledger'", 'to': u"orm['accounting.Ledger']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'narration': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'payment_mode': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'transaction_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['accounting']