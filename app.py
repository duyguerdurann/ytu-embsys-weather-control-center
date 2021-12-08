from flask import Flask,request,render_template
app = Flask(__name__)

#
#   SOCKET IO IMPLEMENTATION
#
from flask_socketio import SocketIO,send,emit
socketio = SocketIO(app)


import datetime as dt
import sqlite3 as sqlite3
import os


class EntrySqlite():

    dbpath = os.path.join(os.path.dirname(__file__), "data", "database.sq3")    
    def __init__(self):
        conn = sqlite3.connect(self.dbpath)
        conn.execute('CREATE TABLE IF NOT EXISTS entries ( lux integer, air integer, temp integer, humidity integer, water_level integer, water_temp integer, model_result integer, created_at text )')
        print("Table created successfully")
        pass
    
    def save(self,lux,air,temp,humidity,water_level,water_temp,model_result):
        isOk = False
        try:
            with sqlite3.connect(self.dbpath) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO entries (lux,air,temp,humidity, water_level,water_temp,model_result,created_at) VALUES (?,?,?,?,?,?,?,?)",(lux,air,temp, humidity, water_level,water_temp, model_result,dt.datetime.now()) )
                con.commit()
                isOk = True
                pass
        except:
            con.rollback()
            pass
        finally:
            con.close()
            pass
        return isOk     
    
    def all(self):
        con = sqlite3.connect(self.dbpath)
        con.row_factory = sqlite3.Row
        
        cur = con.cursor()
        cur.execute("select * from entries;")
        rows = cur.fetchall()
        
        con.close()
        return rows
    pass

database = EntrySqlite()


@app.route('/')
def hello():
    air_quality = int(request.args.get('air',0))
    temperature = int(request.args.get('temp',0))
    lux = int(request.args.get('lux',0))
    humidity = int(request.args.get('humidity',0))
    water_level = int(request.args.get('wlevel',0))
    water_temp = int(request.args.get('wtemp',0))
    
    isOk = database.save(lux,air_quality,temperature,humidity,water_level,water_temp,0)
    
    if(isOk):
        print("Kaydedildi")
        pass
    else:
        print("Hata meydana geldi.")
        pass

    if(air_quality == 0 and temperature == 0 and lux == 0):
        return "No sensor value ensured"
    return str(0)


# http://localhost:5000/new?air=10&temp=10&lux=10&wtemp=20&wlevel=10&humidity=20
@app.route('/db')
def get_db_all():
    allEntries = database.all()    
    return render_template("db.html",rows = allEntries, msg = "Sisteme kayıtlı girdi(entry) kayıtlarını getirdi.")



@app.route('/all')
def get_all():
    allEntries = database.all()    
    return render_template("index.html",rows = allEntries, msg = "Sisteme kayıtlı girdi(entry) kayıtlarını getirdi.")


# http://localhost:5000/new?air=10&temp=10&lux=10&wtemp=20&wlevel=10&humidity=20
@app.route('/new')
def set_new():
    air_quality = int(request.args.get('air',0))
    temperature = int(request.args.get('temp',0))
    lux = int(request.args.get('lux',0))
    humidity = int(request.args.get('humidity',0))
    water_level = int(request.args.get('wlevel',0))
    water_temp = int(request.args.get('wtemp',0))

    if(air_quality == 0 and lux == 0 and temperature == 0):
        return "No value ensured"
    
    new_values = {
        "air" : air_quality,
        "lux" : lux,
        "temp" : temperature,
        "humidity" : humidity,
        "wlevel" : water_level,
        "wtemp" : water_temp,
        "result" : 0
    }

    # send sensor values to dashboard
    try:
        socketio.emit('new-values', new_values)
    except:
        print("Sensor values could not send to admin dashboard")
        pass
    # save entries to database
    try:
        database.save(lux,air_quality,temperature,humidity,water_level,water_temp,int(result[0]))
        print("Kaydedildi")
        pass
    except:
        print("Hata meydana geldi.")
        pass
    return "0"



APP_BIND= os.getenv('APP_BIND', '0.0.0.0')
APP_PORT= os.getenv('APP_PORT', '5000')

# flask main function
if __name__ == '__main__':
    print("App initiliazing...")
    # run from dotenv
    app.run(app,host=APP_BIND,port=APP_PORT)
    print("App Server Port: " + APP_PORT)
    socketio.run(app)
    print("Socket Server Port: " + APP_PORT)
    print("App Initialization Finished")
    pass
