import subprocess
import re
import csv

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

    data = []
    for line in output.splitlines():
        for metric, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                data.append({'Metric': metric, 'Value': match.group(1).strip()})

    return data

def run_command(command):
    # Run the command and capture output
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {result.stderr.decode('utf-8')}")
        return None
    print(result)
    return result.stdout.decode('utf-8')

def main():
    # List of report types
    report_types = ['505_1000_0', '505_1000_1', '505_1000_2', '505_1000_3', '505_1000_4']  # Replace with your actual report types

    combined_data = []
    for report_type in report_types:
        # Command to run (replace with your actual command)
        # Use double quotes around the entire command and escape any inner double quotes
        # command = f'powershell -Command "& {{ .\\get_report.bat summary \'{report_type}\" | Select-String \"Memory Bound\", \"Front-End Bound\", \"Core Bound\", \"Bad Speculation\", \"Retiring\", \"Elapsed Time\", \"CPI Rate\", \"Average CPU Freq\" }}"'
        command = f'powershell -Command "& {{ .\\get_summary.bat {report_type}}}"'
        

        output = run_command(command)
        print(output)
        if output:
            data = parse_output(output)
            
            # Add report name to each entry
            for entry in data:
                entry['Report'] = report_type
                combined_data.append(entry)

            print(f"Processed report: {report_type}")

    # Save combined data to CSV
    with open('combined_report.csv', 'w', newline='') as csvfile:
        fieldnames = ['Report', 'Metric', 'Value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in combined_data:
            writer.writerow(row)

    print("Combined report saved to combined_report.csv")

if __name__ == "__main__":
    main()
