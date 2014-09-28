# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Transaction.credit_amount'
        db.alter_column(u'accounting_transaction', 'credit_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Transaction.debit_amount'
        db.alter_column(u'accounting_transaction', 'debit_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))
    def backwards(self, orm):

        # Changing field 'Transaction.credit_amount'
        db.alter_column(u'accounting_transaction', 'credit_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2))

        # Changing field 'Transaction.debit_amount'
        db.alter_column(u'accounting_transaction', 'debit_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2))
    models = {
        u'accounting.ledger': {
            'Meta': {'object_name': 'Ledger'},
            'balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '5'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounting.Ledger']", 'null': 'True', 'blank': 'True'})
        },
        u'accounting.ledgerentry': {
            'Meta': {'object_name': 'LedgerEntry'},
            'credit_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'debit_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ledger': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounting.Ledger']"}),
            'transaction_reference_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'accounting.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'card_holder_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'card_no': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cheque_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cheque_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'credit_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'credit_ledger': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'credit_ledger'", 'null': 'True', 'to': u"orm['accounting.LedgerEntry']"}),
            'debit_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'debit_ledger': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'debit_ledger'", 'null': 'True', 'to': u"orm['accounting.LedgerEntry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'narration': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'payment_mode': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'transaction_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'transaction_ref': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['accounting']