import network
import urequests

def load_wifi_credentials():
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


def connect_to_wifi():
    # Wi-fi credentials
    wifi_credentials = load_wifi_credentials()
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
    

def post_to_httpbin():
    url = "https://httpbin.org/post"
    data = {
        "temperature": 25.0,
        "humidity": 50.0
    }

    response = urequests.post(url, json=data)
    print("Respuesta de httpbin.org:")
    print(response.text)
    response.close()
    
def disconnect_wifi(wlan):
    wlan.disconnect()
    wlan.active(False)
    print("Wi-Fi disconnected")


wlan = connect_to_wifi()
post_to_httpbin()
disconnect_wifi(wlan)


