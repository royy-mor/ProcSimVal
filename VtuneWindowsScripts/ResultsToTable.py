import subprocess
import re
import csv

USE_EXISTING = "C:\\Users\\roymo\\Documents\\ProcSimVal\\VtuneWindowsScripts\\combined_report.csv"

def parse_output(output):
    # Regular expressions to match each metric
    patterns = {
        'Elapsed Time': r'Elapsed Time: (.*)',
        'CPI Rate': r'CPI Rate: (.*)',
        'Retiring': r'Retiring: (.*)',
        'Front-End Bound': r'Front-End Bound: (.*)',
        'Bad Speculation': r'Bad Speculation: (.*)',
        'Memory Bound': r'Memory Bound: (.*)',
        'Core Bound': r'Core Bound: (.*)',
        'Average CPU Frequency': r'Average CPU Frequency: (.*)',
    }

    data = {
        'Report': None,
        'Elapsed Time (s)': None,
        'CPI Rate': None,
        'Retiring (%)': None,
        'Front-End Bound (%)': None,
        'Bad Speculation (%)': None,
        'Memory Bound (%)': None,
        'Core Bound (%)': None,
        'Average CPU Frequency (GHz)': None,
    }

    for line in output.splitlines():
        for metric, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                value = match.group(1).strip()
                # Remove units from the value
                if metric in ['Retiring', 'Front-End Bound', 'Bad Speculation', 'Memory Bound', 'Core Bound']:
                    data[f'{metric} (%)'] = value.split('%')[0]
                elif metric == 'Elapsed Time':
                    data[f'{metric} (s)'] = value.split('s')[0]
                elif metric == 'Average CPU Frequency':
                    data[f'{metric} (GHz)'] = value.split()[0]
                else:
                    data[metric] = value.split()[0]

    return data

def run_command(command):
    # Run the command and capture output
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {result.stderr.decode('utf-8')}")
        return None
    return result.stdout.decode('utf-8')

def main():
    # List of report types
    benches = [500, 502, 505, 520, 523, 531, 541, 548, 557]
    freq_range = list(range(1000, 2601, 100)) + [3700]
    freq_range.remove(1400)
    freq_range.remove(2200)
    report_types = [f'{bench}_{mhz}_{iter}'
                    for bench in benches 
                    for mhz in freq_range 
                    for iter in range(5)]

    combined_data = []
    for report_type in report_types:
        # Command to run (replace with your actual command)
        command = f'powershell -Command "& {{ .\\get_summary.bat {report_type}}}"'

        output = run_command(command)
        if output:
            data = parse_output(output)
            data['Report'] = report_type
            combined_data.append(data)

            print(f"Processed report: {report_type}")

    # Save combined data to CSV
    fieldnames = ['Report', 'Elapsed Time (s)', 'CPI Rate', 'Retiring (%)', 'Front-End Bound (%)', 'Bad Speculation (%)', 'Memory Bound (%)', 'Core Bound (%)', 'Average CPU Frequency (GHz)']
    with open('combined_report.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in combined_data:
            writer.writerow(row)

    print("Combined report saved to combined_report.csv")

if __name__ == "__main__":
    main()
