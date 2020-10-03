#!/usr/bin/env python3
# coding=utf-8
# -*- coding: UTF-8 -*-
import sys
from flask import Flask, jsonify, request, render_template
import MySQLdb
import traceback

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('test.html')

@app.route('/action', methods=['POST'])
def action():
    # 建立資料庫連線
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="jimmy",
                           passwd="test1234",
                           db="testdb")
    # 欲查詢的 query 指令

    user = request.form.get("username")
    pwd = request.form.get("password")
    query = "SELECT * FROM admin where A_ID= '{user}'".format(user=user) + " and A_password='{pwd}'".format(pwd=pwd)
    query2 = "SELECT * FROM students where S_ID= '{user}'".format(user=user) + " and S_password='{pwd}'".format(pwd=pwd)
    print(type(request.form.get("username")))
    # 執行查詢
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print(len(results))
        if len(results) == 1:
            return render_template('adminPage.html')
        else:
            print("123")
            cursor.execute(query2)
            results = cursor.fetchall()
            if len(results)==1:
                return render_template('studentPage.html')
            else:
                return 'failed login'
    except:
        traceback.print_exc()
        conn.rollback()
        print("XXXXXX")
    # 取得並列出所有查詢結果
    # for (description, ) in cursor.fetchall():
    #     results += "<p>{}</p>".format(description)


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
    sys.exit()
