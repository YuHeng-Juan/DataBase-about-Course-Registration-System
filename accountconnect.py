import sys
from flask import Flask, jsonify, request,render_template,session,redirect,url_for
import pymysql 
import requests
import traceback
import cgi
from flask_session import Session

import os

app = Flask(__name__)
student_ID=""
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = False  
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 7200
app.config['SESSION_FILE_THRESHOLD'] = 100  
app.config['SECRET_KEY'] = "bobb0711"

db= pymysql.connect("140.134.53.65","admin","admin123456","db_project")
cursor=db.cursor()

@app.route('/') #進入點
def f_index():
    session.clear()
    return render_template('index.html')

@app.route('/index') #登入畫面
def login_in():
    session.clear()
    return render_template('index.html')

@app.route('/action', methods=['GET', 'POST'])
def index():
    session.clear()
    ID = request.values['username']
    pwd =request.values['password']
    
    
    if(ID.isupper):
        ID=ID.upper()
    
    cursor.execute("SELECT * FROM `student` WHERE s_id='%s' and s_password='%s'"%(ID,pwd))
    data =cursor.fetchone()

    if(data!=None):
        session['username']=ID
        session['password']=pwd
        session['name']=data[1]
        session['Class']=data[4]
        if(data[3]==1):
             session['login_message']=2
             login_message=2
        else:
             session['login_message']=1
             login_message=1
       
        return render_template('searchCourse.html',alert_msg=0,login_message=login_message,student=ID,name=data[1],Class=data[4])
    else:
        return render_template('fail.html')
    
@app.route('/searchCourse')  #課程檢索
def f_sear1ch1():
    student=session.get('username')
    name=session.get('name')
    Class=session.get('Class')
    login_message=session.get('login_message')
    alert_msg=""
     
    return render_template('searchCourse.html',alert_msg=alert_msg,student=student,name=name,Class=Class,login_message=login_message)
@app.route('/research')  #課程檢索
def research():   
    student=session.get('username')
    name=session.get('name')
    Class=session.get('Class')
    login_message=session.get('login_message')
    msg=request.values['alert_msg']
    print(msg)
    return render_template('searchCourse.html',alert_msg=msg,student=student,name=name,Class=Class,login_message=login_message)
        
@app.route('/search1', methods=['GET', 'POST']) # 下拉式選單
def search():
    student=session.get('username')
    name=session.get('name')
    Class=session.get('Class')
    login_message=session.get('login_message')
    
    college=(str(request.form['college']))
    query="SELECT *,if(COUNT(section)>1,section+COUNT(section)-1,section) AS endsection  FROM course NATURAL JOIN coursetime GROUP BY c_id,day HAVING  course.class='%s'"%(college)
    cursor.execute(query)
    data =cursor.fetchall()
    for  value in data:
         print(value)
    return render_template('Courselist.html',books=data,student=student,name=name,Class=Class,login_message=login_message)

@app.route('/search2', methods=['GET', 'POST']) #textbox搜尋
def search2():
    
    student=session.get('username')
    name=session.get('name')
    Class=session.get('Class')
    login_message=session.get('login_message')
    
    c_id=(str(request.form['C_ID']))
    c_name=(str(request.form['C_name']))
    t_id=(str(request.form['T_ID']))
    query="SELECT *,if(COUNT(section)>1,section+COUNT(section)-1,section) AS endsection  FROM course NATURAL JOIN coursetime GROUP BY c_id,day HAVING "
    if(c_id!="" and c_name!="" and t_id!=""):
        query+="course.c_id LIKE \"%%%s%%\" and course.c_name LIKE \"%%%s%%\" and course.instructor LIKE \"%%%s%%\""%(c_id,c_name,t_id)
    elif(c_id!="" and c_name!=""):
        query+="course.c_id LIKE \"%%%s%%\" and course.c_name LIKE \"%%%s%%\""%(c_id,c_name)
    elif(c_id!="" and t_id!=""):
        query+="course.c_id LIKE \"%%%s%%\" and course.instructor LIKE \"%%%s%%\""%(c_id,t_id)
    elif(c_name!="" and t_id!=""):
        query+="course.c_name LIKE \"%%%s%%\" and course.instructor LIKE \"%%%s%%\""%(c_name,t_id)    
    elif(c_id!=""):
        query+="course.c_id LIKE \"%%%s%%\""%(c_id)
    elif(c_name!=""):
        query+="course.c_name LIKE \"%%%s%%\""%(c_name)
    elif(t_id!=""):
        query+="course.instructor LIKE \"%%%s%%\""%(t_id)
    else:
        return "None"
    cursor.execute(query)
    data =cursor.fetchall()
    for  value in data:
         print(value)
    return render_template('Courselist.html',books=data,student=student,name=name,Class=Class,login_message=login_message)

@app.route('/Courselist_admin', methods=['GET', 'POST']) # admin 搜尋學生課表
def search3():
    student=session.get('username')
    name=session.get('name')
    Class=session.get('Class')
    login_message=session.get('login_message')
    
    stu_id=str(request.form['stu_id'])
    stu_id=stu_id.upper()
    query="SELECT c_id,s_id,c_name,credits,queue,day,section,section+COUNT(section)-1 AS endsection FROM course natural join(timetable NATURAL JOIN coursetime)GROUP BY s_id,c_id,day HAVING s_id='%s'"%(stu_id)
    cursor.execute(query)
    data =cursor.fetchall()
    for  value in data:
         print(value)
    return render_template('Courselist_admin.html',books=data,student=student,name=name,Class=Class,login_message=login_message)
    
    

@app.route('/add')  # 加選課程
def add():
    student=session.get('username')
    name=session.get('name')
    Class=session.get('Class')
    login_message=session.get('login_message')
    message="加選成功"
    course=list(request.args.values())
    
    cursor.execute("SELECT c_id,s_id,c_name,credits,queue,day,section,section+COUNT(section)-1 AS endsection FROM course natural join(timetable NATURAL JOIN coursetime)GROUP BY s_id,c_id,day HAVING s_id=\"%s\""%(student))
    data=cursor.fetchall()

    cursor.execute("SELECT *,section+COUNT(section)-1 AS endsection FROM course NATURAL JOIN coursetime GROUP BY c_id,day HAVING course.c_id ='%s'"%(course[0]))
    coursetime=cursor.fetchall()
    print(course)
    
    for i in coursetime:#判斷衝堂
        for j in data:
            if(i[8]==j[5] and int(i[9])<=int(j[6]) and int(i[10])>=int(j[7])):
                print(i)
                print(j)
                return redirect(url_for('research',alert_msg="衝堂",student=student,name=name,Class=Class,login_message=login_message))
    
 
    credit=int(0)
    sum_cre=int(0)
    for i in data:#判斷重複選課and課程人數
        if(course[1]==i[2]):
            return redirect(url_for('research',alert_msg="不可重複選課",student=student,name=name,Class=Class,login_message=login_message))
    if(int(course[4])>=int(course[5])):
        return redirect(url_for('research',alert_msg="課程人數已滿",student=student,name=name,Class=Class,login_message=login_message))    
        
    cursor.execute("SELECT credits FROM course natural join timetable GROUP BY s_id,c_id HAVING s_id='%s'"%(student)) # 判斷學分是否超過30學分
    credit=cursor.fetchall()
    for i in credit:
        sum_cre+=i[0]
    
    if(int(sum_cre)+int(course[3])>30):
        print(int(sum_cre)+int(course[3]))
        return redirect(url_for('research',alert_msg="超過30學分",student=student,name=name,Class=Class,login_message=login_message))
    
    cursor.execute("INSERT INTO timetable(s_id,c_id,queue) VALUES ('%s','%s',0);"%(student,course[0]))#加選
    cursor.execute("UPDATE `course` SET `num_of_students`=%d WHERE `c_id`='%s'"%(int(course[4])+1,course[0])) 
    db.commit()
    
    return redirect(url_for('research',alert_msg="加選成功",student=student,name=name,Class=Class,login_message=login_message))

@app.route('/pop') #退選課程
def pop():
    student=session.get('username')
    name=session.get('name')
    Class=session.get('Class')
    login_message=session.get('login_message')
    alert_msg=""
    course=list(request.args.values())
    credit=int(0)
    cursor.execute("SELECT sum(credits) FROM timetable join course WHERE `s_id`='%s'"%(student)) # 判斷學分是否低於12學分
    credit=cursor.fetchall()
    
    
    sum_cre=int(0)   
    cursor.execute("SELECT c_name FROM timetable join course WHERE c_name='%s'"%(course[1]))
    noclass=cursor.fetchall()

    cursor.execute("SELECT credits FROM course natural join timetable GROUP BY s_id,c_id HAVING s_id='%s'"%(student)) # 判斷學分是否超過30學分
    credit=cursor.fetchall()
    for i in credit:
        sum_cre+=i[0]
        
    if(len(noclass)==0):
        return redirect(url_for('research',alert_msg="課表無此課",student=student,name=name,Class=Class,login_message=login_message))   
    if(int(sum_cre)-int(course[3])<12):
        return redirect(url_for('research',alert_msg="低於12學分不可退選",student=student,name=name,Class=Class,login_message=login_message))#低於12學分
    if(course[2]=="M" and course[6]==Class):
        return redirect(url_for('research',alert_msg="必修不可退",student=student,name=name,Class=Class,login_message=login_message))#必修不可退
    
    
    cursor.execute("DELETE FROM timetable WHERE s_id='%s' and c_id='%s';"%(student,course[0]))
    cursor.execute("UPDATE `course` SET `num_of_students`=%d WHERE `c_id`='%s'"%(int(course[4])-1,course[0])) 
    db.commit()
    return redirect(url_for('research',alert_msg="退選成功",student=student,name=name,Class=Class,login_message=login_message))

@app.route('/pop1') #admin退選課程
def pop1():
    student=session.get('username')
    name=session.get('name')
    Class=session.get('Class')
    login_message=session.get('login_message')
    alert_msg=""
    course=list(request.args.values())
    print(course)
    cursor.execute("DELETE FROM timetable WHERE s_id='%s' and c_id='%s'and queue=0;"%(course[1],course[0]))
    cursor.execute("SELECT num_of_students FROM `course` WHERE c_id='%s'"%(course[0]))
    data=cursor.fetchone()
    print(str(data[0]))
    cursor.execute("UPDATE `course` SET `num_of_students`=%d WHERE `c_id`='%s'"%(int(str(data[0]))-1,course[0])) 
    db.commit()
    return redirect(url_for('research',alert_msg="退選成功",student=student,name=name,Class=Class,login_message=login_message))
    
@app.route('/schedule') #課表
def schedule():
    student=session.get('username')
    name=session.get('name')
    Class=session.get('Class')
    login_message=session.get('login_message')
    
    cursor.execute("SELECT c_id,s_id,c_name,credits,queue,day,section,section+COUNT(section)-1 AS endsection FROM course natural join(timetable NATURAL JOIN coursetime)GROUP BY s_id,c_id,day HAVING s_id=\"%s\""%(student))
    data=cursor.fetchall()
    print(session.get('name'),session.get('Class'))
    
    list1=[]
    list1.append((len(data),"",0,0))
    n=int(0)
    for i in data:
        print(i)
        if(i[5]=='一'): n=1
        elif(i[5]=='二'): n=2
        elif(i[5]=='三'): n=3
        elif(i[5]=='四'): n=4
        elif(i[5]=='五'): n=5
        elif(i[5]=='六'): n=6
        elif(i[5]=='日'): n=7
        else: n=0
        list1.append((n,i[2],i[6],i[7]))
    for i in list1:
        print(i)
    return render_template('schedule.html',books=list1,student=student,name=name,Class=Class,login_message=login_message)




        
     
    
if __name__ == "__main__": 
    app.run(debug=False, host='127.0.0.1', port=5566)  
    sys.exit()
    
