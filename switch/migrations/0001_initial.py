# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MacDB'
        db.create_table('switch_macdb', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('port', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['switch.Port'])),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=18)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('first_seen', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('switch', ['MacDB'])

        # Adding model 'Switch'
        db.create_table('switch_switch', (
            ('switch_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, primary_key=True)),
            ('switch_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('switch_username', self.gf('django.db.models.fields.CharField')(default='admin', max_length=50)),
            ('switch_password', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('snmp_community', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('only_snmp', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('office', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['switch.Office'])),
        ))
        db.send_create_signal('switch', ['Switch'])

        # Adding model 'Office'
        db.create_table('switch_office', (
            ('office_name', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
        ))
        db.send_create_signal('switch', ['Office'])

        # Adding model 'Room'
        db.create_table('switch_room', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('office', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['switch.Office'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('switch', ['Room'])

        # Adding model 'Port'
        db.create_table('switch_port', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('switch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['switch.Switch'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('vlan', self.gf('django.db.models.fields.IntegerField')(default=3, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('default_vlan', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mode', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('switch', ['Port'])

        # Adding unique constraint on 'Port', fields ['switch', 'number']
        db.create_unique('switch_port', ['switch_id', 'number'])

        # Adding model 'PhysicalPort'
        db.create_table('switch_physicalport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('port', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['switch.Port'])),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['switch.Room'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('switch', ['PhysicalPort'])

        # Adding model 'PortLog'
        db.create_table('switch_portlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('port', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['switch.Port'])),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('switch', ['PortLog'])

        # Adding model 'RoomLog'
        db.create_table('switch_roomlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['switch.Room'])),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('switch', ['RoomLog'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Port', fields ['switch', 'number']
        db.delete_unique('switch_port', ['switch_id', 'number'])

        # Deleting model 'MacDB'
        db.delete_table('switch_macdb')

        # Deleting model 'Switch'
        db.delete_table('switch_switch')

        # Deleting model 'Office'
        db.delete_table('switch_office')

        # Deleting model 'Room'
        db.delete_table('switch_room')

        # Deleting model 'Port'
        db.delete_table('switch_port')

        # Deleting model 'PhysicalPort'
        db.delete_table('switch_physicalport')

        # Deleting model 'PortLog'
        db.delete_table('switch_portlog')

        # Deleting model 'RoomLog'
        db.delete_table('switch_roomlog')


    models = {
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
