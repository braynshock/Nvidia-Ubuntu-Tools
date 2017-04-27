#!/usr/bin/env python3
import subprocess
import time
import math

# config file items
# TODO move these values to config file in /etc

# min speed for the fan (some cards factory = 0)
minFanSpeed = 15
# max speed of fan you want to use
maxFanSpeed = 100
# temp that fan starts to ramp up from minimum
minGpuTemp = 50
# temp where fan = maxFanSpeed
maxGpuTemp = 80
# curveStyle = 0 is linear, curveStyle = 1 is exponential
curveStyle = 0
# Polling offset in seconds (anything longer than 10 seconds could be bad)
pollOffset = 1

# create curve hashmap
curve = {}
deltaSpeed = maxFanSpeed - minFanSpeed
deltaTemp = maxGpuTemp - minGpuTemp
if curveStyle == 0:
    multiplier = deltaSpeed/deltaTemp
    for i in range(1, deltaTemp):
        curve[i + minGpuTemp] = math.floor(i * multiplier) + minFanSpeed
else:
    dividend = (deltaTemp*deltaTemp)/deltaSpeed
    for i in range(1, deltaTemp):
        curve[i + minGpuTemp] = math.ceil((i * i) / dividend) + minFanSpeed

# Print Curve
# print("Custom Fan Curve")
# print("0 - %d " % minGpuTemp, "%d" % minFanSpeed)
# for i in range(minGpuTemp+1, maxGpuTemp):
#     print(i, curve[i])
# print("%d - up " % maxGpuTemp, "%d" % maxFanSpeed)

# Error detection variable
err = ""

# get GPU identities (currently for one GPU)
# TODO - multi-GPU support
gpuGet = subprocess.Popen(["nvidia-smi", "-L"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
gpu = int(gpuGet[0].decode('ascii')[4:5])
err = err + gpuGet[1].decode('ascii')
print("FanControl Service started for [gpu:%s]" % gpu)

# Enable manual fan control
manualFanSet = subprocess.Popen(["nvidia-settings", "-a", "[gpu:%d]/GPUFanControlState=1" % gpu],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
err = err + manualFanSet[1].decode('ascii')

# service setup
while err == "":
    # get current temp of GPU
    # TODO multi-fan support
    getTemp = subprocess.Popen(["nvidia-settings", "-t", "-q", "[gpu:%s]/GPUCoreTemp" % gpu],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    temp = int(getTemp[0].decode('ascii'))
    err = err + getTemp[1].decode('ascii')
    # print("temp = %d" % temp)

    # get setting for fan speed from temp || curve hashmap
    speed = minFanSpeed
    if temp <= minGpuTemp:
        speed = minFanSpeed
    else:
        if temp >= maxGpuTemp:
            speed = maxFanSpeed
        else:
            speed = curve[temp]

    # set GPU Fan Speed
    setSpeed = subprocess.Popen(["nvidia-settings", "-a", "[fan:0]/GPUTargetFanSpeed=%d" % speed],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    out = setSpeed[0].decode('ascii')
    err = err + setSpeed[1].decode('ascii')

    # print("output: ", out, "speed = %d" % speed)

    # wait 1 second before polling again
    time.sleep(pollOffset)

print("Error code stopped GPU-FanControl service\n", err)
