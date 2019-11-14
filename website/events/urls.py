from django.urls import path
from .views import *
from django.conf.urls import include,url
from django.conf import settings
from django.conf.urls.static import static

app_name="events"
urlpatterns=[
    path('create/', event_create, name='event_create'),
    path('list/',events, name='events'),
    path('detail/<int:id>/', event_detail, name='event_detail'),
    path('calender/', calender, name='calender'),
    path('update/<int:id>/', event_update, name='event_update'),
    path('upcoming_list/',upcoming_events, name='upcoming_events'),
    path('create_contest/<int:id>/',create_contest, name='create_contest'),
    path('create_class/<int:id>/',create_class, name='create_class'),
    path('update_contest/<int:id>/',update_contest, name='update_contest'),
    path('upadte_class/<int:id>/',update_class, name='update_class'),
    path('',events, name='events'),
    url(r'^markdownx/', include('markdownx.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
