from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'student'



@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            return render_template('searchEmp.html')
        elif request.form['username'] == 'student' and request.form['password'] == 'student':
            return render_template('registration.html')
        elif request.form['username'] == 'company' and request.form['password'] == 'company':
            return render_template('companyRegistration.html')
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)


# register page - sign up button
@app.route("/registraion", methods=['POST'])
def AddEmp():
    stu_id = request.form['stu_id']
    stu_name = request.form['stu_name']
    stu_email = request.form['stu_email']
    # emp_bod = request.form['emp_bod']
    # emp_hire_date = request.form['emp_hire_date']
    # emp_salary = request.form['emp_salary']
    company = request.form['company']
    # emp_interest = request.form['emp_interest']
    stu_report_file = request.files['stu_report_file']

    insert_sql = "INSERT INTO student VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if stu_report_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (stu_id, stu_name, stu_email, company))
        db_conn.commit()
        # Uplaod image file in S3 #
        stu_report_file_name_in_s3 = "stu-id-" + str(stu_id) + "_pdf_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=stu_report_file_name_in_s3, Body=stu_report_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                stu_report_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('registerSuccess.html', name=stu_name)


# Company register page - sign up button
@app.route("/companyRegistraion", methods=['POST'])
def AddCmp():
    cmp_id = request.form['cmp_id']
    cmp_name = request.form['cmp_name']
    cmp_email = request.form['cmp_email']
    # emp_bod = request.form['emp_bod']
    # emp_hire_date = request.form['emp_hire_date']
    # emp_salary = request.form['emp_salary']
    # cmp_image = request.form['cmp_image']
    # emp_interest = request.form['emp_interest']
    # stu_report_file = request.files['stu_report_file']

    insert_sql = "INSERT INTO company VALUES (%s, %s, %s)"
    cursor = db_conn.cursor()

    # if cmp_image.filename == "":
    #     return "Please select a file"

    try:

        cursor.execute(insert_sql, (cmp_id, cmp_name, cmp_email))
        db_conn.commit()
        # Uplaod image file in S3 #
        # cmp_image_name_in_s3 = "cmp-id-" + str(cmp_id) + "_pdf_file"
        # s3 = boto3.resource('s3')

        # try:
        #     print("Data inserted in MySQL RDS... uploading image to S3...")
        #     s3.Bucket(custombucket).put_object(Key=cmp_image_name_in_s3, Body=cmp_image)
        #     bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
        #     s3_location = (bucket_location['LocationConstraint'])

        #     if s3_location is None:
        #         s3_location = ''
        #     else:
        #         s3_location = '-' + s3_location

        #     object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
        #         s3_location,
        #         custombucket,
        #         cmp_image_name_in_s3)

        # except Exception as e:
        #     return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('registerSuccessCompany.html', name=cmp_name)


# register page - search employee button
@app.route("/searchEmpButton", methods=['POST','GET'])
def search():
    return render_template('searchEmp.html')


# student success page - back button
@app.route("/registerSuccess", methods=['POST'])
def back1():
    return render_template('login.html')


# company register success page - back button
@app.route("/companyRegisterSuccess", methods=['POST'])
def back2():
    return render_template('login.html')


#searh to portfolio page
@app.route("/portfolio", methods=['POST'])
def portfolio():
    return render_template('portfolio.html')
    

# search emp page - search emp function to search
@app.route("/livesearch", methods=["POST", "GET"])
def livesearch():
    searchbox = request.form.get("text")
    cursor = db_conn.cursor()
    query = "select * from student where stu_id LIKE '%{}%' OR stu_name LIKE '%{}%' OR stu_email LIKE '%{}%' OR company LIKE '%{}%' ".format(searchbox, searchbox, searchbox, searchbox)#This is just example query , you should replace field names with yours
    cursor.execute(query)
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/update',methods=['POST'])
def update():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        email = request.form['email']
        # bod = request.form['bod']
        # hire_date = request.form['hire_date']
        # salary = request.form['salary']
        company = request.form['company']
        # interest = request.form['interest']
        cur = db_conn.cursor()
        cur.execute("""UPDATE student SET stu_name = %s, stu_email = %s, company = %s WHERE stu_id = %s""", (name, email, company, id))
        db_conn.commit()
        return redirect(url_for('search'))
    

@app.route('/delete/<string:id>', methods = ['GET'])
def delete(id):
    cur = db_conn.cursor()
    print(id)
    cur.execute("delete from student where stu_id = %s", id)
    db_conn.commit()
    cur.close()
    return redirect(url_for('search'))


# search emp page - back button
@app.route("/backButton", methods=['POST'])
def back3():
    return render_template('login.html')


# download file
@app.route('/download/<string:id>', methods=['GET', 'POST'])
def download(id):
    key = f"stu-id-{id}_pdf_file"

    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(bucket)

    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='application/pdf',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )

# # employee details page - show employee details
# @app.route("/empDetails", methods=['POST'])
# def back3():
#     return render_template('')  

# # employee details page - back button
# @app.route("/backToRegisterButton", methods=['POST'])
# def back():
#     return render_template('registration.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
