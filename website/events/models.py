from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class Contests(models.Model):
    name = models.CharField(max_length=30)
    contest_url=models.URLField(blank=True,null=True)
    editorial_url=models.URLField(blank=True,null=True)
    ranklist_url=models.URLField(blank=True,null=True)
    def __str__(self):
        return self.name



    class Meta:
        managed = True
        db_table = 'contests'
        verbose_name_plural = 'Contests'

class Class(models.Model):
    year = models.CharField(max_length=30)
    topics = models.TextField()
    teacher =  models.CharField(max_length=30,blank=True,null=True)
    material_url = models.URLField(blank=True, null=True)
    def __str__(self):
        return self.topics


    class Meta:
        managed = True
        db_table = 'class'
        verbose_name_plural = 'Class'        

# DONE
class Events(models.Model):
    
    title = models.CharField(max_length=30)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='images/')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location=models.CharField(max_length=30,blank=True, null=True)
    event_choices = (
        ('1', 'contest'),
        ('2', 'class'),
        ('3', 'other')
    )
    event_type = models.CharField(max_length=50, choices=event_choices ,default='3')
    contest_name = models.OneToOneField(Contests, on_delete=models.CASCADE,blank=True,null=True)
    class_topics = models.OneToOneField(Class, on_delete=models.CASCADE,blank=True,null=True)
    # TODO
    # AUTOGEN DATE TIME
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    def __str__(self):
        return self.title
    class Meta:
        managed = True
        db_table = 'events'
        verbose_name_plural = 'Events' 


class Event_and_users(models.Model):
    role=(
        ('tester','tester'),
        ('setter','setter'),
        ('teacher','teacher'),
        ('rank1','rank1'),
        ('rank2','rank2'),
        ('rank3','rank3')
    )       
    user_type= models.CharField(max_length=50, choices=role ,default='tester')
    user=models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    event=models.ForeignKey(Events, on_delete=models.CASCADE,blank=True,null=True)

    def __str__(self):
        return str(self.user_type) +" "+ str(self.user.username)+" "+str(self.event.id)
    class Meta:
        managed = True
        db_table = 'event_and_users'
        verbose_name_plural = 'Event_and_users' 

