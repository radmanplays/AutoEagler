import os
import requests
import shutil
import time
import threading
import subprocess
import psutil   

# URLs and file locations
latest_bungee = "https://api.papermc.io/v2/projects/waterfall/versions/1.20/builds/550/downloads/waterfall-1.20-550.jar"
bungee_location = "Bungee/BungeeCord.jar"
latest_eaglerx = "https://github.com/lax1dude/eagl3rxbungee-memory-leak-patch/raw/main/EaglerXBungee-Memleak-Fixed.jar"
eaglerx_location = "./Bungee/plugins/eaglerXbungee.jar"
latest_guard = "https://ci.lucko.me/job/BungeeGuard/lastSuccessfulBuild/artifact/bungeeguard-universal/target/BungeeGuard.jar"
guard_location = "./Bungee/plugins/BungeeGuard.jar"
latest_protocol = "https://ci.dmulloy2.net/job/ProtocolLib/lastStableBuild/artifact/build/libs/ProtocolLib.jar"
protocol_location = "./Server/plugins/ProtocolLib.jar"
latest_spigot = "https://cdn.getbukkit.org/spigot/spigot-1.8.8-R0.1-SNAPSHOT-latest.jar"
spigot_location = "Server\Spigot.jar"

def download_file(url, location):
    response = requests.get(url)
    with open(location, 'wb') as file:
        file.write(response.content)

def replace_in_file(file_path, search, replace):
    with open(file_path, 'r') as file:
        file_data = file.read()
    file_data = file_data.replace(search, replace)
    with open(file_path, 'w') as file:
        file.write(file_data)

def remove_everything():
    shutil.rmtree("./Bungee", ignore_errors=True)
    shutil.rmtree("./Server", ignore_errors=True)
    if os.path.exists(bungee_location):
        os.remove(bungee_location)
    if os.path.exists(eaglerx_location):
        os.remove(eaglerx_location)
    if os.path.exists(guard_location):
        os.remove(guard_location)
    if os.path.exists(spigot_location):
        os.remove(spigot_location)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_command_in_new_terminal(command):
    if os.name == 'nt':
        subprocess.Popen(['start', 'cmd', '/c', command], shell=True)
    else:
        subprocess.Popen(['x-terminal-emulator', '-e', command])

def run_servers():
    print(f"Running BungeeCord from: {bungee_location}")

    # Change directory to the location of BungeeCord.jar
    os.chdir(os.path.dirname(bungee_location))
    run_command_in_new_terminal(f'java -Xms64M -Xmx64M -jar {os.path.basename(bungee_location)}')
    os.chdir(os.path.dirname("../"))

    # Change directory to the location of Spigot.jar
    os.chdir(os.path.dirname(spigot_location))
    run_command_in_new_terminal(f'java -Xms2G -Xmx2G -jar {os.path.basename(spigot_location)}')
    os.chdir(os.path.dirname("../"))

def stop_servers():
    print("Stopping servers...")
    
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = process.info.get('cmdline')
            if cmdline and 'java' in cmdline and any(jar_name in cmdline for jar_name in ['BungeeCord.jar', 'Spigot.jar']):
                print(f"Terminating process {process.info['pid']} ({' '.join(cmdline)})")
                process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    print("Servers stopped.")

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("1) Set up AutoEagler")
        print("2) Run AutoEagler")
        print("3) Add plugins")
        print("4) Wipe everything")
        print("5) Exit")

        choice = input(">> ")

        if choice == '1':
            if not os.path.exists(bungee_location):
                os.makedirs(os.path.dirname(bungee_location), exist_ok=True)
                download_file(latest_bungee, bungee_location)
                print(f"BungeeCord.jar downloaded to {bungee_location}")

            if not os.path.exists(eaglerx_location):
                os.makedirs(os.path.dirname(eaglerx_location), exist_ok=True)
                download_file(latest_eaglerx, eaglerx_location)
                print(f"eaglerxbungee.jar downloaded to {eaglerx_location}")

            if not os.path.exists(guard_location):
                os.makedirs(os.path.dirname(guard_location), exist_ok=True)
                download_file(latest_guard, guard_location)
                print(f"BungeeGuard.jar downloaded to {guard_location}")
            
            if not os.path.exists("./Server/plugins/BungeeGuard.jar"):
                os.makedirs(os.path.dirname("./Server/plugins/BungeeGuard.jar"), exist_ok=True)
                download_file(latest_guard, "./Server/plugins/BungeeGuard.jar")
                print(f"BungeeGuard.jar downloaded to ./Server/plugins/BungeeGuard.jar")

            if not os.path.exists(protocol_location):
                os.makedirs(os.path.dirname(protocol_location), exist_ok=True)
                download_file(latest_protocol, protocol_location)
                print(f"ProtocolLib.jar downloaded to {protocol_location}")

            if not os.path.exists(spigot_location):
                os.makedirs(os.path.dirname(spigot_location), exist_ok=True)
                download_file(latest_spigot, spigot_location)
                print(f"Spigot.jar downloaded to {spigot_location}")

            run_servers()  # Run the servers after downloading
            time.sleep(15)
            stop_servers()
            replace_in_file("Server/eula.txt", "false", "true")  # Example: Change eula to true
            run_servers()
            time.sleep(15)
            stop_servers()

            # Replace content in configuration files
            replace_in_file("Server/server.properties", "online-mode=true", "online-mode=false")
            replace_in_file("Server/spigot.yml", "bungeecord: false", "bungeecord: true")
            replace_in_file("Bungee/plugins/EaglercraftXBungee/authservice.yml", "enable_authentication_system: true", "enable_authentication_system: false")

            with open("Bungee/plugins/BungeeGuard/token.yml", 'r') as file:
                token = file.read()
                split_result = token.split(': ', 1)
                token = split_result[1]
                token = token.replace('\n', '')

            replace_in_file("Server/plugins/BungeeGuard/config.yml", "the token generated by the proxy goes here", token)  # Example: Replace token
            replace_in_file("Bungee/config.yml", "online_mode: true", "online_mode: false")

        elif choice == '2':
            run_servers()

        elif choice == '3':
            pass  # Add plugins logic here

        elif choice == '4':
            remove_everything()
            print("Everything has been removed.")

        elif choice == '5':
            stop_servers()
            break

if __name__ == "__main__":
    main()