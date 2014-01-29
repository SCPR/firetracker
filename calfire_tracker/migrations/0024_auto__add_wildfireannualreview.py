# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WildfireAnnualReview'
        db.create_table('calfire_tracker_wildfireannualreview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(max_length=4, null=True, blank=True)),
            ('date_range_beginning', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('date_range_end', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('acres_burned', self.gf('django.db.models.fields.IntegerField')(max_length=8, null=True, blank=True)),
            ('number_of_fires', self.gf('django.db.models.fields.IntegerField')(max_length=10, null=True, blank=True)),
            ('dollar_damage', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=2, blank=True)),
            ('injuries', self.gf('django.db.models.fields.CharField')(max_length=2024, null=True, blank=True)),
            ('structures_threatened', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('structures_destroyed', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('administrative_unit', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('jurisdiction', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('last_saved', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('calfire_tracker', ['WildfireAnnualReview'])


    def backwards(self, orm):
        # Deleting model 'WildfireAnnualReview'
        db.delete_table('calfire_tracker_wildfireannualreview')


    models = {
        'calfire_tracker.calwildfire': {
            'Meta': {'object_name': 'CalWildfire'},
            'acres_burned': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'administrative_unit': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'air_quality_rating': ('django.db.models.fields.IntegerField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'asset_host_image_id': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'}),
            'asset_photo_credit': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'asset_url_link': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'cause': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'computed_location': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'conditions': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'containment_percent': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'cooperating_agencies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'county_slug': ('django.db.models.fields.SlugField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'}),
            'created_fire_id': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'current_situation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'damage_assessment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'date_time_started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'evacuations': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fire_name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'fire_slug': ('django.db.models.fields.SlugField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'}),
            'historical_narrative': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'injuries': ('django.db.models.fields.CharField', [], {'max_length': '2024', 'null': 'True', 'blank': 'True'}),
            'last_saved': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_scraped': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'location_geocode_error': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'location_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'location_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'more_info': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'perimeters_image': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'phone_numbers': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'promoted_fire': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'road_closures': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'school_closures': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
            'twitter_hashtag': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'}),
            'update_lockout': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'year': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'})
        },
        'calfire_tracker.wildfireannualreview': {
            'Meta': {'object_name': 'WildfireAnnualReview'},
            'acres_burned': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'administrative_unit': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'date_range_beginning': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_range_end': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dollar_damage': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'injuries': ('django.db.models.fields.CharField', [], {'max_length': '2024', 'null': 'True', 'blank': 'True'}),
            'jurisdiction': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'last_saved': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'number_of_fires': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'structures_destroyed': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'structures_threatened': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'})
        },
        'calfire_tracker.wildfiretweet': {
            'Meta': {'object_name': 'WildfireTweet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tweet_created_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'tweet_hashtag': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'tweet_id': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'tweet_profile_image_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'tweet_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'tweet_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'calfire_tracker.wildfireupdate': {
            'Meta': {'object_name': 'WildfireUpdate'},
            'date_time_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fire_name': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calwildfire_fire_name'", 'null': 'True', 'to': "orm['calfire_tracker.CalWildfire']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'update_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['calfire_tracker']