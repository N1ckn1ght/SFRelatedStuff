import datetime
import mysql.connector
import requests
import socket
import threading
import time
from config import config
from flask import Flask
from flask import request


db = mysql.connector.connect(
    host=config["db_host"],
    user=config["db_user"],
    password=config["db_password"],
    database=config["db_database"]
)
table = config["table"]

app = Flask(__name__)


@app.route("/")
def showHomePage():
    return "[ONLINE]"

@app.route("/get", methods=["POST"])
def sendData():
    result = getResult(request)
    if (result is None):
        return "error"
    if (len(result) < 1):
        return "error"
    return "{}\t{}\t{}\t{}".format(
        result[0][3],
        result[0][4],
        result[0][5],
        int(result[0][6].strftime("%Y%m%d%H%M%S"))
    )

@app.route("/set", methods=["POST"])
def getData():
    result = getResult(request)
    if (result is None):
        return "error"
    if (len(result) < 1):
        return "error"
    if "dispense" in request.form:
        dist = threading.Thread(target = dispense, args=(result[0][0], result[0][1], result[0][2], result[0][3], result[0][4]), daemon = True).start()
    if "rate" in request.form:
        try:
            rate = int(request.form["rate"])
            cursor_local = db.cursor()
            cursor_local.execute("UPDATE `{}` SET `rate` = '{}' WHERE `id` = '{}'".format(table, request.form["rate"], result[0][0]))
            db.commit()
        except ValueError:
            pass
    return ""
            

def getResult(request):
    if "id" in request.form:
        id = request.form["id"]
        print("Got request about:", id)
        
        cursor_local = db.cursor()
        cursor_local.execute("SELECT * FROM `{}` WHERE `id`='{}'".format(table, id))
        result = cursor_local.fetchall()
        
        w = float(requests.get("http://" + result[0][1] + "/recv").content)
        cursor_local.execute("UPDATE `{}` SET `plate` = {} WHERE `id` = '{}'".format(table, w, id))
        db.commit()
        
        cursor_local.execute("SELECT * FROM `{}` WHERE `id`='{}'".format(table, id))
        result = cursor_local.fetchall()
        return result
    else:
        # this will drop the application
        return None

def isTime(dt, rate):
    if (rate > 0):
        now = datetime.datetime.now()
        diff = int((now - dt).total_seconds() / 60)
        if (diff >= rate):
            return True
    return False

def dispense(id, ipw, ipd, stock, plate):
    # TODO: make calculations based on plate weight
    params = {
        'angle': 75,
        'interval': 3
    }
    r = requests.post("http://" + ipd + "/dispense", json=params)
    if (r.status_code == 200):
        cursor_local = db.cursor()
        cursor_local.execute("UPDATE `{}` SET `last` = CURRENT_TIMESTAMP WHERE `id` = '{}'".format(table, id))
        db.commit()
        time.sleep(5)
        w2 = float(requests.get("http://" + ipw + "/recv").content)
        # this should be done another way, but
        d = stock + plate - w2
        cursor_local.execute("UPDATE `{}` SET `stock` = {} WHERE `id` = '{}'".format(table, d, id))
        db.commit()

def loop():
    cursor_local = db.cursor()
    while True:
        try:
            cursor_local.execute("SELECT * from `{}`".format(table))
            result = cursor_local.fetchall()
            for (id, ipw, ipd, stock, plate, rate, last) in result:
                # TODO: calculate plate threshold (! moved to dispense function)
                if (isTime(last, rate)):
                    dispense(id, ipw, ipd, stock, plate)
            time.sleep(10)
        except mysql.connector.Error as err:
            break
            

if __name__ == "__main__":
    loop = threading.Thread(target = loop, daemon = True).start()
    app.run(host=config["app_host"])
