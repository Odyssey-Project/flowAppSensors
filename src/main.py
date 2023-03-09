#!python3
"""Main module. Flask server"""

#
# Copyright 2023 Toradex AG. or its affiliates. All Rights Reserved.
#

from threading import Thread
import time

# flask
from flask import Flask
from flask import jsonify
from flask_restful import Api
from flask_cors import CORS, cross_origin
from device_info import DeviceInfo

# global sensor
device_info = DeviceInfo()
# flask route
app = Flask(__name__)
# add cors
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)

# the API will be used by the GUI to get the data
@app.route('/')
@cross_origin()
def index():
    """Root route"""

    # pylint: disable=line-too-long
    return "<img src='http://www.quickmeme.com/img/e7/e7ce51fa8f392143a6af3159be424b340279fd89b57ee74b77ac919562c64a99.jpg'></img>"

def sensor_monitor():
    """Sensor monitor thread"""

    while True:
        # get data
        _t = device_info.get_temperature_cpu_a53()
        _r = device_info.get_ram_usage()
        _c = device_info.get_cpu_usage()

        # save data in a file
        with open("/none/data.txt", "a", encoding="utf-8") as _f:
            _f.write(str(_t) + "," + str(_r) + "," + str(_c) + "\n")

        time.sleep(10)

if __name__ == '__main__':
    # monitoring thread
    thread = Thread(target=sensor_monitor)
    thread.start()

    print("Flask working well")
    app.run(host='0.0.0.0', port='8080')
else:
    print(__name__)
    print("Flask not working")
