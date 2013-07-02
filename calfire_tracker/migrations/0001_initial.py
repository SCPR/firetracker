# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CalWildfire'
        db.create_table('calfire_tracker_calwildfire', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_fire_id', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('twitter_hashtag', self.gf('django.db.models.fields.CharField')(max_length=140, null=True, blank=True)),
            ('fire_name', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('location_latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('location_longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('location_geocode_error', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('administrative_unit', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('more_info', self.gf('django.db.models.fields.URLField')(max_length=1024, null=True, blank=True)),
            ('acres_burned', self.gf('django.db.models.fields.IntegerField')(max_length=8, null=True, blank=True)),
            ('containment_percent', self.gf('django.db.models.fields.IntegerField')(max_length=4, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_time_started', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('phone_numbers', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True, blank=True)),
            ('evacuations', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True, blank=True)),
            ('structures_threatened', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('injuries', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('road_closures', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True, blank=True)),
            ('structures_destroyed', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('total_dozers', self.gf('django.db.models.fields.IntegerField')(max_length=10, null=True, blank=True)),
            ('total_helicopters', self.gf('django.db.models.fields.IntegerField')(max_length=10, null=True, blank=True)),
            ('total_fire_engines', self.gf('django.db.models.fields.IntegerField')(max_length=10, null=True, blank=True)),
            ('total_fire_personnel', self.gf('django.db.models.fields.IntegerField')(max_length=10, null=True, blank=True)),
            ('total_water_tenders', self.gf('django.db.models.fields.IntegerField')(max_length=10, null=True, blank=True)),
            ('cause', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True, blank=True)),
            ('total_airtankers', self.gf('django.db.models.fields.IntegerField')(max_length=10, null=True, blank=True)),
            ('conditions', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('cooperating_agencies', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True, blank=True)),
            ('total_fire_crews', self.gf('django.db.models.fields.IntegerField')(max_length=10, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True, blank=True)),
            ('last_scraped', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('calfire_tracker', ['CalWildfire'])


    def backwards(self, orm):
        # Deleting model 'CalWildfire'
        db.delete_table('calfire_tracker_calwildfire')


    models = {
        'calfire_tracker.calwildfire': {
            'Meta': {'object_name': 'CalWildfire'},
            'acres_burned': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'administrative_unit': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'cause': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'conditions': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'containment_percent': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'cooperating_agencies': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'created_fire_id': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'date_time_started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'evacuations': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'fire_name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'injuries': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'last_scraped': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'location_geocode_error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'location_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'more_info': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'phone_numbers': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'road_closures': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'structures_destroyed': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'structures_threatened': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'total_airtankers': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_dozers': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_fire_crews': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_fire_engines': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_fire_personnel': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_helicopters': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_water_tenders': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'twitter_hashtag': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['calfire_tracker']