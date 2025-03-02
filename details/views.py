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
            
            
            if len(value)>0:
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
         
            
def add_employee(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        reg_id = body.get('reg_id','')
        name = body.get('name','')
        adhar = body.get('adhar','')
        designation = body.get('designation','')
        email = body.get('email','')
        education_qualification = body.get('education_qualification','')
        field_name = body.get('field_name','')
        date_of_birth = body.get('date_of_birth','')
        address = body.get('address','')
        people_group = body.get('people_group','')
        language_known = body.get('language_known','')
        date_of_joining = body.get('date_of_joining','')
        contact_no = body.get('contact_no','')
        martial_status = body.get('martial_status','')
        spouse_name = body.get('spouse_name','')
        date_of_marriage = body.get('date_of_marriage','')
        spouse_occupation = body.get('spouse_occupation','')
        father_name = body.get('father_name','')
        mother_name = body.get('mother_name','')
        child_1 = body.get('child_1','')
        child_2 = body.get('child_2','')
        child_3 = body.get('child_3','')
        child_4 = body.get('child_4','')
        child_5 = body.get('child_5','')
        spouse_image = body.get('spouse_image','')
        signature = body.get('signature','')
        image = body.get('image','')
        family_image = body.get('family_image','')
        comment = body.get('comment','')
        branch = body.get('branch','')
        gender = body.get('gender','')
        status = body.get('status',0)
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            values =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]
            if(len(values)>0):
                if(reg_id and  name  and designation):                  
                    
                    cursor.execute(f"""INSERT INTO `song_book`.`employee` (`reg_id`,`name`,`adhar`,`designation`,`email`,`education_qualification`,`field_name`, `date_of_birth`, `address`, `people_group`,`language_known`,`date_of_joining`, `contact_no`,`martial_status`,`spouse_name`,`date_of_marriage`,`spouse_occupation`,`father_name`,`mother_name`,`child_1`,`child_2`,`child_3`,`child_4`,`child_5`,`spouse_image`,`signature`,`image`,`status`,`family_image`,`comment`,`branch`,`gender`) 
                                    VALUES ('{reg_id}','{name}','{adhar}','{designation}','{email}','{education_qualification}','{field_name}','{date_of_birth}','{address}','{people_group}','{language_known}','{date_of_joining}','{contact_no}','{martial_status}','{spouse_name}','{date_of_marriage}','{spouse_occupation}','{father_name}','{mother_name}','{child_1}','{child_2}','{child_3}','{child_4}','{child_5}','{spouse_image}','{signature}','{image}',{status},'{family_image}','{comment}','{branch}','{gender}');""")
                    return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
            
def update_employee(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        id = body.get('id','')
        reg_id = body.get('reg_id','')
        name = body.get('name','')
        adhar = body.get('adhar','')
        designation = body.get('designation','')
        email = body.get('email','')
        education_qualification = body.get('education_qualification','')
        field_name = body.get('field_name','')
        date_of_birth = body.get('date_of_birth','')
        address = body.get('address','')
        people_group = body.get('people_group','')
        language_known = body.get('language_known','')
        date_of_joining = body.get('date_of_joining','')
        contact_no = body.get('contact_no','')
        martial_status = body.get('martial_status','')
        spouse_name = body.get('spouse_name','')
        date_of_marriage = body.get('date_of_marriage','')
        spouse_occupation = body.get('spouse_occupation','')
        father_name = body.get('father_name','')
        mother_name = body.get('mother_name','')
        child_1 = body.get('child_1','')
        child_2 = body.get('child_2','')
        child_3 = body.get('child_3','')
        child_4 = body.get('child_4','')
        child_5 = body.get('child_5','')
        spouse_image = body.get('spouse_image','')
        signature = body.get('signature','')
        image = body.get('image','')
        family_image = body.get('family_image','')
        comment = body.get('comment','')
        branch = body.get('branch','')
        gender = body.get('gender','')
        status = body.get('status',0)
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            values =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]
            if(len(values)>0):
                if(reg_id and id and  name  and designation):                  
                    
                    cursor.execute(f"""UPDATE `song_book`.`employee`
                    SET 
                        `name` = '{name}',
                        `adhar` = '{adhar}',
                        `designation` = '{designation}',
                        `email` = '{email}',
                        `education_qualification` = '{education_qualification}',
                        `field_name` = '{field_name}',
                        `date_of_birth` = '{date_of_birth}',
                        `address` = '{address}',
                        `people_group` = '{people_group}',
                        `language_known` = '{language_known}',
                        `date_of_joining` = '{date_of_joining}',
                        `contact_no` = '{contact_no}',
                        `martial_status` = '{martial_status}',
                        `spouse_name` = '{spouse_name}',
                        `date_of_marriage` = '{date_of_marriage}',
                        `spouse_occupation` = '{spouse_occupation}',
                        `father_name` = '{father_name}',
                        `mother_name` = '{mother_name}',
                        `child_1` = '{child_1}',
                        `child_2` = '{child_2}',
                        `child_3` = '{child_3}',
                        `child_4` = '{child_4}',
                        `child_5` = '{child_5}',
                        `spouse_image` = '{spouse_image}',
                        `signature` = '{signature}',
                        `image` = '{image}',
                        `status` = {status},
                        `family_image` = '{family_image}',
                        `comment` = '{comment}',
                        `branch` = '{branch}',
                        `gender` = '{gender}',
                        `reg_id` = '{reg_id}'
                        
                    WHERE 
                        `id`={id}
                        ;""")
                    return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
            
def add_branch(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')        
        branch_name = body.get('branch_name','')
        status = body.get('status',0)
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0):
                if(branch_name and  status ):                  
                    cursor.execute(f"""SELECT * FROM song_book.branch where branch_name='{branch_name}' ;""")
                    desc = cursor.description 
                    values =  [dict(zip([col[0] for col in desc], row)) 
                        for row in cursor.fetchall()]
                    if(len(values)==0):
                        
                        cursor.execute(f"""INSERT INTO `song_book`.`branch` (`branch_name`,`status`) 
                                        VALUES ('{branch_name}',{status});""")
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    else:
                        return JsonResponse({"message":"Branch Name Already Exists","status":"failed"})
                        
                    
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
    
def add_mission_field(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')        
        field_name = body.get('field_name','')
        branch_id = body.get('branch_id','')
        status = body.get('status',0)
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0):
                if(branch_id and  status and field_name ):                  
                    cursor.execute(f"""SELECT * FROM song_book.mission_field where field_name='{field_name}' AND branch_id='{branch_id}' ;""")
                    desc = cursor.description 
                    values =  [dict(zip([col[0] for col in desc], row)) 
                        for row in cursor.fetchall()]
                    if(len(values)==0):
                        
                        cursor.execute(f"""INSERT INTO `song_book`.`mission_field` (`field_name`,`status`,`branch_id`) 
                                    VALUES ('{field_name}',{status},'{branch_id}');""")
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    else:
                        return JsonResponse({"message":"Field Already Exists","status":"failed"})                    
                    
                    
                   
                    
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
    
def add_field_report(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')        
        testimony = body.get('testimony','')
        employee_id = body.get('employee_id','')
        prayer_request = body.get('prayer_request','')
        year = body.get('year','')
        month = body.get('month','')
        obstacles = body.get('obstacles','')
        new_followers = body.get('new_followers','')
        status = body.get('status',0)
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0):
                if(month and  status and year ):                  
                    cursor.execute(f"""SELECT * FROM song_book.field_report where employee_id='{employee_id}' AND year='{year}'  AND month='{month}' ;""")
                    desc = cursor.description 
                    values =  [dict(zip([col[0] for col in desc], row)) 
                        for row in cursor.fetchall()]
                    if(len(values)==0):
                        
                        cursor.execute(f"""INSERT INTO `song_book`.`field_report` (`employee_id`,`status`,`year`,`month`,`testimony`,`prayer_request`,`obstacles`,`new_followers`) 
                                                                            VALUES ('{employee_id}',{status},'{year}','{month}','{testimony}','{prayer_request}','{obstacles}','{new_followers}');""")
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    else:
                        return JsonResponse({"message":"Field Report Already Exists","status":"failed"})                
                    
                    
                   
                    
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
    
def add_designation(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')        
        designation = body.get('designation','')
        status = body.get('status',0)
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            valuee =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(valuee)>0):
                if(designation and  status ):   
                    cursor.execute(f"""SELECT * FROM song_book.designation where designation_name='{designation}' ;""")
                    desc = cursor.description 
                    values =  [dict(zip([col[0] for col in desc], row)) 
                        for row in cursor.fetchall()]
                    if(len(values)==0):
                        
                        cursor.execute(f"""INSERT INTO `song_book`.`designation` (`designation_name`,`status`) 
                                    VALUES ('{designation}',{status});""")
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    else:
                        return JsonResponse({"message":"Field Already Exists","status":"failed"})
                        
                        
                   
                    
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})

def get_latest_employee_id(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0):
                cursor.execute(f"SELECT MAX(reg_id) as reg_id  FROM song_book.employee ")
                desc = cursor.description 
                values =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]    
                         
                if(values[0]['reg_id']!=None):
                    s=values[0]['reg_id']
                    match = re.search(r'(\d+)$', s)
                    if match:
                        numeric_part = match.group(1)
                        prefix = s[:-len(numeric_part)] 
                        new_numeric_part = int(numeric_part) + 1
                        new_s = prefix + str(new_numeric_part).zfill(len(numeric_part))
                        return JsonResponse({"data":new_s,"status":"success"})
                    else:
                        return JsonResponse({"data":'001',"status":"success"})
                else:
                    return JsonResponse({"data":'001',"status":"success"})
            else:    
                return JsonResponse({"message":"Invalid User","status":"failed"})
        else:
            return JsonResponse({"status":"failed","message":"Please Login"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
    
def get_latest_song_no(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0):
                cursor.execute(f"SELECT MAX(serial_no) as serial_no  FROM song_book.song ")
                desc = cursor.description 
                values =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]    
                # print(values)
                if(values[0]['serial_no']!=None):
                    s=values[0]['serial_no']
                    s=int(s)+1                    
                    return JsonResponse({"data":s,"status":"success"})
                else:
                    return JsonResponse({"data":'001',"status":"success"})
            else:    
                return JsonResponse({"message":"Invalid User","status":"failed"})
        else:
            return JsonResponse({"status":"failed","message":"Please Login"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
    
def get_field_report(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        employee_id = body.get('employee_id','')
        year = body.get('year','')
        month = body.get('month','')
        condition=''
        if(employee_id):
            condition+=f"AND fr.employee_id='{employee_id}'"
        if(month):
            condition+=f"AND fr.month='{month}'"
        if(year):
            condition+=f"AND fr.year='{year}'"
        
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0):
                cursor.execute(f"""SELECT fr.*,des.designation_name,br.branch_name,mis.field_name,emp.name,emp.gender,emp.email,emp.date_of_birth,emp.address,emp.contact_no,emp.date_of_joining,emp.martial_status,emp.spouse_name,emp.father_name,emp.reg_id,yr.year as year_name FROM song_book.field_report fr 
                                    join song_book.employee emp on emp.id=fr.employee_id 
                                    join designation des on emp.designation=des.id
                                    join year yr on fr.year=yr.id
                                    left join branch br on emp.branch=br.branch_name
                                    left join mission_field mis on emp.field_name=mis.id
                                    where fr.status=1 {condition} """)
                desc = cursor.description 
                value =  [dict(zip([col[0] for col in desc], row)) 
                        for row in cursor.fetchall()]
                return JsonResponse({"data":value,"status":"success"})
            else:    
                return JsonResponse({"message":"Invalid User","status":"failed"})
        else:
            return JsonResponse({"status":"failed","message":"Please Login"})
    except:
        return JsonResponse({"status":"failed","message":"BAD REQUEST"})
    
def get_employees(request):
    private_connections = ConnectionHandler(settings.DATABASES)
    db = router.db_for_write(model)
    new_conn = private_connections[db]
    cursor = new_conn.cursor()
    req=json.loads(request.body)
    cursor.execute(f"""SELECT emp.*,branch.branch_name,desig.designation_name FROM song_book.employee emp
left join song_book.branch branch on emp.branch=branch.id
left join song_book.designation desig on emp.designation=desig.id""")
    desc = cursor.description 
    value =  [dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall()]
    return JsonResponse({"data":value,"status":"success"})

def get_branch(request):
    private_connections = ConnectionHandler(settings.DATABASES)
    db = router.db_for_write(model)
    new_conn = private_connections[db]
    cursor = new_conn.cursor()
    req=json.loads(request.body)
    
    cursor.execute(f"SELECT * FROM song_book.branch ")
    desc = cursor.description 
    value =  [dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall()]
    return JsonResponse({"data":value,"status":"success"})

def get_designation(request):
    private_connections = ConnectionHandler(settings.DATABASES)
    db = router.db_for_write(model)
    new_conn = private_connections[db]
    cursor = new_conn.cursor()
    req=json.loads(request.body)
    cursor.execute(f"SELECT * FROM song_book.designation ")
    desc = cursor.description 
    value =  [dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall()]
    return JsonResponse({"data":value,"status":"success"})

def get_year(request):
    private_connections = ConnectionHandler(settings.DATABASES)
    db = router.db_for_write(model)
    new_conn = private_connections[db]
    cursor = new_conn.cursor()
    req=json.loads(request.body)
    cursor.execute(f"SELECT * FROM song_book.year; ")
    desc = cursor.description 
    value =  [dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall()]
    return JsonResponse({"data":value,"status":"success"})

def get_fields(request):
    private_connections = ConnectionHandler(settings.DATABASES)
    db = router.db_for_write(model)
    new_conn = private_connections[db]
    cursor = new_conn.cursor()
    
    body=json.loads(request.body)
    branch_id=body.get('branch_id','')
    if(branch_id):
        cursor.execute(f"SELECT * FROM song_book.mission_field where branch_id={branch_id}")
        desc = cursor.description 
        value =  [dict(zip([col[0] for col in desc], row)) 
                for row in cursor.fetchall()]
        return JsonResponse({"data":value,"status":"success"})
    else:
        cursor.execute(f"SELECT * FROM song_book.mission_field")
        desc = cursor.description 
        value =  [dict(zip([col[0] for col in desc], row)) 
                for row in cursor.fetchall()]
        return JsonResponse({"data":value,"status":"success"})


        
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
    


   



 
  