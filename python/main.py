import threading
import os

def run_publisher():
    os.system("python mqtt_publisher.py")

def run_ai():
    os.system("python edge_ai.py")

t1 = threading.Thread(target=run_publisher)
t2 = threading.Thread(target=run_ai)

t1.start()
t2.start()

t1.join()
t2.join()