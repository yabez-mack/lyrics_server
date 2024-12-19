from django.urls import path
from . import views

urlpatterns=[
    path('get_songs',views.get_songs),
    path('add_song',views.add_song),
    path('update_song',views.update_song),
    path('delete_song',views.delete_song),
  
]