# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CalWildfire.current_situation'
        db.add_column('calfire_tracker_calwildfire', 'current_situation',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'CalWildfire.damage_assessment'
        db.add_column('calfire_tracker_calwildfire', 'damage_assessment',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'CalWildfire.training'
        db.add_column('calfire_tracker_calwildfire', 'training',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


        # Changing field 'CalWildfire.evacuations'
        db.alter_column('calfire_tracker_calwildfire', 'evacuations', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'CalWildfire.phone_numbers'
        db.alter_column('calfire_tracker_calwildfire', 'phone_numbers', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'CalWildfire.road_closures'
        db.alter_column('calfire_tracker_calwildfire', 'road_closures', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'CalWildfire.location'
        db.alter_column('calfire_tracker_calwildfire', 'location', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'CalWildfire.computed_location'
        db.alter_column('calfire_tracker_calwildfire', 'computed_location', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'CalWildfire.cause'
        db.alter_column('calfire_tracker_calwildfire', 'cause', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'CalWildfire.notes'
        db.alter_column('calfire_tracker_calwildfire', 'notes', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'CalWildfire.cooperating_agencies'
        db.alter_column('calfire_tracker_calwildfire', 'cooperating_agencies', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):
        # Deleting field 'CalWildfire.current_situation'
        db.delete_column('calfire_tracker_calwildfire', 'current_situation')

        # Deleting field 'CalWildfire.damage_assessment'
        db.delete_column('calfire_tracker_calwildfire', 'damage_assessment')

        # Deleting field 'CalWildfire.training'
        db.delete_column('calfire_tracker_calwildfire', 'training')


        # Changing field 'CalWildfire.evacuations'
        db.alter_column('calfire_tracker_calwildfire', 'evacuations', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True))

        # Changing field 'CalWildfire.phone_numbers'
        db.alter_column('calfire_tracker_calwildfire', 'phone_numbers', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True))

        # Changing field 'CalWildfire.road_closures'
        db.alter_column('calfire_tracker_calwildfire', 'road_closures', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True))

        # Changing field 'CalWildfire.location'
        db.alter_column('calfire_tracker_calwildfire', 'location', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True))

        # Changing field 'CalWildfire.computed_location'
        db.alter_column('calfire_tracker_calwildfire', 'computed_location', self.gf('django.db.models.fields.TextField')(max_length=255, null=True))

        # Changing field 'CalWildfire.cause'
        db.alter_column('calfire_tracker_calwildfire', 'cause', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True))

        # Changing field 'CalWildfire.notes'
        db.alter_column('calfire_tracker_calwildfire', 'notes', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True))

        # Changing field 'CalWildfire.cooperating_agencies'
        db.alter_column('calfire_tracker_calwildfire', 'cooperating_agencies', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True))

    models = {
        'calfire_tracker.calwildfire': {
            'Meta': {'object_name': 'CalWildfire'},
            'acres_burned': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'administrative_unit': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'cause': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'computed_location': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'conditions': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'containment_percent': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'cooperating_agencies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'created_fire_id': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'current_situation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'damage_assessment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_time_started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'evacuations': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fire_name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'fire_slug': ('django.db.models.fields.SlugField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'injuries': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'last_scraped': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'location_geocode_error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'location_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'more_info': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'phone_numbers': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'promoted_fire': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'road_closures': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'structures_destroyed': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'structures_threatened': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'total_airtankers': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_dozers': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_fire_crews': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_fire_engines': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_fire_personnel': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_helicopters': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'total_water_tenders': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'training': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'twitter_hashtag': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['calfire_tracker']