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
import boto3
from botocore.exceptions import NoCredentialsError
from django.http import JsonResponse
from django.core.files.storage import default_storage
import tempfile
from django.conf import settings
import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

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
            password=encrypt_aes(password)
            cursor.execute(f"""SELECT user_id,username,full_name,user_type from song_book.user_details where username='{user_name}' and password='{password}' """)
            
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
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
            
def validate_token(request):
    try:
        body=json.loads(request.body)
        token = body.get('token')
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT 
                                    b.username, 
                                    b.full_name, 
                                    a.*, 
                                    GROUP_CONCAT(
                                        CASE 
                                            WHEN b.user_type = 2 THEN ma.module_id 
                                            ELSE m.id 
                                        END 
                                        
                                        ORDER BY ma.module_id
                                        ) AS module_access
                                FROM song_book.auth_tokens a
                                JOIN song_book.user_details b 
                                    ON a.user_id = b.user_id 
                                    AND a.token = '{token}'
                                LEFT JOIN song_book.module_access ma 
                                    ON a.user_id = ma.user_id 
                                    AND b.user_type = 2
                                LEFT JOIN song_book.modules m 
                                    ON b.user_type != 2
                                
                                
                                GROUP BY b.username, b.full_name, a.user_id;""")
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
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
            
def set_image_casrol(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        title = body.get('title','')
        image_url = body.get('image_url','')
        status = body.get('status','')
        detail = body.get('detail','')
        file = body.get('file','')
        file_name = body.get('file_name','')
        type = body.get('type','')
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
                if(title  and status and type):
                    
                    cursor.execute(f"""SELECT COUNT(*) AS count FROM `song_book`.`dashboard_casrol` WHERE title = '{title}' AND type={type};""")
                    desc = cursor.description 
                    value =  [dict(zip([col[0] for col in desc], row)) 
                                for row in cursor.fetchall()]
                    if value[0]['count']==0:
                        image_url=upload_file(file,file_name,'dashboard/casrol')
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
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
            
def set_events(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        title = body.get('title','')
        image_url = body.get('image_url','')
        status = body.get('status','')
        detail = body.get('detail','')
        file = body.get('file','')
        event_start_date = body.get('event_start_date','')
        event_end_date = body.get('event_end_date','')
        file_name = body.get('file_name','')
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
                if(title  and status and event_start_date and event_end_date):
                    
                    cursor.execute(f"""SELECT COUNT(*) AS count FROM `song_book`.`events` WHERE event_name = '{title}';""")
                    desc = cursor.description 
                    value =  [dict(zip([col[0] for col in desc], row)) 
                                for row in cursor.fetchall()]
                    if value[0]['count']==0:
                        image_url=upload_file(file,file_name,'dashboard/events')
                        
                        cursor.execute(f"""INSERT INTO `song_book`.`events` (`event_name`, `image`, `status`, `detail`, `event_start_date`, `event_end_date`) 
                                                                    VALUES ('{title}','{image_url}', {status}, '{detail}', '{event_start_date}', '{event_end_date}' );""")
                        
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    else:
                        return JsonResponse({"message":"Title Already Exists","status":"failed"})
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
            
def get_events(request):
   
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.events""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0):
            
                return JsonResponse({"data":value,"status":"success"})
                
            else:    
                return JsonResponse({"message":"No Data Found","status":"failed"})
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
        # Parse the request body as JSON
        body = json.loads(request.body)
        
        # Extract fields from the request
        token = body.get('token', '')
        username = body.get('username', '')
        password = body.get('password', '')
        full_name = body.get('full_name', '')
        created_by = body.get('user_id', '')
        status = body.get('status', '')
        user_type = body.get('user_type', '')
        image = body.get('image', '')
        
        if token:
            # Handle database connection using Django's database router
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)  # This model should be defined earlier
            new_conn = private_connections[db]
            cursor = new_conn.cursor()

            # Query to validate token
            cursor.execute("""SELECT * FROM song_book.auth_tokens WHERE token = %s;""", [token])
            desc = cursor.description
            values = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

            if values:
                # All required fields are present
                if username and password and status and user_type and full_name:
                    encrypted_password = encrypt_aes(password)  # Encrypt password

                    # Get the latest user_id for incrementing (assuming user_id follows a pattern)
                    cursor.execute("""SELECT * FROM song_book.user_details ORDER BY id DESC LIMIT 1;""")
                    desc = cursor.description
                    value = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

                    # Assuming you have an increment_alphanumeric function to generate a new user_id
                    user_id = increment_alphanumeric(value[0]['user_id']) if value else 'user001'

                    # Prepare SQL to insert new user details
                    cursor.execute("""
                        INSERT INTO song_book.user_details 
                        (user_id, username, password, full_name, created_date, created_by, status, user_type, image) 
                        VALUES (%s, %s, %s, %s, CURRENT_DATE, %s, %s, %s, %s);
                    """, (user_id, username, encrypted_password, full_name, created_by, status, user_type, image))

                    return JsonResponse({"message": "User Created Successfully", "status": "success"})
                else:
                    return JsonResponse({"message": "Mandatory Fields Required", "status": "failed"})
            else:
                return JsonResponse({"message": "Invalid Token", "status": "failed"})
        else:
            return JsonResponse({"message": "Token is required", "status": "failed"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})     
            
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
        date_of_joining = body.get('date_of_joining','')
        contact_no = body.get('contact_no','')
        martial_status = body.get('martial_status','')
        spouse_name = body.get('spouse_name','')
        date_of_marriage = body.get('date_of_marriage','')
        spouse_occupation = body.get('spouse_occupation','')
        father_name = body.get('father_name','')
        mother_name = body.get('mother_name','')       
        spouse_image = body.get('spouse_image','')
        spouse_image_name = body.get('spouse_image_name','')
        signature = body.get('signature','')
        signature_name = body.get('signature_name','')
        image = body.get('image','')
        image_name = body.get('image_name','')
        family_image = body.get('family_image','')
        family_image_name = body.get('family_image_name','')
        comment = body.get('comment','')
        branch = body.get('branch','')
        gender = body.get('gender','')
        status = body.get('status',0)
        image_url=''
        spouse_image_url=''
        signature_url=''
        family_image_url=''
        language_speak = body.get('language_speak', '')
        language_write = body.get('language_write', '')
        spouse_adhar = body.get('spouse_adhar', '')
        mut_member = body.get('mut_member', 0)  
        mut_id = body.get('mut_id', '')
        bank_name = body.get('bank_name', '')
        account_name = body.get('account_name', '')
        account_number = body.get('account_number', '')
        ifsc = body.get('ifsc', '')
        micr = body.get('micr', '')
        blood_group = body.get('blood_group', '')
        children = body.get('children', [])
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
                    
                    if image:
                        image_url=upload_file(image,image_name,'staff/employee')
                    
                    if spouse_image:
                        spouse_image_url=upload_file(spouse_image,spouse_image_name,'staff/employee')
                    
                    if signature:
                        signature_url=upload_file(signature,signature_name,'staff/employee')
                    
                    if family_image:
                        family_image_url=upload_file(family_image,family_image_name,'staff/employee')
                    
                    
                    cursor.execute(f"""INSERT INTO `song_book`.`employee` 
(
    `reg_id`, `name`, `adhar`, `designation`, `email`, `education_qualification`, 
    `field_name`, `date_of_birth`, `address`, `people_group`, `language_speak`, 
    `language_write`, `date_of_joining`, `contact_no`, `martial_status`, `spouse_name`, 
    `date_of_marriage`, `spouse_occupation`, `father_name`, `mother_name`, 
    `spouse_adhar`, `mut_member`, `mut_id`, `bank_name`, `account_name`, 
    `account_number`, `ifsc`, `micr`, `spouse_image`, `signature`, `image`, `status`, 
    `family_image`, `comment`, `branch`, `gender`,`blood_group`
) 
VALUES 
(
    '{reg_id}', '{name}', '{adhar}', '{designation}', '{email}', '{education_qualification}', 
    '{field_name}', '{date_of_birth}', '{address}', '{people_group}', '{language_speak}', 
    '{language_write}', '{date_of_joining}', '{contact_no}', '{martial_status}', '{spouse_name}', 
    '{date_of_marriage}', '{spouse_occupation}', '{father_name}', '{mother_name}', 
    '{spouse_adhar}', {mut_member}, '{mut_id}', '{bank_name}', '{account_name}', 
    '{account_number}', '{ifsc}', '{micr}', '{spouse_image_url}', '{signature_url}', '{image_url}', 
    {status}, '{family_image_url}', '{comment}', '{branch}', '{gender}','{blood_group}'
);""")
                    cursor.execute("SELECT LAST_INSERT_ID();")
                    id = cursor.fetchone()[0]
                    cursor.execute(f"""DELETE FROM `song_book`.`employee_children` WHERE emp_id='{id}'""")
                    if len(children)>0:

                        for child in children:
                            child_name = child['child_name']
                            dob = None if not child['dob'] else child['dob']  # If empty, set as None
                            gender = None if not child['gender'] else child['gender']  # If empty, set as None
                            education = None if not child['education'] else child['education']  # If empty, set as None
                            marital_status = None if not child['marital_status'] else child['marital_status']  # If empty, set as None

                            query = """INSERT INTO `employee_children` 
                                        (child_name, dob, gender, education, marital_status, emp_id, status)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                
                            cursor.execute(query, (
                                child_name, 
                                dob, 
                                gender, 
                                education, 
                                marital_status, 
                                id, 
                                status
                            ))
                    return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
            
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
        date_of_joining = body.get('date_of_joining','')
        contact_no = body.get('contact_no','')
        martial_status = body.get('martial_status','')
        spouse_name = body.get('spouse_name','')
        date_of_marriage = body.get('date_of_marriage','')
        spouse_occupation = body.get('spouse_occupation','')
        father_name = body.get('father_name','')
        mother_name = body.get('mother_name','')
        spouse_image = body.get('spouse_image','')
        spouse_image_name = body.get('spouse_image_name','')
        signature = body.get('signature','')
        signature_name = body.get('signature_name','')
        image = body.get('image','')
        image_name = body.get('image_name','')
        family_image = body.get('family_image','')
        family_image_name = body.get('family_image_name','')
        comment = body.get('comment','')
        branch = body.get('branch','')
        gender = body.get('gender','')
        status = body.get('status',0)
        language_speak = body.get('language_speak', '')
        language_write = body.get('language_write', '')
        spouse_adhar = body.get('spouse_adhar', '')
        mut_member = body.get('mut_member', 0)  
        mut_id = body.get('mut_id', '')
        bank_name = body.get('bank_name', '')
        account_name = body.get('account_name', '')
        account_number = body.get('account_number', '')
        ifsc = body.get('ifsc', '')
        micr = body.get('micr', '')
        blood_group = body.get('blood_group', '')
        children = body.get('children', [])
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
                    if image_name:
                        image=upload_file(image,image_name,'staff/employee')
                    
                    if spouse_image_name:
                        spouse_image=upload_file(spouse_image,spouse_image_name,'staff/employee')
                    
                    if signature_name:
                        signature=upload_file(signature,signature_name,'staff/employee')
                    
                    if family_image_name:
                        family_image=upload_file(family_image,family_image_name,'staff/employee')
                    
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
                                        `language_speak` = '{language_speak}',
                                        `language_write` = '{language_write}',
                                        `date_of_joining` = '{date_of_joining}',
                                        `contact_no` = '{contact_no}',
                                        `martial_status` = '{martial_status}',
                                        `spouse_name` = '{spouse_name}',
                                        `date_of_marriage` = '{date_of_marriage}',
                                        `spouse_occupation` = '{spouse_occupation}',
                                        `father_name` = '{father_name}',
                                        `mother_name` = '{mother_name}',
                                        `spouse_adhar` = '{spouse_adhar}',
                                        `mut_member` = {mut_member},
                                        `mut_id` = '{mut_id}',
                                        `bank_name` = '{bank_name}',
                                        `account_name` = '{account_name}',
                                        `account_number` = '{account_number}',
                                        `ifsc` = '{ifsc}',
                                        `micr` = '{micr}',
                                        `spouse_image` = '{spouse_image}',
                                        `signature` = '{signature}',
                                        `image` = '{image}',
                                        `status` = {status},
                                        `family_image` = '{family_image}',
                                        `comment` = '{comment}',
                                        `branch` = '{branch}',
                                        `gender` = '{gender}',
                                        `reg_id` = '{reg_id}',
                                        `blood_group` = '{blood_group}'
                                    WHERE 
                                        `id` = {id};
                                    """)
                    cursor.execute(f"""DELETE FROM `song_book`.`employee_children` WHERE emp_id='{id}'""")
                    if len(children)>0:

                        for child in children:
                            child_name = child['child_name']
                            dob = None if not child['dob'] else child['dob']  # If empty, set as None
                            gender = None if not child['gender'] else child['gender']  # If empty, set as None
                            education = None if not child['education'] else child['education']  # If empty, set as None
                            marital_status = None if not child['marital_status'] else child['marital_status']  # If empty, set as None

                            query = """INSERT INTO `employee_children` 
                                        (child_name, dob, gender, education, marital_status, emp_id, status)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                
                            cursor.execute(query, (
                                child_name, 
                                dob, 
                                gender, 
                                education, 
                                marital_status, 
                                id, 
                                status
                            ))
                    return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
            
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
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
    
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
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
    
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
        testimony_font = body.get('testimony_font','')
        prayer_request_font = body.get('prayer_request_font','')
        obstacle_font = body.get('obstacle_font','')
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
                        
                        cursor.execute(f"""
                        INSERT INTO `song_book`.`field_report` 
                        (`employee_id`, `status`, `year`, `month`, `testimony`, `prayer_request`, `obstacles`, `new_followers`, 
                        `testimony_font`, `prayer_request_font`, `obstacle_font`)
                        VALUES 
                        ('{employee_id}', {status}, '{year}', '{month}', '{testimony}', '{prayer_request}', '{obstacles}', '{new_followers}',
                        '{testimony_font}', '{prayer_request_font}', '{obstacle_font}');
                            """)
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    else:
                        return JsonResponse({"message":"Field Report Already Exists","status":"failed"})                
                    
                    
                   
                    
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
    
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
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  

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
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
    
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
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
    
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
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
    
def save_module_access(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        user_id = body.get('user_id','')
        module_id = body.get('module_id',[])
        status = body.get('status',1)
        
        if(token and user_id):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0 ) :
                cursor.execute(f"""DELETE FROM module_access
                                    WHERE user_id = '{user_id}';""")
                for item in module_id:
                    cursor.execute(f"""INSERT INTO module_access (user_id, module_id, status)
                                        VALUES ('{user_id}', '{item}', {status});""")
                
                return JsonResponse({"data":value,"status":"success"})
            else:    
                return JsonResponse({"message":"Invalid User","status":"failed"})
        else:
            return JsonResponse({"status":"failed","message":"Mandatory Fields Required"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
    
def get_users(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        
        if(token ):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0 ) :
                cursor.execute(f"""SELECT user_id,username,full_name,user_type from song_book.user_details where id!=1""")
                
                desc = cursor.description 
                value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]
                return JsonResponse({"data":value,"status":"success"})
            else:    
                return JsonResponse({"message":"Invalid User","status":"failed"})
        else:
            return JsonResponse({"status":"failed","message":"Mandatory Fields Required"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
    
def get_module_access(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
                
            cursor.execute(f"""SELECT 
                                m.id, 
                                m.module_name,
                                m.path
                            FROM 
                                modules m
                            JOIN 
                                auth_tokens atk ON atk.token = '{token}'
                            JOIN 
                                user_details ud ON ud.user_id = atk.user_id
                            WHERE 
                                (ud.user_type = 1) 
                                OR (ud.user_type = 2 AND EXISTS (
                                    SELECT 1 
                                    FROM module_access ma 
                                    WHERE ma.user_id = ud.user_id AND ma.module_id = m.id
                                ));
                            ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]
            
            return JsonResponse({"data":value,"status":"success"})
            
        else:
            return JsonResponse({"status":"failed","message":"Please Login"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
    
def get_all_module_access(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        user_id = body.get('user_id','')
        
        if(token):
            private_connections = ConnectionHandler(settings.DATABASES)
            db = router.db_for_write(model)
            new_conn = private_connections[db]
            cursor = new_conn.cursor()
            
            cursor.execute(f"""SELECT * FROM song_book.auth_tokens where token={token} ;""")
            desc = cursor.description 
            value =  [dict(zip([col[0] for col in desc], row)) 
                    for row in cursor.fetchall()]

            if(len(value)>0 ) :    
                cursor.execute(f"""SELECT 
                        m.id, 
                        m.module_name,
                        m.path,
                        CASE 
                            WHEN ud.user_type = 1 THEN 'Selected'  -- All modules are selected for user_type 1
                            WHEN ud.user_type = 2 AND EXISTS (
                                SELECT 1 
                                FROM module_access ma 
                                WHERE ma.user_id = ud.user_id 
                                AND ma.module_id = m.id
                            ) THEN true  -- Module is selected for user_type 2
                            ELSE false  -- Module is not selected for user_type 2
                        END AS access_status
                    FROM 
                        modules m
                    
                    JOIN 
                        user_details ud ON ud.user_id = '{user_id}';
                    """)
                desc = cursor.description 
                value =  [dict(zip([col[0] for col in desc], row)) 
                        for row in cursor.fetchall()]
                
                return JsonResponse({"data":value,"status":"success"})
            else:
                return JsonResponse({"status":"failed","message":"Please Login"}) 
        else:
            return JsonResponse({"status":"failed","message":"Please Login"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
    
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
    for val in value:
        cursor.execute(f"""SELECT * from song_book.employee_children where emp_id='{val['id']}'""")
        desc = cursor.description 
        values =  [dict(zip([col[0] for col in desc], row)) 
                for row in cursor.fetchall()]
        val['children']=values
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
    
def get_gallery_images(request):
    private_connections = ConnectionHandler(settings.DATABASES)
    db = router.db_for_write(model)
    new_conn = private_connections[db]
    cursor = new_conn.cursor()
    req=json.loads(request.body)
    cursor.execute(f"""SELECT gl.name as gallery_name,gi.* FROM song_book.gallery_images gi
                        join gallery_list gl on gi.gallery_id=gl.id;""")
    desc = cursor.description 
    value =  [dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall()]
    return JsonResponse({"data":value,"status":"success"})
   
def get_gallery_list(request):
    private_connections = ConnectionHandler(settings.DATABASES)
    db = router.db_for_write(model)
    new_conn = private_connections[db]
    cursor = new_conn.cursor()
    req=json.loads(request.body)
    cursor.execute(f"SELECT * FROM song_book.gallery_list ")
    desc = cursor.description 
    value =  [dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall()]
    return JsonResponse({"data":value,"status":"success"})
   
def add_gallery_list(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')        
        name = body.get('name','')
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
                if(name and  status ):   
                    cursor.execute(f"""SELECT * FROM song_book.gallery_list where name='{name}' ;""")
                    desc = cursor.description 
                    values =  [dict(zip([col[0] for col in desc], row)) 
                        for row in cursor.fetchall()]
                    if(len(values)==0):
                        
                        cursor.execute(f"""INSERT INTO `song_book`.`gallery_list` (`name`,`status`) 
                                    VALUES ('{name}',{status});""")
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                    else:
                        return JsonResponse({"message":"Gallery Already Exists","status":"failed"})
                        
                        
                   
                    
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
 
def set_gallery_images(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        gallery_id = body.get('gallery_id','')
        image_url = body.get('image_url','')
        status = body.get('status','')
        file = body.get('file',[])
        file_name = body.get('file_name',[])
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
                if(len(file_name)>0  and status and len(file)>0):
                    
                        result = [{'file': name, 'file_name': value} for name, value in zip(file, file_name)]
                        for item in result:
                            image_url=upload_file(item['file'],item['file_name'],f'gallery/{gallery_id}')
                            cursor.execute(f"""INSERT INTO `song_book`.`gallery_images` (`file_name`, `image_url`, `status`, `gallery_id`) 
                                        VALUES ('{item['file_name']}','{image_url}', {status}, {gallery_id});""")
                        
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                   
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
 
def get_employee_document(request):
    try:
        private_connections = ConnectionHandler(settings.DATABASES)
        db = router.db_for_write(model)
        new_conn = private_connections[db]
        cursor = new_conn.cursor()
        body=json.loads(request.body)
        employee_id = body.get('employee_id','')
        token = body.get('token','')
        
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
                cursor.execute(f"""SELECT * FROM song_book.employee_documents where employee_id='{employee_id}';""")
                desc = cursor.description 
                value =  [dict(zip([col[0] for col in desc], row)) 
                        for row in cursor.fetchall()]
                return JsonResponse({"data":value,"status":"success"})
        else:
            return JsonResponse({"message":"Please Login","status":"success"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
     
def set_employee_document(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        employee_id = body.get('employee_id','')
        user_id = body.get('user_id','')
        image_url = body.get('url','')
        status = body.get('status','')
        file = body.get('file','')
        file_name = body.get('file_name','')
        title = body.get('title','')
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
                if(file_name and status and file):
                    
                        image_url=upload_file(file,file_name,f'document/{employee_id}')
                        cursor.execute(f"""INSERT INTO `song_book`.`employee_documents` (`document_name`, `url`, `status`, `employee_id`, `uploaded_by`) 
                                        VALUES ('{title}','{image_url}', {status}, '{employee_id}','{user_id}');""")
                        
                        return JsonResponse({"message":"Uploaded Successfully","status":"success"})
                   
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
     
def delete_employee_document(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        id = body.get('id','')
        file = body.get('file','')
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
                if(id and file ):                    
                    delete_file(file)
                    cursor.execute(f"""DELETE FROM `song_book`.`employee_documents` where id={id};""")                              
                    return JsonResponse({"message":"Deleted Successfully","status":"success"})
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
          
def delete_gallery_images(request):
    try:
        body=json.loads(request.body)
        token = body.get('token','')
        id = body.get('id',[])
        image = body.get('image',[])
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
                if(len(id)>0 and image ):
                    
                        result = [{'file': name, 'file_name': value} for name, value in zip(id, image)]
                        
                        for item in result:
                            delete_file(item['file_name'])
                            cursor.execute(f"""DELETE FROM `song_book`.`gallery_images` where id={item['file']};""")
                            
                        
                        return JsonResponse({"message":"Deleted Successfully","status":"success"})
                   
                else:
                    return JsonResponse({"message":"Mandatory Fields Required","status":"failed"})
                
            else:    
                return JsonResponse({"message":"Please Login","status":"failed"})
        
        else:
            return JsonResponse({"message":"Please Enter Username And Password","status":"failed"})
    except Exception as e:
        return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})  
     
     
def upload_file(image_base64, image_name, path):
    if image_base64:
        try:
            # Clean up file name: remove slashes or backslashes
            image_name = os.path.basename(image_name)

            uploaded_image = base64.b64decode(image_base64)

            media_root = settings.MEDIA_ROOT
            print("MEDIA_ROOT:", media_root)

            save_path = os.path.join(media_root, path)
            os.makedirs(save_path, exist_ok=True)

            file_path = os.path.join(save_path, image_name)
            print("Saving file to:", file_path)

            with open(file_path, 'wb') as f:
                f.write(uploaded_image)

            if os.path.exists(file_path):
                print("File saved successfully.")
            else:
                print("File not found after writing.")

            file_url = f'/media/{path}/{image_name}'
            return file_url

        except Exception as e:
            print(f"Error saving image: {e}")
            raise
    else:
        print("No image provided")
        return ''
def encrypt_aes(data: str) -> str:
    # Convert the key to bytes (ensure the key is 16 bytes long for AES-128)
    key = settings.USER_CIP_KEY.encode('utf-8')

    # Convert the data to bytes
    data_bytes = data.encode('utf-8')

    # Create AES cipher object in ECB mode (no IV required)
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()

    # Ensure data is a multiple of block size (16 bytes for AES)
    pad_length = 16 - len(data_bytes) % 16
    padded_data = data_bytes + (chr(pad_length) * pad_length).encode('utf-8')

    # Encrypt the data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Return encrypted data as a hex string (no IV used)
    return encrypted_data.hex()  # Return as hex string for easy storage

def decrypt_aes(encrypted_data: str) -> str:
    # Convert the key to bytes (ensure the key is 16 bytes long for AES-128)
    key = settings.USER_CIP_KEY.encode('utf-8')

    # Convert the hexadecimal string back to bytes
    encrypted_data_bytes = bytes.fromhex(encrypted_data)

    # Create AES cipher object in ECB mode (no IV required)
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the data
    decrypted_data = decryptor.update(encrypted_data_bytes) + decryptor.finalize()

    # Remove padding
    pad_length = decrypted_data[-1]
    return decrypted_data[:-pad_length].decode('utf-8') 


def delete_file(image):
    if image:
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        aws_default_region = settings.AWS_DEFAULT_REGION
        
        
        session = boto3.Session()
        s3 = session.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_default_region
        )

        try:
           

            bucket_name = 'bcmmission'
           
            s3.delete_object(Bucket=bucket_name, Key=image)
            return True


        except Exception as e:
            print(f"An error occurred: {e}")
            return ''
    else:
        print('No image provided')
        return ''