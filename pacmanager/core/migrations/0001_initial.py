# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Setting'
        db.create_table('core_setting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('core', ['Setting'])

        # Adding model 'Character'
        db.create_table('core_character', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('core', ['Character'])

        # Adding model 'Corporation'
        db.create_table('core_corporation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tax_rate', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('ceo', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['core.Character'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='corporations', null=True, to=orm['auth.User'])),
            ('balance', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=25, decimal_places=2)),
            ('last_transaction', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('payment_id', self.gf('django.db.models.fields.CharField')(default=UUID('2bd5462c-28d9-4fed-b0d1-e835c6954c57'), max_length=36)),
        ))
        db.send_create_signal('core', ['Corporation'])

        # Adding model 'MonthTotal'
        db.create_table('core_monthtotal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('month', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('corporation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='totals', to=orm['core.Corporation'])),
            ('tax', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=25, decimal_places=2)),
            ('charged', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['MonthTotal'])

        # Adding model 'Transaction'
        db.create_table('core_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corporation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transactions', to=orm['core.Corporation'])),
            ('type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=25, decimal_places=2)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('core', ['Transaction'])

        # Adding model 'Key'
        db.create_table('core_key', (
            ('corporation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='keys', to=orm['core.Corporation'])),
            ('keyid', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('vcode', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('mask', self.gf('django.db.models.fields.BigIntegerField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('core', ['Key'])

        # Adding model 'APICache'
        db.create_table('core_apicache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('cache_until', self.gf('django.db.models.fields.DateTimeField')()),
            ('document', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('core', ['APICache'])

    def backwards(self, orm):
        # Deleting model 'Setting'
        db.delete_table('core_setting')

        # Deleting model 'Character'
        db.delete_table('core_character')

        # Deleting model 'Corporation'
        db.delete_table('core_corporation')

        # Deleting model 'MonthTotal'
        db.delete_table('core_monthtotal')

        # Deleting model 'Transaction'
        db.delete_table('core_transaction')

        # Deleting model 'Key'
        db.delete_table('core_key')

        # Deleting model 'APICache'
        db.delete_table('core_apicache')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.apicache': {
            'Meta': {'object_name': 'APICache'},
            'cache_until': ('django.db.models.fields.DateTimeField', [], {}),
            'document': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'core.character': {
            'Meta': {'object_name': 'Character'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.corporation': {
            'Meta': {'object_name': 'Corporation'},
            'balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '25', 'decimal_places': '2'}),
            'ceo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['core.Character']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'corporations'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_transaction': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'payment_id': ('django.db.models.fields.CharField', [], {'default': "UUID('84a11b5a-467e-496e-96b4-ffdfc6bb5a2b')", 'max_length': '36'}),
            'tax_rate': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'core.key': {
            'Meta': {'object_name': 'Key'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'keys'", 'to': "orm['core.Corporation']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'keyid': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'mask': ('django.db.models.fields.BigIntegerField', [], {}),
            'update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'vcode': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'core.monthtotal': {
            'Meta': {'ordering': "['-year', '-month']", 'object_name': 'MonthTotal'},
            'charged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'totals'", 'to': "orm['core.Corporation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '25', 'decimal_places': '2'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'core.setting': {
            'Meta': {'object_name': 'Setting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'core.transaction': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Transaction'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': "orm['core.Corporation']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '25', 'decimal_places': '2'})
        }
    }

    complete_apps = ['core']