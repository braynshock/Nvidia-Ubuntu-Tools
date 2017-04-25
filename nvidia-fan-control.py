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
maxGpuTemp = 85
# curveStyle = 0 is linear, curveStyle = 1 is exponential
curveStyle = 0

# create curve
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
print("Custom Fan Curve")
print("0 - %d " % minGpuTemp, "%d" % minFanSpeed)
for i in range(minGpuTemp, maxGpuTemp):
    print(i, curve[i])
print("%d - up " % maxGpuTemp, "%d" % maxFanSpeed)


# get GPU identities (currently for one GPU)
# TODO - multi-GPU support
gpu = subprocess.Popen(["nvidia-smi","-L"], stdout=subprocess.PIPE).communicate()[0].decode('ascii')[4:5]
print("FanControl Service started for [gpu:%s]" % gpu)

# service setup
err = ""
while err == "":
    # get current temp of GPU
    # TODO multi-fan support
    getTemp = subprocess.Popen(["nvidia-settings", "-t", "-q", "[gpu:%s]/GPUCoreTemp" % gpu],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    temp = int(getTemp[0].decode('ascii'))
    err = getTemp[1].decode('ascii')
    # print("temp = %d" % temp)

    # calculate fan speed
    speed = minFanSpeed
    if temp <= minGpuTemp:
        speed = minFanSpeed
    else:
        if temp >= maxGpuTemp:
            speed = maxFanSpeed
        else:
            speed = curve[temp]

    # set GPU Fan Speed
    setSpeed = subprocess.Popen(["nvidia-settings","-a","[fan:0]/GPUTargetFanSpeed=%d" % speed],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    out = setSpeed[0].decode('ascii')
    err = setSpeed[1].decode('ascii')

    # print("output: ", out, "speed = %d" % speed)

    # wait 1 second before polling again
    time.sleep(1)

print("Error code stopped GPU-FanControl service\n", err)