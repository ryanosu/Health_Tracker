from flask import Flask, render_template, redirect, url_for, request, session
from flask_mysqldb import MySQL
import MySQLdb.cursors, re, os, timeit
from flask_bootstrap import Bootstrap
import requests
import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
import time
from dotenv import load_dotenv

#load_dotenv()
application = Flask(__name__)
Bootstrap(application)
mysql = MySQL(application)

# database connection info
# app.config["MYSQL_HOST"] = os.getenv('app.config["MYSQL_HOST"]')
# app.config["MYSQL_USER"] = os.getenv('app.config["MYSQL_USER"]')
# app.config["MYSQL_PASSWORD"] = os.getenv('app.config["MYSQL_PASSWORD"]')
# app.config["MYSQL_DB"] = os.getenv('app.config["MYSQL_DB"]')
# app.secret_key = os.getenv('app.secret_key')
# app.config["SESSION_TYPE"] = os.getenv('app.config["SESSION_TYPE"]')

# Nutrition API client key
# nutrition_api_client_primary_key = os.getenv('nutrition_api_client_primary_key')

#################################################################################
#                                                                               #
#                           Functionality Begins                                #
#                                                                               #
#################################################################################

#################################################################################
#                                                                               #
#                                  CRUD                                         #
#                                                                               #
################################################################################# 

@application.route('/main', methods = ['POST', 'GET'])
def main():
    if 'loggedin' not in session:
        return render_template("login.html")

    # read data
    def helper_func_read():
        query = f"SELECT * FROM food_calories WHERE users_id={session['id']};"
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        new_data = []
        for i in range(len(data)):
            new_data.append([data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], data[i][5]])
        data = new_data
        cursor.close()
        return data

    # sum calories column
    def helper_func_sum():
        total_query = f"SELECT SUM(calories) FROM food_calories WHERE users_id={session['id']};"
        cursor = mysql.connection.cursor()
        cursor.execute(total_query)
        total_amount = cursor.fetchone()
        total_amount = int(total_amount[0] or 0)
        return total_amount
    
    # sum protein column
    def helper_func_sum_protein():
        total_query = f"SELECT SUM(protein) FROM food_calories WHERE users_id={session['id']};"
        cursor = mysql.connection.cursor()
        cursor.execute(total_query)
        total_amount_protein = cursor.fetchone()
        total_amount_protein = int(total_amount_protein[0] or 0)
        return total_amount_protein

    # sum fat column
    def helper_func_sum_fat():
        total_query = f"SELECT SUM(fat) FROM food_calories WHERE users_id={session['id']};"
        cursor = mysql.connection.cursor()
        cursor.execute(total_query)
        total_amount_fat = cursor.fetchone()
        total_amount_fat = int(total_amount_fat[0] or 0)
        return total_amount_fat

    # sum carbs column
    def helper_func_sum_carbs():
        total_query = f"SELECT SUM(carbs) FROM food_calories WHERE users_id={session['id']};"
        cursor = mysql.connection.cursor()
        cursor.execute(total_query)
        total_amount_carbs = cursor.fetchone()
        total_amount_carbs = int(total_amount_carbs[0] or 0)
        return total_amount_carbs

    # create data
    def helper_func_create(name, calories, protein, fat, carbs):
        query = f"INSERT INTO food_calories (name, calories, protein, fat, carbs, users_id) VALUES ('{name}', '{calories}', '{protein}', '{fat}', '{carbs}','{session['id']}')"
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        mysql.connection.commit()
    
    # update data
    def helper_func_update(name, calories, protein, fat, carbs, food_calories_id):
        update_query = f"UPDATE food_calories SET name='{name}', calories='{calories}', protein='{protein}', fat='{fat}', carbs='{carbs}' WHERE `food_calories_id`='{food_calories_id}';"
        cursor = mysql.connection.cursor()
        cursor.execute(update_query)
        mysql.connection.commit()

    # get goal_cal
    def helper_func_goal_cal():
        query = f"SELECT goal_cal FROM users WHERE users_id={session['id']};"
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        goal_cal = cursor.fetchall()
        return goal_cal
    
    # change goal_cal
    def helper_func_goal_cal_change(new_goal_cal):
        query = f"UPDATE users SET goal_cal = '{new_goal_cal}' WHERE users_id={session['id']};"
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        mysql.connection.commit()
    
    # query the USDA API
    def helper_nutrition_api(search):
        protein = None
        fat = None
        carbs = None
        cal = None
        headers = {
            'Accept': 'application/json'
                    }
        params = urllib.parse.urlencode({
            'query': search,
            'api_key': nutrition_api_client_primary_key,
            'pageSize': 1
                    })
        try:
            url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
            resp = requests.get(url=url, headers=headers, params=params)
            resp = resp.json()
            resp = resp["foods"][0]["foodNutrients"]
            # parse the json
            for i in range(len(resp)):
                if not protein or not carbs or not fat or not cal:
                    if resp[i]["nutrientName"] == "Protein":
                        protein = resp[i]["value"]

                    if resp[i]["nutrientName"] == 'Total lipid (fat)':
                        fat = resp[i]["value"]

                    if resp[i]["nutrientName"] == 'Carbohydrate, by difference':
                        carbs = resp[i]["value"]

                    if resp[i]["nutrientName"] == 'Energy':
                        cal = resp[i]["value"]
                else:
                    break
        except requests.exceptions.RequestException as e:
            print(e)
        if protein and fat and carbs and cal:
            return (cal, protein, fat, carbs)
        else:
            return None


    if request.method == 'GET':
        data = helper_func_read()
        total_amount = helper_func_sum()
        total_amount_protein = helper_func_sum_protein()
        total_amount_fat = helper_func_sum_fat()
        total_amount_carbs = helper_func_sum_carbs()
        goal_cal = helper_func_goal_cal()
        goal_cal = goal_cal[0][0]
        return render_template("main.html", data=data, total_amount=total_amount, goal_cal=goal_cal, 
        total_amount_protein=total_amount_protein, total_amount_fat=total_amount_fat, total_amount_carbs=total_amount_carbs)
    
    if request.method == 'POST':
        # add inputted food
        if request.form.get("add_food"):
            name = request.form['name']
            calories = request.form['calories']
            protein = request.form['protein']
            fat = request.form['fat']
            carbs = request.form['carbs']
            helper_func_create(name, calories, protein, fat, carbs)
            return redirect("/main")
        # change calorie goal
        if request.form.get("change_cal_goal_new"):
            goal_cal = request.form["change_cal_goal_new"]
            helper_func_goal_cal_change(goal_cal)
            return redirect("/main")
        # query the API
        if request.form.get("query_string"):
            search = request.form["query_string"]
            database_api_data = helper_nutrition_api(search)
            # (name, calories, protein, fat, carbs)
            if database_api_data:
                helper_func_create(search, database_api_data[0], database_api_data[1], database_api_data[2], database_api_data[3])
            else:
                print("MUST TYPE IN FOOD MANUALLY")
            return redirect("/main")
        # update row
        if request.form.get("update_food"):
            name = request.form['name']
            calories = request.form['calories']
            protein = request.form['protein']
            fat = request.form['fat']
            carbs = request.form['carbs']
            food_calories_id = request.form['food_calories_id']
            helper_func_update(name, calories, protein, fat, carbs, food_calories_id)
            return redirect("/main")

# deletes all food and calories information (not actual back end table)
@application.route("/delete_table")
def delete_table():
    query = "DELETE FROM food_calories;"
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    return redirect("/main")

# delete a single row in the table (name of food, calories)
@application.route("/delete_row/<row_to_delete>")
def delete_row(row_to_delete):
    query = f"DELETE FROM food_calories WHERE food_calories_id={row_to_delete}"
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    return redirect("/main")

# update variables on separate page
@application.route("/update_page/<row_to_update>")
def update_page(row_to_update):
    query = f"SELECT * FROM food_calories WHERE food_calories_id={row_to_update};"
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("/update_page.html", data=data)

#################################################################################
#                                                                               #
#                                   MISC                                        #
#                                                                               #
################################################################################# 

# non-functional requirement/server response speed test
@application.route("/time")
def time_test():
    total_seconds = 0
    for i in range(10):
        seconds = timeit.timeit(stmt="main()", setup="from __main__ import main", number=1)
        total_seconds = total_seconds + seconds
    print("Average Number of Seconds:", total_seconds / 10)
    return redirect("/main")

#################################################################################
#                                                                               #
#                           Profile Functionality                               #
#                                                                               #
################################################################################# 

@application.route('/')
@application.route("/login", methods=["GET", "POST"])
def login():
    if 'loggedin' in session:
        return redirect("/main")
    msg = ''
    # Check if user submitted form
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        # If account exists in users table
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['users_id']
            session['username'] = account['username']
            print("Logged in!")
            return redirect("/main")
        else:
            msg = 'Incorrect username/password!'
    return render_template("login.html", msg=msg)

@application.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@application.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    # Check if user submitted form
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        # validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account does not exists and form data is valid
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s)', (username, password, email, 2500))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    # form empty
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@application.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE users_id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

if __name__ == "__main__":
    # port = int(os.environ.get('PORT', 13132))
    # app.run(port=port, debug=True)
    application.debug = True
    application.run()