import os
import subprocess
from pathlib import Path

# full freq range: 1000, 1100, 1200, 1300, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2300, 2400, 2500, 2600, 3700
# full intrate benchmarks: 500, 502, 505, 520, 523, 531, 541, 548, 557
# full intspeed benchmarks: +100
# full fprate benchmarks: 503, 507, 510, 511, 519, 521, 526, 527

BENCHES = [541]
FREQUENCIES = [1600, 1700, 1800, 1900, 2000, 2100, 2300, 2400, 2500, 2600, 3700]
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
    for bench in BENCHES:
        for freq in FREQUENCIES:
            prefix = f"{bench}_{freq}_"
            
            try:
                ssh_command(f"~/scripts/set_freq_cache.sh {freq}")
            except subprocess.CalledProcessError:
                continue

            for run in range(RUNS_PER_FREQ):
                target_dir = find_available_folder(BASE_DIR, prefix)
                target_dir.mkdir(parents=True)
                
                print(f"Starting bench {bench} run {run+1}/{RUNS_PER_FREQ} at {freq}MHz")
                print(f"Target directory: {target_dir}")

                vtune_cmd = [
                    VTUNE_PATH,
                    "-target-system", f"ssh:{REMOTE_USER}@{REMOTE_HOST}",
                    "-target-install-dir", "/tmp/vtune_profiler_2025.0.1.629235",
                    "-collect", "uarch-exploration",
                    "-result-dir", str(target_dir),
                    "--app-working-dir", "/home/cc/scripts",
                    "--", "/home/cc/scripts/good_run.sh",
                    "run", str(bench)
                ]
                # vtune_cmd = f'"C:\Program Files (x86)\Intel\oneAPI\vtune\2025.0\bin64\vtune" -target-system ssh:{REMOTE_USER}@{REMOTE_HOST} -target-install-dir=/tmp/vtune_profiler_2025.0.1.629235 -collect uarch-exploration -result-dir {str(target_dir)} --app-working-dir=/home/cc/scripts -- /home/cc/scripts/run.sh run 505'
                
                # print(vtune_cmd)

                try:
                    subprocess.run(vtune_cmd)
                    print(f"Completed run {run+1}/{RUNS_PER_FREQ} at {freq}MHz")
                except subprocess.CalledProcessError as e:
                    print(f"VTune failed for {freq}Hz run {run+1}: {e}")

if __name__ == "__main__":
    main()
