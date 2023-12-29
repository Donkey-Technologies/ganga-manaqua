import network
import urequests
import ujson
from machine import Pin
import utime  as time
from dht import DHT11


def get_wifi_credentials():
    credentials = {}
    try:
        with open('wifi_config.txt', 'r') as f:
            for line in f:
                if ":" in line:
                    key, value = line.strip().split(':', 1)
                    credentials[key] = value
    except OSError:
        print("Unable to extract config info")
    return credentials


def get_aws_url():
    try:
         with open('aws_url.txt', 'r') as f:
            for line in f:
                if ":" in line:
                    _, value = line.strip().split(':', 1)
                    return value
    except OSError:
        print("Unable to extract URL")
        return ""


def connect_to_wifi():
    # Wi-fi credentials
    wifi_credentials = get_wifi_credentials()
    ssid = wifi_credentials.get("SSID")
    password = wifi_credentials.get("PASSWORD")
    
    print(ssid)
    print(password)

    # Connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait until response is valid
    print("Connecting to Wi-Fi")
    while not wlan.isconnected():
        pass

    print("Succesful Wi-Fi Connection")
    print(wlan.ifconfig())
    
    return wlan
    

def post_to_aws(url: str, data: dict):
    headers = {'Content-Type': 'application/json'}
    
    response = urequests.post(url, data=ujson.dumps(data), headers=headers)
    if response.status_code == 200:
        print("Datos enviados con éxito")
        error = False
    else:
        print(f"Error al enviar datos: {response.text}")
        error = True

    response.close()
    
    return error

    
def disconnect_wifi(wlan):
    wlan.disconnect()
    wlan.active(False)
    print("Wi-Fi disconnected")
    
    
def config_sensors():
    inlet_pin = Pin(16, Pin.OUT, Pin.PULL_DOWN)
    inlet_sensor = DHT11(inlet_pin)

    outlet_pin = Pin(17, Pin.OUT, Pin.PULL_DOWN)
    outlet_sensor = DHT11(outlet_pin)
    
    return inlet_sensor, outlet_sensor


def read_sensors(inlet_sensor, outlet_sensor):
    data = {}
    
    inlet_sensor.measure()
    outlet_sensor.measure()
    
    data["inlet_temp"] = inlet_sensor.temperature()
    data["inlet_hum"] = inlet_sensor.humidity()
    
    data["outlet_temp"] = outlet_sensor.temperature()
    data["outlet_hum"] = outlet_sensor.humidity()
    
    print(data)
    print("")
    
    return data


# Sensors configuration 
inlet_sensor, outlet_sensor = config_sensors()

# AWS connection
wlan = connect_to_wifi()
url = get_aws_url()

# Send data for the followin hour
counter = 0

while True:
    print("Measurement", counter)
    data = read_sensors(inlet_sensor, outlet_sensor)
    post_error = post_to_aws(url, data)
    counter += 1
    
    if counter >= 120 or post_error:
        break
    
    time.sleep(30)
    
disconnect_wifi(wlan)


