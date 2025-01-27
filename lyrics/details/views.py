import json
from pyexpat import model
import random
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


# def create_conn():
    # cursor = new_conn.cursor()
private_connections = ConnectionHandler(settings.DATABASES)
db = router.db_for_write(model)
new_conn = private_connections[db]
cursor = new_conn.cursor()   
    
def validate_user(request):
    try:
        body=json.loads(request.body)
        user_name = body.get('user_name')
        password = body.get('password')
        if(user_name and password):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
            cursor.execute(f"""SELECT * from song_book.user_details where username='{user_name}' and password='{password}' """)
            
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]
          
            if len(value)>0:
                user_id=value[0]
                token = ''.join([str(random.randint(0, 9)) for _ in range(20)])
                cursor.execute(f'''INSERT INTO song_book.auth_tokens (token,user_id,created_at,expires_at)
                                    VALUES ({token},'{user_id['user_id']}',NOW(), NOW()+ INTERVAL 24 HOUR)''')
                return JsonResponse({"token":token,"user":user_id,"status":"success"})
                
            else:    
                return JsonResponse({"message":"No Data Found","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
            
def validate_token(request):
    try:
        body=json.loads(request.body)
        token = body.get('token')
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT b.username,b.full_name,a.* FROM song_book.auth_tokens a
                                join song_book.user_details b on a.user_id=b.user_id and a.token='{token}' ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]
            print(value)
            print((token))
            if len(value)==0:
                user=value[0]
                return JsonResponse({"data":user,"status":"success"})
            elif len(value)>0:
                user=value[0]
                return JsonResponse({"data":user,"status":"success"})
            else:    
                return JsonResponse({"message":"No Data Found","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
            
def set_image_casrol(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        title = body.get('title','')
        image_url = body.get('image_url','')
        status = body.get('status','')
        detail = body.get('detail','')
        type = body.get('type','')
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT b.username,b.full_name,a.* FROM song_book.auth_tokens a
                                join song_book.user_details b on a.user_id=b.id ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(any(d['token'] == token for d in value)):
                if(title and  image_url and status and type):
                    
                    cursor.execute(f"""SELECT COUNT(*) AS count FROM `song_book`.`dashboard_casrol` WHERE title = '{title}' AND type={type};""")
                    desc = cursor.description 
                    value =  [dict(zip([col[0] for col in desc], row)) 
                                for row in cursor.fetchall()]
                    if value[0]['count']==0:
                        
                        cursor.execute(f"""INSERT INTO `song_book`.`dashboard_casrol` (`title`, `image`, `status`, `detail`, `type`) 
                                    VALUES ('{title}','{image_url}', {status}, '{detail}', {type});""")
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    else:
                        return JsonResponse({"message":"Title Already Exists","status":"failed"})
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
            
def get_image_casrol(request):
   
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.dashboard_casrol""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0):
            
                return JsonResponse({"data":value,"status":"success"})
                
            else:    
                return JsonResponse({"message":"No Data Found","status":"failed"})
def create_user(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        username = body.get('username','')
        password = body.get('password','')
        full_name = body.get('full_name','')
        created_by = body.get('user_id','')
        status = body.get('status','')
        user_type = body.get('user_type','')
        image = body.get('image','')
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT b.username,b.full_name,a.* FROM song_book.auth_tokens a
                                join song_book.user_details b on a.user_id=b.id ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(any(d['token'] == token for d in value)):
                if(username and  password and status and user_type and full_name):
                    cursor.execute(f"""SELECT * FROM `song_book`.`user_details`
                                        ORDER BY id DESC
                                        LIMIT 1;""")
                    desc = cursor.description 
                    value =  [dict(zip([col[0] for col in desc], row)) 
                                for row in cursor.fetchall()]
                    
                    if increment_alphanumeric(value[0]['user_id']):
                        user_id=increment_alphanumeric(value[0]['user_id'])
                        print(f"""INSERT INTO `song_book`.`user_details` (`user_id`, `username`,`password`,`full_name`,`created_date`,`created_by`  ,`status`, `user_type`, `image`) 
                                    VALUES ('{user_id}','{username}','{password}', '{full_name}',CURRENT_DATE,'{created_by}',{status}, {user_type}, '{image}');""")
                        cursor.execute(f"""INSERT INTO `song_book`.`user_details` (`user_id`, `username`,`password`,`full_name`,`created_date`,`created_by`  ,`status`, `user_type`, `image`) 
                                    VALUES ('{user_id}','{username}','{password}', '{full_name}',CURRENT_DATE,'{created_by}',{status}, {user_type}, '{image}');""")
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    else:
                        return JsonResponse({"message":"Title Already Exists","status":"failed"})
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
         
def increment_alphanumeric(string):
    match = re.match(r"([a-zA-Z]+)(\d+)$", string)
    
    if match:
        letters = match.group(1)
        number = int(match.group(2))
        
        # Increment the number by 1
        incremented_number = number + 1
        
        return f"{letters}{incremented_number}"
    else:
        return False

def get_songs(request):
    private_connections = ConnectionHandler(settings.DATABASES)
    db = router.db_for_write(model)
    new_conn = private_connections[db]
    cursor = new_conn.cursor()
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
    


   



 
  