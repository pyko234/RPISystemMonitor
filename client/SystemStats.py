import wmi
import os
import re
import psutil
import time
import subprocess
import threading
from pathlib import Path


fps = 0
fps_thread = None
fps_thread_stop = threading.Event()
fps_lock = threading.Lock()
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
    global fps, fps_thread, fps_thread_stop, current_game_exe
    global games, game_thread_started, apps_path

    if not game_thread_started:
        threading.Thread(target=watch_manifests, args=(apps_path,), daemon=True).start()
        game_thread_started = True

    sys_wmi = wmi.WMI()
    ohm_wmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")

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

    game_name, game_exe = game

    if game_exe:
        # Start FPS thread if not running
        if not fps_thread or not fps_thread.is_alive():
            #print(f"[Main] Starting FPS thread for: {game_exe}")
            fps_thread_stop.clear()
            fps_thread = threading.Thread(target=get_fps, args=(game_exe, fps_thread_stop), daemon=True)
            fps_thread.start()

    else:
        # No game running, stop thread if it exists
        if fps_thread and fps_thread.is_alive():
            #print("[Main] Stopping FPS thread — no game running.")
            fps_thread_stop.set()
            fps_thread.join()

    with fps_lock:
        current_fps = fps 

    return {
        'cpu_usage': f"{cpu_usage:.1f}",
        'cpu_temp': f"{cpu_temp:.1f}",
        'gpu_usage': f"{gpu_usage:.1f}",
        'gpu_temp': f"{gpu_temp:.1f}",
        'game': game_name,
        'time': time.strftime("%I:%M %p", time.localtime()),
        'fps': f"{current_fps:.0f}"
    }

def get_fps(exe, stop_event):
    global fps, fps_lock

    def is_running():
        for p in psutil.process_iter(['name']):
            if p.info['name'] and p.info['name'].lower() == exe.lower():
                return True
        return False

    creation_flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'STARTUPINFO') else 0

    proc = subprocess.Popen(
        [
            "PresentMon-2.3.1-x64.exe",
            "-output_stdout",
            "-stop_existing_session",
            "-process_name", exe
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        creationflags=creation_flags
    )

    try:
        while not stop_event.is_set():
            line = proc.stdout.readline()
            if not line:
                break
            if proc.poll() is not None or not is_running():
                break

            try:
                ms_between_presents = float(line.strip().split(',')[11])
                with fps_lock:
                    fps = 1000.0 / ms_between_presents
                time.sleep(1)
            except (IndexError, ValueError):
                continue
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        with fps_lock:
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
