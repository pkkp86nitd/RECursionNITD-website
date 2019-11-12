from django.contrib import admin
from .models import *

@admin.register(Events)    
class EventAdmin(admin.ModelAdmin):
    pass

@admin.register(Class)    
class ClassAdmin(admin.ModelAdmin):
    pass
@admin.register(Contests)    
class ContestAdmin(admin.ModelAdmin):
    pass
@admin.register(Event_and_users)    
class Event_and_userAdmin(admin.ModelAdmin):
    pass


