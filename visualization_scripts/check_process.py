"""
assert Cytoscape is running on machine

"""
#assert Cytoscape is running on machine
import subprocess
import time

def process_exists(process_name):
    bytes_name = str.encode(process_name)
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call)
    # check in last line for process name
    last_line = output.strip().split(b'\r\n')[-1]
    return last_line.lower().startswith(bytes_name.lower())

print("sleep program execution")
print("waiting for Cytoscape to load")
#time.sleep(45)
print("sleep over")

# check Cytoscape
isRunning = process_exists('Cytoscape.exe')
if (isRunning == False):
    print("Cytoscape not running")
else:
    print("Cytoscape running")