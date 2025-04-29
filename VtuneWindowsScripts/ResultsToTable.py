import subprocess
import re
import csv
import statistics
import os

# use_existing = "C:\\Users\\roymo\\Documents\\ProcSimVal\\VtuneWindowsScripts\\combined_report.csv"
use_existing = None

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
                    val = float(value.split()[0])
                    if val > 4: 
                        val /= 1000
                    data[f'{metric} (GHz)'] = val
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

def load_data_from_csv(file_path):
    data = []
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if float(row['Elapsed Time (s)']) >= 1:
                data.append(row)
    return data

def generate_data():
    # List of report types
    benches = [503, 507, 508, 510, 511, 519, 521, 538, 544, 549, 554]
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
        if(os.name == 'nt'):
            command = f'powershell -Command "& {{ .\\get_summary.bat {report_type}}}"'
        elif(os.name == 'posix'):
            pass

        output = run_command(command)
        if output:
            data = parse_output(output)
            data['Report'] = report_type
            
            # Filter out results with elapsed times under 1 second
            if float(data['Elapsed Time (s)']) >= 1:
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

    return combined_data

def calculate_medians(data):
    # Organize data by benchmark and frequency
    data_by_benchmark = {}
    for row in data:
        report = row['Report']
        parts = report.split('_')
        benchmark = f"{parts[0]}_{parts[1]}"
        
        if benchmark not in data_by_benchmark:
            data_by_benchmark[benchmark] = {'Elapsed Time (s)': [], 'CPI Rate': [], 'Retiring (%)': [], 'Front-End Bound (%)': [], 'Bad Speculation (%)': [], 'Memory Bound (%)': [], 'Core Bound (%)': [], 'Average CPU Frequency (GHz)': []}
        
        data_by_benchmark[benchmark]['Elapsed Time (s)'].append(float(row['Elapsed Time (s)']))
        data_by_benchmark[benchmark]['CPI Rate'].append(float(row['CPI Rate']))
        data_by_benchmark[benchmark]['Retiring (%)'].append(float(row['Retiring (%)']))
        data_by_benchmark[benchmark]['Front-End Bound (%)'].append(float(row['Front-End Bound (%)']))
        data_by_benchmark[benchmark]['Bad Speculation (%)'].append(float(row['Bad Speculation (%)']))
        data_by_benchmark[benchmark]['Memory Bound (%)'].append(float(row['Memory Bound (%)']))
        data_by_benchmark[benchmark]['Core Bound (%)'].append(float(row['Core Bound (%)']))
        data_by_benchmark[benchmark]['Average CPU Frequency (GHz)'].append(float(row['Average CPU Frequency (GHz)']))

    # Calculate medians
    medians_data = []
    for benchmark, values in data_by_benchmark.items():
        median_row = {
            'Benchmark': benchmark,
            'Elapsed Time (s) Median': statistics.median(values['Elapsed Time (s)']) if values['Elapsed Time (s)'] else None,
            'CPI Rate Median': statistics.median(values['CPI Rate']) if values['CPI Rate'] else None,
            'Retiring (%) Median': statistics.median(values['Retiring (%)']) if values['Retiring (%)'] else None,
            'Front-End Bound (%) Median': statistics.median(values['Front-End Bound (%)']) if values['Front-End Bound (%)'] else None,
            'Bad Speculation (%) Median': statistics.median(values['Bad Speculation (%)']) if values['Bad Speculation (%)'] else None,
            'Memory Bound (%) Median': statistics.median(values['Memory Bound (%)']) if values['Memory Bound (%)'] else None,
            'Core Bound (%) Median': statistics.median(values['Core Bound (%)']) if values['Core Bound (%)'] else None,
            'Average CPU Frequency (GHz) Median': statistics.median(values['Average CPU Frequency (GHz)']) if values['Average CPU Frequency (GHz)'] else None,
        }
        medians_data.append(median_row)

    return medians_data

def main():
    if use_existing:
        print(f"Loading data from existing CSV: {use_existing}")
        combined_data = load_data_from_csv(use_existing)
    else:
        combined_data = generate_data()

    # Calculate and save medians to CSV
    medians_data = calculate_medians(combined_data)
    medians_fieldnames = ['Benchmark', 'Elapsed Time (s) Median', 'CPI Rate Median', 'Retiring (%) Median', 'Front-End Bound (%) Median', 'Bad Speculation (%) Median', 'Memory Bound (%) Median', 'Core Bound (%) Median', 'Average CPU Frequency (GHz) Median']
    with open('medians_report.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=medians_fieldnames)
        
        writer.writeheader()
        for row in medians_data:
            writer.writerow(row)

    print("Medians report saved to medians_report.csv")

if __name__ == "__main__":
    main()