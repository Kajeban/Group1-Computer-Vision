import paho.mqtt.publish as publish

# server_ip = "172.20.10.4"
# server_ip = "192.168.7.237"
server_ip = "172.20.10.5"

topic = "GateNegotiation"

message = "Hello World"

try:
    publish.single(topic, message, hostname=server_ip)
    print("Success")
except Exception as e:
    print("Error:", e)
