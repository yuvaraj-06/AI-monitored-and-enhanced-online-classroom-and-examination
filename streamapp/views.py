import os
from moviepy.editor import *
import moviepy.editor as mp
from os.path import dirname, join
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http.response import StreamingHttpResponse
from streamapp.camera import VideoCamera
from django.template.loader import render_to_string
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from django.template import loader, Context
from json import dumps 
from django.template.defaulttags import register
from threading import Thread
import requests
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence



import base64
#path='/staticfiles'
cloud_config= {
        'secure_connect_bundle': join(dirname(__file__), "secure-connect-database.zip")
}
auth_provider = PlainTextAuthProvider('Datauser', 'database@1')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

row = session.execute("select release_version from system.local").one()
if row:
    print(row[0])
else:
    print("An error occurred.")
session.set_keyspace('data')

############

ids=[]


def index(request):
    return render(request, 'streamapp/input.html')
def quiz(request):

    return render(request, 'streamapp/copyquiz.html',{'a':3,'q1':{"QUESTION 1 Who developed the Python language?":['.py','.p','.c','.java'],"Which one of the following is the correct extension of the Python file?":['Zim Den','Guido van Rossum','Niene Stom','Wick van Rossum','.py','.python','.p','.java'],"QUESTION 1 Who developed the Python language?":['.py','.p','.c','.java'],"Which one of the following is the correct extension of the Python file?":['Zim Den','Guido van Rossum','Niene Stom','Wick van Rossum','.py','.python','.p','.java'],"QUESTION 1 Who developed the Python language?":['.py','.p','.c','.java'],"Which one of the following is the correct extension of the Python file?":['Zim Den','Guido van Rossum','Niene Stom','Wick van Rossum','.py','.python','.p','.java']}})
def take(request):
    global ids
    st=request.POST.get('st')
    user = request.POST.get('user')
    b = request.POST.get('pass')
    if st.lower()=="teacher":
        ids.append(user)
        futures = []
        query = "SELECT id FROM teacher"
        futures.append(session.execute_async(query))
        l = []
        for future in futures:
            rows = future.result()
            l.append(str(rows[0].id))
        if user in l:
            c = "Sorry" + " " + "Please Login Account Already Exists"
            return render(request, 'streamapp/input.html', {'resultt': c})
        else:
            insert_statement = session.prepare("INSERT INTO teacher (id,psw) VALUES (?,?)")
            session.execute(insert_statement, [user, b])
            c =user.capitalize() 
            return render(request, 'streamapp/landt.html', {'user': c})
    else:
        ids.append(user)
        futures = []
        query = "SELECT id FROM userdata"
        futures.append(session.execute_async(query))
        l = []
        for future in futures:
            rows = future.result()
            l.append(str(rows[0].id))
        if user in l:
            c = "Sorry" + " " + "Please Login Account Already Exists"
            return render(request, 'streamapp/input.html', {'resultt': c})
        else:
            insert_statement = session.prepare("INSERT INTO userdata (id,pass) VALUES (?,?)")
            session.execute(insert_statement, [user, b])
            c =user.capitalize() 
            return render(request, 'streamapp/landt.html', {'user': c})

def add(request):
    global dpass
    global ids
    global user
    dpass=""
    st=request.POST.get('st')
    user=request.POST.get('user')
    passl=request.POST.get('pass')
    if False:
        print('cart id exists')
    else:
        if st.lower()!="teacher":
            try:
                query = "SELECT * FROM userdata WHERE id=%s"
                a=session.execute_async(query, [user])
                #for future in futures:
                rows = a.result()
                print(rows[0].field_2_)
                dpass=rows[0].field_2_
                if passl==dpass:
                    c =user.capitalize() 
                    return render(request, 'streamapp/lands.html', {'user': c})
                else:
                    c = "Sorry" + " " + user +" Wrong Password Please Try Again"
                    return render(request, 'streamapp/input.html', {'result': c})
            except:
                c = "Sorry" + " " + user +" Please Sign Up Try Again"
                return render(request, 'streamapp/input.html', {'result': c})
        else:
            try:
                query = "SELECT * FROM teacher WHERE id=%s"
                a=session.execute_async(query, [user])
                #for future in futures:
                rows = a.result()
                print(rows[0].psw)
                dpass=rows[0].psw
                if passl==dpass:
                    c =user.capitalize() 
                    return render(request, 'streamapp/landt.html', {'user': c})
                else:
                    c = "Sorry" + " " + user +" Wrong Password Please Try Again"
                    return render(request, 'streamapp/input.html', {'result': c})
            except:
                c = "Sorry" + " " + user +" Please Sign Up Try Again"
                return render(request, 'streamapp/input.html', {'result': c})
        

Test=False
frame1=""
def gen(camera):
    global frame1
    global Test
    global user
    while True:
        if Test==True:
            print(frame1)
            session.set_keyspace('data')
            insert_statement = session.prepare("INSERT INTO userdata (id,marks) VALUES (?,?)")
            session.execute(insert_statement, [user,str(frame1)])
            print("finaly break")
            break
        frame,frame1 = camera.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_fee(request):
        global Test
        print("I AM THERE")
        Test=True
        c=request.POST.get('num1')
       # c = "WELCOME" + " " +"THIS IS YOUR TEST SUMMARY"
        futures = []
        query = "SELECT * FROM userdata WHERE id=%s"
 
        futures.append(session.execute_async(query,[user]))
        l = []
        for future in futures:
            rows = future.result()
            l.append(str(rows[0].marks))
            a=str(rows[0].marks).split(" ")
            print(l,a)
            c=a
        
        a1=c[-1]
        print(a)

        return render(request, 'streamapp/marks.html', {'c': a[:-1],'c1':['Number of Times Mouth Opened','Number of Times Head Up','Number of Times Head Down','Number of Times Head Left','Number of Times Head Right','Number of Times Left the Test'],'s':a1})

def video_feed(request):
    print(Test)
    if not(Test):
        return StreamingHttpResponse(gen(VideoCamera()),
                        content_type='multipart/x-mixed-replace; boundary=frame')
    print("video freed")
    return render(request, 'streamapp/wrong.html', {'res': "bryeu", 'data': False})
global l
l=[]
def video(request):
    fileObj=request.FILES['in']
    fs=FileSystemStorage()
    filePathName=fs.save(fileObj.name,fileObj)
    filePathName=fs.url(filePathName)
    p="C:/Users/tanka/Downloads/video_stream-master/video_stream-master"+filePathName
    print(p)
    return render(request, 'streamapp/landt.html',{'res':"File Uploaded Sucessfull",'user':'Joseph'})
def startexm(request):
    return render(request, 'streamapp/home.html',{'user':user})
def record(request):
    return render(request, 'streamapp/rec.html')
def vid(request):
    if "1" in request.POST:
        futures = []
        query = "SELECT * FROM teacher"
        ids_to_fetch=[1]
        for user_id in ids_to_fetch:
            futures.append(session.execute_async(query))
        for i in futures:
            rows = i.result()
            a=rows[0].trans
        a=a.strip('][').split(',') 
        s=a[0].strip("'")
        return render(request, 'streamapp/recout.html',{'res':s})
    elif "2" in request.POST: 
        futures = []
        query = "SELECT * FROM teacher"
        ids_to_fetch=[1]
        for user_id in ids_to_fetch:
            futures.append(session.execute_async(query))
        for i in futures:
            rows = i.result()
            a=rows[1].trans
        a=a.strip('][').split(',') 
        s=a[0].strip("'")
        return render(request, 'streamapp/recout.html',{'res':s})
  
def trans(request):
    if "1" in request.POST:
        futures = []
        query = "SELECT * FROM teacher"
        ids_to_fetch=[1]
        for user_id in ids_to_fetch:
            futures.append(session.execute_async(query))
        for i in futures:
            rows = i.result()
            a=rows[0].trans
        a=a.strip('][').split(',') 
        return render(request, 'streamapp/transout.html',{'res':a[1]})
    elif "2" in request.POST: 
        futures = []
        query = "SELECT * FROM teacher"
        ids_to_fetch=[1]
        for user_id in ids_to_fetch:
            futures.append(session.execute_async(query))
        for i in futures:
            rows = i.result()
            a=rows[1].trans
        a=a.strip('][').split(',')
        return render(request, 'streamapp/transout.html',{'res':a[1]})