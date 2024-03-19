# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Education(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    degree_name = models.CharField(max_length=255, blank=True, null=True)
    field_of_study = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.CharField(max_length=10, blank=True, null=True)
    end_date = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'education'


class Experience(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.CharField(max_length=10, blank=True, null=True)
    end_date = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'experience'


class User(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    headline = models.TextField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'
