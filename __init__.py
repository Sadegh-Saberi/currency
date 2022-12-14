from flask import Flask
from flask import render_template
# replace it with a new db path if 
db_path = "/var/www/webApp/webApp/database.sqlite"
import sqlite3

app = Flask(__name__)
connection_timeout = 3600

def currencies_value_sorter(list_):
    try:
        result = float(list_[-1])
        return result
    except:
        return 0

def currencies2_value_sorter(list_):
    try:
        result = float(list_[3])
        return result
    except:
        return 0

def currencies_data():
    with sqlite3.connect(db_path,timeout=connection_timeout) as connection:
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM currencies;").fetchall()
        result.sort(key=currencies_value_sorter,reverse=True)
        return result

def currencies2_data():
    with sqlite3.connect(db_path,timeout=connection_timeout) as connection:
        cursor = connection.cursor()
        result =  cursor.execute("SELECT * FROM currencies2;").fetchall()
        result.sort(key=currencies2_value_sorter,reverse=True)
        return result


@app.route("/currencies")
def currencies():
    data = currencies_data()
    return render_template("1.html",currencies=data)

@app.route("/currencies2")
def currencies2():
    data = currencies2_data()
    return render_template("2.html",currencies=data)

if __name__ == "__main__":
    app.run()