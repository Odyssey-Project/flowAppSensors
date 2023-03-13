"""Apalis iMX8 Device Info class"""

#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

import os.path as pcheck
import subprocess
import json
import psutil


__author__ = 'Matheus Castello'
__version__ = '0.1'
__license__ = 'MIT'
__copyright__ = 'Copyright 2019 Toradex AG'

#
# I try to make this more generic but the thermal zones depends on device tree
# descriptions, so this deviceInfo will be util only for the
# NXP® i.MX 8QuadMax (i.MX 8QM), 2x Arm® Cortex-A72, 4x Cortex-A53, 2x Cortex-M4
#


# pylint: disable=too-many-instance-attributes
class DeviceInfo:
    """Device Info class"""

    def __init__(self):
        self.__cpu_a53_temperature = 0.0
        self.__cpu_a72_temperature = 0.0
        self.__gpu0_temperature = 0.0
        self.__gpu1_temperature = 0.0

        self.__serial_number = "00000000"
        self.__product_id = "0"
        self.__product_revision = "0"

        # Initial checks

        # /proc/device-tree symlinks to /sys/firmware/devicetree/base
        # self.DTDIR = '/proc/device-tree'
        self.dt_dir = '/sys/firmware/devicetree/base/'

        self.dtdir_exist = pcheck.isdir(self.dt_dir)

    def __bash_command(self, cmd):
        """Execute a bash command and return the output"""

        # pylint: disable=consider-using-with
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            # pylint: disable=broad-exception-raised
            raise Exception(error)
        return output

    def __get_celsius_from_thermal_zone(self, index):
        """Get temperature from thermal zone"""

        # get from thermal zone
        # pylint: disable=consider-using-with
        _f = open("/sys/class/thermal/thermal_zone" + str(index) + "/temp", "r", encoding="utf-8")
        temp = int(_f.read())
        # kernel int to float
        return float(temp) / 1000.0

    def get_cpu_cores_count(self):
        """Get CPU cores count"""

        # check how many cpus we have
        cpu_json = self.__bash_command("lscpu -J")
        lscpu = json.loads(cpu_json)
        # get cpu cores and threads per core
        for i in range(0, len(lscpu["lscpu"])):
            if lscpu["lscpu"][i]["field"] == "CPU(s):":
                cores = int(lscpu["lscpu"][i]["data"])
            if lscpu["lscpu"][i]["field"] == "Thread(s) per core:":
                threads = int(lscpu["lscpu"][i]["data"])
        return int(cores / threads)

    def get_temperature_cpu_a53(self):
        """Get CPU A53 temperature"""

        # get from thermal zone
        self.__cpu_a53_temperature = self.__get_celsius_from_thermal_zone(0)
        return self.__cpu_a53_temperature

    def get_temperature_cpu_a72(self):
        """Get CPU A72 temperature"""

        # get from thermal zone
        self.__cpu_a72_temperature = self.__get_celsius_from_thermal_zone(1)
        return self.__cpu_a72_temperature

    def get_temperature_gpu0(self):
        """Get GPU 0 temperature"""

        # get from thermal zone
        self.__gpu0_temperature = self.__get_celsius_from_thermal_zone(2)
        return self.__gpu0_temperature

    def get_temperature_gpu1(self):
        """Get GPU 1 temperature"""

        # get from thermal zone
        self.__gpu1_temperature = self.__get_celsius_from_thermal_zone(3)
        return self.__gpu1_temperature

    def get_cpu_usage(self):
        """Get CPU usage"""

        return psutil.cpu_percent()

    def get_cpu_usage_detailed(self):
        """Get CPU usage detailed"""

        return psutil.cpu_percent(percpu=True)

    def get_ram_usage(self):
        """Get RAM usage in percentage"""

        return psutil.virtual_memory().percent

    def get_ram_total(self):
        """Get RAM total"""

        return round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 4)

    def get_ram_free(self):
        """Get RAM free"""

        return round(psutil.virtual_memory().free / 1024 / 1024 / 1024, 4)

    def get_gpu_memory_usage(self):
        """Get GPU memory usage"""

        stuff = self.__bash_command("cat /sys/kernel/debug/gc/meminfo")
        print(stuff.split())
        slices = stuff.split()
        used = int(slices[9])
        slices = stuff.split()
        free = int(slices[21])
        return (used * 100) / free

    def get_tdx_serial_number(self):
        """Get Toradex serial number"""

        if self.dtdir_exist:
            with open(self.dt_dir + '/serial-number', 'r', encoding="ascii") as _f:
                self.__serial_number = _f.read().rstrip('\x00')
        return int(self.__serial_number)

    def get_tdx_product_id(self):
        """Get Toradex product ID"""

        if self.dtdir_exist:
            # Get SKU and module version
            with open(self.dt_dir + '/toradex,product-id', 'r', encoding='ascii') as _f:
                self.__product_id = _f.read().rstrip('\x00')
            try:  # try to decode a number to an actual human readable info
                self.__product_id = self._module_info_decode(
                    int(self.__product_id))
            except AttributeError:
                pass  # just provide 'undefined'
        return self.__product_id

    def get_tdx_product_revision(self):
        """Get Toradex product revision"""

        if self.dtdir_exist:
            with open(self.dt_dir + '/toradex,board-rev', 'r', encoding='ascii') as _f:
                self.__product_revision = _f.read().rstrip('\x00')
        return self.__product_revision
