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
    path('get_employees',views.get_employees),
    path('add_employee',views.add_employee),
    path('update_employee',views.update_employee),
    path('get_latest_employee_id',views.get_latest_employee_id),
    path('get_branch',views.get_branch),
    path('get_designation',views.get_designation),
    path('get_fields',views.get_fields),
    path('add_designation',views.add_designation),
    path('add_branch',views.add_branch),
    path('add_mission_field',views.add_mission_field),
    path('get_latest_song_no',views.get_latest_song_no),
    path('get_year',views.get_year),
    path('add_field_report',views.add_field_report),
    path('get_field_report',views.get_field_report),
    path('upload_file',views.upload_file),
  
]