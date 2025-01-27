from django.urls import path
from . import views

urlpatterns=[
    path('get_songs',views.get_songs),
    path('add_song',views.add_song),
    path('update_song',views.update_song),
    path('delete_song',views.delete_song),
    path('validate_user',views.validate_user),
    path('validate_token',views.validate_token),
    path('get_image_casrol',views.get_image_casrol),
    path('set_image_casrol',views.set_image_casrol),
    path('create_user',views.create_user),
  
]