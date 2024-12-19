import json
from pyexpat import model
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
from django.db.utils import ConnectionHandler
import re
# import mysql.connector 
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="1234",
#     database='schoolknot'
# )
from django.db import connection, router

private_connections = ConnectionHandler(settings.DATABASES)
db = router.db_for_write(model)
new_conn = private_connections[db]
cursor = new_conn.cursor()
    
def get_songs(request):
    req=json.loads(request.body)
    cursor.execute(f"SELECT * FROM song_book.song ")
    desc = cursor.description 
    value =  [dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall()]
    return JsonResponse({"data":value,"status":"success"})

def add_song(request):
    payload = request.body
    event = None
    try:
        json.loads(request.body)
        req=json.loads(request.body)
        album=req.get('album','')
        artist=req.get('artist','')
        image=req.get('image','')
        index=req.get('index','')
        language=req.get('language','')
        name=req.get('name','')
        serial_no=req.get('serial_no','')
        song=req.get('song','')
        video_url=req.get('video_url','')
        if(name==''):
            return JsonResponse({"status":"failed","message":"Please Enter Song Name"})
        if(serial_no==''):
            return JsonResponse({"status":"failed","message":"Please Enter Song No."})
        if(song==''):
            return JsonResponse({"status":"failed","message":"Please Enter Song Lyrics"})
        else:
            cursor.execute(f"""INSERT INTO song_book.song (album,artist,image,language,name,serial_no,song,video_url) VALUES ('{album}','{artist}','{image}','{language}','{name}','{serial_no}','{song}','{video_url}')""")
        
            return JsonResponse({"status":"success"})

    except ValueError as e:
    # Invalid payload
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
    
def update_song(request):
    payload = request.body
    event = None
    try:
        json.loads(request.body)
        req=json.loads(request.body)
        id=req.get('id','')
        album=req.get('album','')
        artist=req.get('artist','')
        image=req.get('image','')
        index=req.get('index','')
        language=req.get('language','')
        name=req.get('name','')
        serial_no=req.get('serial_no','')
        song=req.get('song','')
        video_url=req.get('video_url','')
        if(id==''):
            return JsonResponse({"status":"failed","message":"ID NOT FOUND"})
        if(name==''):
            return JsonResponse({"status":"failed","message":"Please Enter Song Name"})
        if(serial_no==''):
            return JsonResponse({"status":"failed","message":"Please Enter Song No."})
        if(song==''):
            return JsonResponse({"status":"failed","message":"Please Enter Song Lyrics"})
        else:
            cursor.execute(f"""UPDATE song_book.song SET album ='{album}',artist ='{artist}', image ='{image}', language ='{language}', name='{name}', serial_no ='{serial_no}', song ='{song}', video_url ='{video_url}' where id={id}""")
        
            return JsonResponse({"status":"success"})

    except ValueError as e:
    # Invalid payload
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
    
def delete_song(request):
    payload = request.body
    event = None
    try:
        json.loads(request.body)
        req=json.loads(request.body)
        id=req.get('id','')
      
        if(id==''):
            return JsonResponse({"status":"failed","message":"ID NOT FOUND"})      
        else:
            cursor.execute(f"""DELETE FROM song_book.song  where id={id}""")
        
            return JsonResponse({"status":"success"})

    except ValueError as e:
    # Invalid payload
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
    


   



 
  