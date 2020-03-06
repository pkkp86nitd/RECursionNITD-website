from django.shortcuts import render, redirect,get_object_or_404, get_list_or_404
from .models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader, RequestContext
from .forms import Eventsform,Contestsform,Classform,Contest_and_usersform,Class_and_usersform
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.forms import modelformset_factory
from django.contrib.auth.forms import UserCreationForm
from itertools import chain
from django.utils import timezone
from datetime import timedelta
from django.core.files.base import ContentFile
from io import BytesIO
import urllib.request
from PIL import Image
import json
import datetime
from .validators import valid_url_extension
from .validators import valid_url_mimetype
from django.core.exceptions import PermissionDenied
from .cal_api import create_event
from django.forms import modelformset_factory
from django.contrib.auth.forms import UserCreationForm


json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)

def superuser_only(function):
   def _inner(request, *args, **kwargs):
       if not request.user.is_superuser:
           raise PermissionDenied
       return function(request, *args, **kwargs)
   return _inner

def events(request):
    events=Events.objects.all()
    perms=0
    if request.user.is_superuser:
        perms=1
    return render(request, 'events.html',{'events': events,"perms":perms})


@superuser_only
def create_contest(request,id):
     perms=0
     if request.user.is_superuser:
         perms=1
     print(request.method)
     form=Contestsform(None)
     eform = modelformset_factory(Contest_and_users, fields=('user_type','user'), extra=6)
     if request.method == "POST":
         form = Contestsform(request.POST)
         form2= eform(request.POST )
         if form.is_valid() and form2.is_valid(): 
             if form.name != "": 
                 f=form.save(commit=False)
                 form.save()
                 event=Events.objects.get(id=id)
                 print(event,f.name,f.id)
                 event.contest_name=Contests.objects.get(name=f.name)
                 event.save()
                 f2 =form2.save(commit=False)   
                 for item in f2:
                     item.event=Events.objects.get(id=id)
                     item.save()

             return redirect('events:events')    
   
     form2 =eform(queryset=Contest_and_users.objects.none())
     args={'form':form,'perms':perms,'id':id,'eform':form2}
     return render(request,'create_contest.html',args)    


@superuser_only
def create_class(request,id):
    perms=0
    if request.user.is_superuser:
        perms=1
    form=Classform(None)
    form2=Contest_and_usersform(None)
    if request.method =="POST":
        form=Classform(request.POST or None)
        form2=Contest_and_usersform(request.POST or None)
        if form.is_valid and form2.is_valid:
            if form.topics != "":
                f=form.save(commit=False)
                f2=form2.save(commit=False)
                form.save()
                event=Events.objects.get(id=id)
                event.class_topics=Class.objects.get(topics=f.topics)
                event.save()
                f2.event=event
                f2.save()
            return redirect('events:events')
    return render(request,'create_class.html',{'form':form,'form2':form2,'perms':perms,'id':id})        




@superuser_only
def event_create(request):
    perms=0
    if request.user.is_superuser:
        perms=1
    form = Eventsform( None)
    print(request.method)
    Conform=Contestsform( None)
    Clsform=Classform( None)
    eform2 = modelformset_factory(Contest_and_users, fields=('user_type','user'), extra=6)
    eform3 = modelformset_factory(Class_and_users, fields=('designation','name'), extra=3)
    form2=eform2(queryset=Contest_and_users.objects.none()) 
    form3=eform3(queryset=Class_and_users.objects.none()) 
    if request.method=="POST":
        form = Eventsform( request.POST or None)
        Conform=Contestsform(request.POST or None )
        form2=eform2(request.POST or None) 
        Clsform=Classform(request.POST or None )
        
        form3=eform3(request.POST or None) 
        print(form3)
        print("oberve ",form.is_valid(),Conform.is_valid(),form2.is_valid(),Clsform.is_valid(),form3.is_valid())
    if form.is_valid() :
        event=form.save(commit=False)
        form.save()
        id=event.id
        image_url=form.cleaned_data['image_url']
        if image_url != "":
                type=valid_url_extension(image_url)
                print("event ",id)
                full_path='media/images/'+'event_'+str(id)+ '.png'
                try:
                    urllib.request.urlretrieve(image_url,full_path)
                except:
                    get_object_or_404(Events,pk=id).delete()
                    return HttpResponse("Downloadable Image Not Found!")
                event.image='../'+full_path           
        print("Conform ",Conform.name)  
        if Conform.is_valid() and form2.is_valid() :
            print("Conform")      
            if Conform.name != "": 
                 f=Conform.save(commit=False)
                 Conform.save()
                 event.save()
                 print(event,f.name,event.title)
                 
                 Con=Contests.objects.get(pk=f.id)
                 Con.event=Events.objects.get(pk=event.id)
                 Con.save()
            
              
                 print("commit") 
                 
                 for item in form2:
                     it=item.save(commit=False)
                     it.event=Events.objects.get(pk=event.id)
                     if it.user != None:
                        it.save()           

                 #Event_contest.objects.create(event_title=get_object_or_404(Events,pk=event.id),contest_name=get_object_or_404(Contests,pk=f.id))

        if Clsform.is_valid() and form3.is_valid() :
            print("CLSform")
            if Clsform.topics != "":
                f=Clsform.save(commit=False)
                Clsform.save()
                event.save() 
                Con=Class.objects.get(pk=f.id)
                Con.event=Events.objects.get(pk=event.id)
                Con.save()
                for item in form3:
                    it=item.save(commit=False)
                    it.event=Events.objects.get(pk=event.id)
                    if it.name != None:
                       it.save()  

                #Event_class.objects.create(event_title=get_object_or_404(Events,pk=event.id),class_topics=get_object_or_404(Class,pk=f.id))  
        return redirect("events:events")

    
    
    args={'Conform':Conform,'perms':perms,'eform2':form2,'eform3':form3,'form':form,'Clsform':Clsform}           
    return render(request, 'create_event.html',args)

def event_detail(request,id):
    try:
        event =get_object_or_404( Events,pk=id)
    except:
        return HttpResponse("id does not exist")
    else:
        if event.event_type == "1":
            event_add=Contests.objects.get(event=event)
            to_add=event_add
        elif event.event_type == "2":
            event_add=Class.objects.get(event=event)
            to_add=event_add
        else:
            to_add=""
        Con_users=Contest_and_users.objects.filter(event=event)
        Cls_users=Class_and_users.objects.filter(event=event)      
        return render(request,'event_detail.html',{'event':event,"event_add":to_add,"con_users":Con_users,"cls_users":Cls_users})
@superuser_only
def update_contest(request,id):
    try:
        event=get_object_or_404(Events,pk=id)
        
    except:
        return HttpResponse("id does not exist")
    else :
        perms=0
        if request.user.is_superuser:
            perms=1
        else :
            return HttpResponse("Go get perms,admins only")
        contest=get_object_or_404(Contests,pk=event.contest_name.id)
        form=Contestsform( None,instance=contest) 
        eform = modelformset_factory(Contest_and_users, fields=('user_type',"user"), extra=5)
        if request.method == "POST":
             form = Contestsform(request.POST)
             form2= eform(request.POST)
             if form.is_valid and form2.is_valid: 
                if form.name != "": 
                    f=form.save(commit=False)
                    form.save()

                f2=form2.save(commit=False)    
                for item in f2:
                    if item.user != None:
                        try:
                            user_name = item.user
                            user = get_object_or_404(Contest_and_users, name=user_name)  
                        except:
                            if  Contest_and_users.objects.filter(user=user_name,event=event,user_type=item.user_type).exists() == False:
                                user = Contest_and_users.objects.create(user=user_name,event=event,user_type=user_type) 
                    else :
                        item.delete()       
                     
                return redirect('events:events')    
        
        form2 =eform(queryset=Contest_and_users.objects.filter(event=event))    
        args={'form':form,'perms':perms,'id':id,'eform':form2}
    return render(request,'update_contest.html',args) 

@superuser_only
def update_class(request,id):
    try:
        event=get_object_or_404(Events,pk=id)
        
    except:
        return HttpResponse("id does not exist")
    else :
        perms=0
        if request.user.is_superuser:
            perms=1
        else :
            return HttpResponse("Go get perms,admins only")
        classs=get_object_or_404(Class,pk=event.class_topics.id)
        print("classss",classs.id)
        form=Classform( None,instance=classs) 
        eform = modelformset_factory(Contest_and_users, fields=('user_type',"user"), extra=2)
        if request.method == "POST":
             form = Classform(request.POST)
             form2= eform(request.POST)
             if form.is_valid and form2.is_valid: 
                if form.topics != "": 
                    f=form.save(commit=False)
                    form.save()

                f2=form2.save(commit=False)    
                for item in f2:
                    if item.user != None:
                        try:
                            user_name = item.user
                            user = get_object_or_404(Contest_and_users, name=user_name)  
                        except:
                            if  Contest_and_users.objects.filter(user=user_name,event=event,user_type=item.user_type).exists() == False:
                                user = Contest_and_users.objects.create(user=user_name,event=event,user_type=item.user_type) 
                    else :
                        item.delete()       
                return redirect('events:events')    
        
        form2 =eform(queryset=Contest_and_users.objects.filter(event=event))    
        args={'form':form,'perms':perms,'id':id,'eform':form2}
    return render(request,'update_class.html',args)          


@superuser_only
def event_update(request,id):
    print("call")
    try:
        event =get_object_or_404(Events, pk=id)

    except:
        return HttpResponse("id does not exist")
    else:
        perms=0
        if request.user.is_superuser:
            perms=1
        else:
            return HttpResponse("Go get perms,only admins")
        upform = Eventsform(request.POST or None, instance=event)

        if request.method == "POST":
            if upform.is_valid():
                image_url=upform.cleaned_data['image_url']
                print(image_url)
                if image_url != "":
                    event=upform.save(commit=False)
                    image_url=upform.cleaned_data['image_url']
                    type=valid_url_extension(image_url)
                    full_path='media/images/'+'event_'+str(id)+ '.png'
                    try:
                        urllib.request.urlretrieve(image_url,full_path)
                    except:
                        return HttpResponse("Downloadable Image Not Found!")
                    event.image='../'+full_path
                event.save()    
                request.method="GET"
                if event.event_type == "1" :
                    print("Contest",id)
                    return update_contest(request,id)
                    
                elif event.event_type == "2":
                    print("Class",id)
                    return  update_class(request,id)
                    
                else:
                    return redirect("events:events")    
                
        return render(request, 'update_event.html',{'upform':upform,"perms":perms,"id":id})

def upcoming_events(request):
    today=timezone.now()
    upto=today + timedelta(days=365)
    events=Events.objects.filter(start_time__range=[today, upto])
    
    return render(request, 'events.html',{'events': events})

def calender(request):
    events=Events.objects.all().order_by('-start_time')
    args={'events':events,}
    return render(request, 'calender.html', args)