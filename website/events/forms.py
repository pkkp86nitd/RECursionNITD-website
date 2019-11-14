from django import forms
from .models import *
from django.contrib.auth.models import User
from .validators import valid_url_extension
from .validators import valid_url_mimetype
from django.utils.translation import ugettext as _
from markdownx.fields import MarkdownxFormField
import mimetypes

class Eventsform(forms.ModelForm):
    title = models.CharField(max_length=30)
    description = models.TextField()
    description = MarkdownxFormField()
    image_url = models.URLField()
    start_time = forms.DateTimeField( widget=forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder':'YYYY-MM-DD HH:MM:SS '}))
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder':'YYYY-MM-DD HH:MM:SS '}))
    location = models.CharField(max_length=30)
    event_choices = (
        ('1', 'contest'),
        ('2', 'class'),
        ('3', 'other')
    )
    event_type = forms.ChoiceField(choices=event_choices )
    
       
                           
    def clean_image_url(self):
        url=""
        if self.cleaned_data['image_url']!= None:
            url = self.cleaned_data['image_url'].lower()
            print("url", url)
            if not valid_url_extension(url) or not valid_url_mimetype(url):
                raise forms.ValidationError(_("Not a valid Image. The URL must have an image extensions (.jpg/.jpeg/.png)"))
        return url

    class Meta:
        model=Events
        fields=('title','description','image_url','start_time','end_time','location','event_type')
        widgets = {
            'description': forms.Textarea(
                attrs={'placeholder': 'Enter description here'},
                ),
                'title': forms.TextInput(
                attrs={'placeholder': 'contest name/class for/others'},
                ),
              
        }
class Contestsform(forms.ModelForm):
    name = models.CharField(max_length=30)
    contest_url = models.URLField()
    editorial_url = models.URLField()
    ranklist_url = models.URLField()

    class Meta:
         model=Contests
         fields=('name','contest_url','editorial_url','ranklist_url')

class Classform(forms.ModelForm):
    year = models.CharField(max_length=30)
    topics = models.TextField()
    teacher =  models.CharField(max_length=30)
    material_url = models.URLField()         
    class Meta:
        model=Class
        fields=('year','topics','material_url')

class Event_and_usersform(forms.ModelForm):
    roles=(
        ('tester','tester'),
        ('setter','setter'),
        ('teacher','teacher'),
        ('rank1','rank1'),
        ('rank2','rank2'),
        ('rank3','rank3')
    )  
    user_type=models.CharField(choices=roles) 
     
    class Meta:
        model=Event_and_users
        fields=('user_type','user')       