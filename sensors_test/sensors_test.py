from machine import Pin
import utime  as time
from dht import DHT11

inletPin = Pin(16, Pin.OUT, Pin.PULL_DOWN)
inletSensor = DHT11(inletPin)

outletPin = Pin(17, Pin.OUT, Pin.PULL_DOWN)
outletSensor = DHT11(outletPin)

while True:
    inletSensor.measure()
    outletSensor.measure()
    
    inletTemp = inletSensor.temperature()
    inletHum = inletSensor.humidity()
    
    outletTemp = outletSensor.temperature()
    outletHum = outletSensor.humidity()
    
    print(inletTemp, inletHum)
    print(outletTemp, outletHum)
    
    time.sleep(1)