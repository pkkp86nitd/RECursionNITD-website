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
@admin.register(Contest_and_users)    
class Contest_and_userAdmin(admin.ModelAdmin):
    pass

@admin.register(Class_and_users)    
class Class_and_userAdmin(admin.ModelAdmin):
    pass




