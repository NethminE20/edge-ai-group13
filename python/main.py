import subprocess

p1 = subprocess.Popen(["python", "mqtt_publisher.py"])
p2 = subprocess.Popen(["python", "edge_ai.py"])

p1.wait()
p2.wait()