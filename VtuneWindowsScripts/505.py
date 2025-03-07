import os
import subprocess
from pathlib import Path

# Configuration
FREQUENCIES = [2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600]
RUNS_PER_FREQ = 5
BASE_DIR = Path(r"C:\Users\roymo\Documents\ProcSimVal\RunResults")
REMOTE_USER = "cc"
REMOTE_HOST = "procsimval-chameleon"
VTUNE_PATH = r"C:\Program Files (x86)\Intel\oneAPI\vtune\2025.0\bin64\vtune"

def find_available_folder(base_path, prefix):
    count = 0
    while (base_path / f"{prefix}{count}").exists():
        count += 1
    return base_path / f"{prefix}{count}"

def ssh_command(command):
    """Execute remote command using SSH via subprocess"""
    try:
        result = subprocess.run(
            ["ssh", f"{REMOTE_USER}@{REMOTE_HOST}", command],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"SSH command failed: {e.stderr}")
        raise

def main():
    for freq in FREQUENCIES:
        prefix = f"505_{freq}_"
        
        # Set frequency once per frequency group
        try:
            ssh_command(f"~/bench_exe/scripts/set_freq_cache.sh {freq}")
        except subprocess.CalledProcessError:
            continue  # Skip this frequency if setup fails

        for run in range(RUNS_PER_FREQ):
            target_dir = find_available_folder(BASE_DIR, prefix)
            target_dir.mkdir(parents=True)
            
            print(f"Starting run {run+1}/{RUNS_PER_FREQ} at {freq}MHz")

            vtune_cmd = [
                VTUNE_PATH,
                "-target-system", f"ssh:{REMOTE_USER}@{REMOTE_HOST}",
                "-target-install-dir", "/tmp/vtune_profiler_2025.0.1.629235",
                "-collect", "uarch-exploration",
                "-result-dir", str(target_dir),
                "--app-working-dir", "/home/cc/bench_exe/505.mcf_r",
                "--", "/home/cc/bench_exe/505.mcf_r/505.mcf_r.sh"
            ]
            
            try:
                subprocess.run(vtune_cmd)
                print(f"Completed run {run+1}/{RUNS_PER_FREQ} at {freq}MHz")
            except subprocess.CalledProcessError as e:
                print(f"VTune failed for {freq}Hz run {run+1}: {e}")

if __name__ == "__main__":
    main()
