#!python3
"""Main module. Flask server"""

#
# Copyright 2023 Toradex AG. or its affiliates. All Rights Reserved.
#

from threading import Thread
import time
import sys

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

@app.route('/sensors/last')
@cross_origin()
def sensors_data_last():
    """Sensors data route"""

    data = []

    with open("/media/SENSORS/last", "r", encoding="utf-8") as _f:
        for _line in _f:
            _data = _line.split(",")
            _temperature = _data[0]
            _ram = _data[1]
            _cpu = _data[2]

            data.append({
                "temperature": _temperature,
                "ram": _ram,
                "cpu": _cpu
            })

    return jsonify(data)

@app.route('/sensors/data')
@cross_origin()
def sensors_data():
    """Sensors data route"""

    data = []

    with open("/media/SENSORS/data", "r", encoding="utf-8") as _f:
        for _line in _f:
            _data = _line.split(",")
            _temperature = _data[0]
            _ram = _data[1]
            _cpu = _data[2]

            data.append({
                "temperature": _temperature,
                "ram": _ram,
                "cpu": _cpu
            })

    return jsonify(data)

def sensor_monitor():
    """Sensor monitor thread"""

    while True:
        # get data
        _t = device_info.get_temperature_cpu_a53()
        _r = device_info.get_ram_usage()
        _c = device_info.get_cpu_usage()

        try:
            # WARNING: THE USB STICK MUST BE MOUNTED IN /media/SENSORS
            # write the last read in a file
            with open("/media/SENSORS/last", "w", encoding="utf-8") as _f:
                _f.write(str(_t) + "," + str(_r) + "," + str(_c) + "\n")

            # append data in a file
            with open("/media/SENSORS/data", "a", encoding="utf-8") as _f:
                _f.write(str(_t) + "," + str(_r) + "," + str(_c) + "\n")
        # pylint: disable=broad-exception-caught
        except Exception as _e:
            print(_e, file=sys.stderr)

        time.sleep(2)

if __name__ == '__main__':
    # monitoring thread
    thread = Thread(target=sensor_monitor)
    thread.start()

    print("Flask working well")
    app.run(host='0.0.0.0', port='8080')
else:
    print(__name__)
    print("Flask not working")
