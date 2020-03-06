from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

class Events(models.Model):
    
    title = models.CharField(max_length=30)
    description = MarkdownxField()
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

    # TODO
    # AUTOGEN DATE TIME
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    # Create a property that returns the markdown instead
    @property
    def formatted_markdown(self):
        return markdownify(self.description)

    def __str__(self):
        return self.title
    class Meta:
        managed = True
        db_table = 'events'
        verbose_name_plural = 'Events' 
class Contests(models.Model):
    name = models.CharField(max_length=30)
    contest_url=models.URLField(blank=True,null=True)
    editorial_url=models.URLField(blank=True,null=True)
    ranklist_url=models.URLField(blank=True,null=True)
    rank1 = models.CharField(max_length=30,blank=True,null=True)
    rank2 = models.CharField(max_length=30,blank=True,null=True)
    rank3 = models.CharField(max_length=30,blank=True,null=True)
    event = models.ForeignKey(Events, on_delete=models.CASCADE,blank=True,null=True)
    def __str__(self):
        return self.name



    class Meta:
        managed = True
        db_table = 'contests'
        verbose_name_plural = 'Contests'

class Class(models.Model):
    year = models.CharField(max_length=30)
    topics = models.TextField()
    material_url = models.URLField(blank=True, null=True)
    event = models.ForeignKey(Events, on_delete=models.CASCADE,blank=True,null=True)
    def __str__(self):
        return self.topics


    class Meta:
        managed = True
        db_table = 'class'
        verbose_name_plural = 'Class'        

# DONE

   


class Contest_and_users(models.Model):
    role=(
        ('tester','tester'),
        ('setter','setter'),
        ('rank1','rank1'),
        ('rank2','rank2'),
        ('rank3','rank3')
    )       
    user_type= models.CharField(max_length=50, choices=role ,default='tester')
    user=models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    event=models.ForeignKey(Events, on_delete=models.CASCADE,blank=True,null=True)
    def __str__(self):
        if self.user == None or self.event == None:
            return "None"
        else :
            return str(self.user_type) +" "+ str(self.user.username)+" "+str(self.event.title)

    class Meta:
        managed = True
        db_table = 'contest_and_users'
        verbose_name_plural = 'Contest_and_users' 

class Class_and_users(models.Model):
    role=(
        ('teacher','teacher'),
        ('coordinator','coordinator')
    )       
    designation= models.CharField(max_length=50, choices=role ,default='teacher')
    name=models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    event=models.ForeignKey(Events, on_delete=models.CASCADE,blank=True,null=True)
    def __str__(self):
        if self.name == None or self.event == None:
            return "None"
        else :
            return str(self.designation) +" "+ str(self.name.username)+" "+str(self.event.title)

    class Meta:
        managed = True
        db_table = 'class_and_users'
        verbose_name_plural = 'Class_and_users'         

