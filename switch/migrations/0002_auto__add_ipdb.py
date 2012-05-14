# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'IPDB'
        db.create_table('switch_ipdb', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=18)),
            ('first_seen', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('updated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('switch', ['IPDB'])


    def backwards(self, orm):
        
        # Deleting model 'IPDB'
        db.delete_table('switch_ipdb')


    models = {
        'switch.ipdb': {
            'Meta': {'object_name': 'IPDB'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'updated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'switch.macdb': {
            'Meta': {'object_name': 'MacDB'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'port': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['switch.Port']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'switch.office': {
            'Meta': {'object_name': 'Office'},
            'office_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        'switch.physicalport': {
            'Meta': {'ordering': "['name']", 'object_name': 'PhysicalPort'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'port': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['switch.Port']"}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['switch.Room']", 'null': 'True', 'blank': 'True'})
        },
        'switch.port': {
            'Meta': {'ordering': "['switch__switch_name', 'number']", 'unique_together': "(('switch', 'number'),)", 'object_name': 'Port'},
            'default_vlan': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'switch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['switch.Switch']"}),
            'vlan': ('django.db.models.fields.IntegerField', [], {'default': '3', 'null': 'True', 'blank': 'True'})
        },
        'switch.portlog': {
            'Meta': {'ordering': "['-created']", 'object_name': 'PortLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['switch.Port']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'switch.room': {
            'Meta': {'object_name': 'Room'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'office': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['switch.Office']"})
        },
        'switch.roomlog': {
            'Meta': {'ordering': "['-created']", 'object_name': 'RoomLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['switch.Room']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'switch.switch': {
            'Meta': {'object_name': 'Switch'},
            'office': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['switch.Office']"}),
            'only_snmp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'snmp_community': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'switch_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'primary_key': 'True'}),
            'switch_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'switch_password': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'switch_username': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '50'})
        }
    }

    complete_apps = ['switch']
