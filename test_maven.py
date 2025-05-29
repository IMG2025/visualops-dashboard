from maven import start_maven

start_maven()

# Keep the script alive so threads can run
import time
while True:
    time.sleep(60)
