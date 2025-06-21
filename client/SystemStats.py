import wmi
import os
import re
import psutil
import time
import subprocess
import threading
from pathlib import Path


fps = 0
fps_thread_started = False
games = {}
game_thread_started = False
apps_path = "E:\\SteamLibrary\\steamapps"
install_path = "E:\\SteamLibrary\\steamapps\\common"

def watch_manifests(manifest_dir):
    global games
    previous_manifests = set(os.listdir(manifest_dir))
    while True:
        time.sleep(10)
        current_manifests = set(os.listdir(manifest_dir))
        created = current_manifests - previous_manifests
        removed = previous_manifests - current_manifests
        if created or removed or games == {}:
            get_games()
            previous_manifests = current_manifests

def get_stats():
    global fps, fps_thread_started, games, game_thread_started
    global apps_path

    if not game_thread_started:
        threading.Thread(target=watch_manifests, args=(apps_path,), daemon=True).start()
        game_thread_started = True

    # Connect to standard WMI namespace (for RAM speed)
    sys_wmi = wmi.WMI()

    # Connect to OpenHardwareMonitor namespace (for sensor data)
    ohm_wmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")

    # GPU sensor values from OpenHardwareMonitor
    for sensor in ohm_wmi.Sensor():
        if sensor.Name == "GPU Core" and sensor.SensorType == "Load":
            gpu_usage = sensor.value
        elif sensor.Name == "GPU Core" and sensor.SensorType == "Temperature":
            gpu_temp = sensor.value
        elif sensor.Name == "CPU Package":
            cpu_temp = sensor.value
        elif sensor.Name == "CPU Total":
            cpu_usage = sensor.value
    
    game = get_running_game()
    
    if not game:
        game = ("Chillin'", None)
    else:
        if not fps_thread_started:
            fps_thread_started = True
            threading.Thread(target=get_fps, args=(game[1],), daemon=True).start()

    return {
        'cpuUsage': f"{cpu_usage:.1f}",
        'cpuTemp': f"{cpu_temp:.1f}",
        'gpuUsage': f"{gpu_usage:.1f}",
        'gpuTemp': f"{gpu_temp:.1f}",
        'game': game[0],
        'time': time.strftime("%I:%M %p", time.localtime()),
        'fps': f"{fps:.0f}"
    }

def get_fps(exe):
    global fps, fps_thread_started

    def is_running():
        for p in psutil.process_iter(['name']):
            if p.info['name'] and p.info['name'].lower() == exe.lower():
                return True
        return False
    
    creation_flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'STARTUPINFO') else 0

    proc = subprocess.Popen(
        ["PresentMon-2.3.1-x64.exe", "-no_csv", "-output_stdout", "-stop_existing_session", "-process_name", exe],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        creationflags=creation_flags
    )

    try:
        for line in proc.stdout:
            print(line)
            try:
                if not is_running():
                    break
                ms_between_presents= float(line.strip().split(',')[11])
                fps = 1000.0 / ms_between_presents
            except IndexError:
                pass
            except ValueError:
                pass   
            except Exception as e:
                print(f"Unknown Error: {e}")
    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()
        fps_thread_started = False
        fps = 0

def find_all_exes(directory):
    exe_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.exe'):
                exe_paths.append(os.path.normcase(os.path.join(root, file)))
    return exe_paths

def get_steam_games_from_manifests(manifest_dir):
    games = {}
    acf_pattern = re.compile(r'appmanifest_(\d+)\.acf')

    for filename in os.listdir(manifest_dir):
        match = acf_pattern.match(filename)
        if not match:
            continue

        appid = match.group(1)
        filepath = os.path.join(manifest_dir, filename)

        installdir = None
        game_name = None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line.startswith('"name"') and game_name is None:
                    parts = line.split('"')
                    if len(parts) >= 4:
                        game_name = parts[3]

                elif line.startswith('"installdir"') and installdir is None:
                    parts = line.split('"')
                    if len(parts) >= 4:
                        installdir = parts[3]

                if game_name and installdir:
                    break

            if game_name and installdir:
                games[appid] = {
                    "name": game_name,
                    "installdir": installdir
                }

        except Exception as e:
            print(f"Failed to read {filepath}: {e}")

    return games

def get_games():
    global games, apps_path, install_path
    games = get_steam_games_from_manifests(apps_path)
    for x in games.keys():
        path = Path(install_path + "\\" + games[x]['installdir'])
        games[x]["exe"] = find_all_exes(path)
      
def get_running_game():
    global games
    exe_to_game = {}

    # Build map: normalized exe full path -> (game_name, exe_filename)
    for game in games.values():
        for exe_full_path in game.get('exe', []):
            exe_filename = os.path.basename(exe_full_path)
            exe_to_game[os.path.normcase(exe_full_path)] = (game['name'], exe_filename)

    for proc in psutil.process_iter(['exe']):
        try:
            path = proc.info['exe']
            if path:
                norm_path = os.path.normcase(path)
                if norm_path in exe_to_game:
                    return exe_to_game[norm_path]  # returns (game_name, exe_filename)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return None

if __name__ == "__main__":
    while True:
        print(get_stats())
        time.sleep(5)
