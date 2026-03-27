"""
data_generator.py

This script generates synthetic activity logs that simulate real-world
enterprise systems such as Jira, GitHub, AWS, and VPN logs.

Usage:
    python data_generator.py <number_of_logs>

Output:
    A JSON file (logs.json) containing generated log entries.
"""

import random
import sys
import json
from datetime import datetime, timedelta


# -------------------------------
# Load Employee Data
# -------------------------------
def load_employees(filename="employees.json"):
    with open(filename, "r") as file:
        return json.load(file)


# -------------------------------
# Sample Sources
# -------------------------------
SOURCES = ["Jira", "GitHub", "AWS", "VPN"]
PROJECTS = ["ProjectA", "ProjectB", "ProjectC"]

ACTIVITIES = {
    "Jira": ["Task Created", "Task Started", "Task Completed"],
    "GitHub": ["Commit", "Pull Request", "Merge"],
    "AWS": ["Deploy", "Instance Start", "Instance Stop"],
    "VPN": ["Login", "Logout"]
}


# -------------------------------
# Helper Functions
# -------------------------------
def generate_timestamp(start_time, index):
    return (start_time + timedelta(seconds=index * random.randint(30, 120))) \
        .strftime("%Y-%m-%d %H:%M:%S")


def generate_details(source):
    if source == "Jira":
        return {"task_id": f"JIRA-{random.randint(100, 999)}"}
    elif source == "GitHub":
        return {
            "repo": random.choice(["backend", "frontend", "api-service"]),
            "lines_changed": random.randint(5, 500)
        }
    elif source == "AWS":
        return {"service": random.choice(["EC2", "S3", "Lambda"])}
    elif source == "VPN":
        return {"ip": f"192.168.1.{random.randint(1, 255)}"}
    return {}


# -------------------------------
# Generate Logs
# -------------------------------
def generate_logs(num_logs):
    logs = []
    start_time = datetime.now()

    employees = load_employees()
    employee_ids = [emp["employee_id"] for emp in employees]

    for i in range(num_logs):
        source = random.choice(SOURCES)
        activity = random.choice(ACTIVITIES[source])
        emp_id = random.choice(employee_ids)

        log = {
            "timestamp": generate_timestamp(start_time, i),
            "employee_id": emp_id,
            "source": source,
            "activity": activity,
            "project": random.choice(PROJECTS) if source != "VPN" else None,
            "details": generate_details(source)
        }

        logs.append(log)

    return logs


def save_to_file(logs, filename="logs.json"):
    with open(filename, "w") as file:
        json.dump(logs, file, indent=4)

    print(f"\nLogs saved to '{filename}'")


# -------------------------------
# Main
# -------------------------------
def main():
    if len(sys.argv) != 2:
        print("Usage: python data_generator.py <number_of_logs>")
        sys.exit(1)

    try:
        num_logs = int(sys.argv[1])
    except ValueError:
        print("Invalid number.")
        sys.exit(1)

    logs = generate_logs(num_logs)
    save_to_file(logs)


if __name__ == "__main__":
    main()
