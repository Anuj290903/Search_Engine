from django.db import models

class MyUser(models.Model):
    first_name = models.CharField(max_length=255, db_column='first_name', null=True)
    last_name = models.CharField(max_length=255, db_column='last_name', null=True)
    username = models.CharField(max_length=255, db_column='username', null=True)
    headline = models.TextField(db_column='headline', null=True)
    location = models.TextField(db_column='location', null=True)

    class Meta:
        managed = False
        db_table = 'user'

class MyEducation(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, db_column='user_id')
    school_name = models.CharField(max_length=255, db_column='school_name', null=True)

    class Meta:
        managed = False
        db_table = 'education'

class MyExperience(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, db_column='user_id')
    title = models.CharField(max_length=255, db_column='title', null=True)
    company_name = models.CharField(max_length=255, db_column='company_name', null=True)

    class Meta:
        managed = False
        db_table = 'experience'
