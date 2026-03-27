"""
main.py

FEATURES:
- FIFO log processing
- Raw activity scoring from LogAnalyticsSystem
- Efficiency-based scoring (score per log)
- Percentile-based normalization (0–100 scale)
- Employee ranking (Top-N)
- Department analytics
- Clean tabular output
- Fair comparison across employees
- Scalable scoring model for large datasets
"""

"""
main.py (FINAL FIXED VERSION)

Fixes:
- Removes dependency on system.employee_log_count
- Computes logs per employee directly from logs
- Keeps percentile scoring model (0–100)
- Fully robust and submission-ready
"""

import json
from collections import defaultdict
from log_system import LogAnalyticsSystem


# ============================================================
# TABULAR PRINT UTILITY
# ============================================================
def print_table(headers, rows):

    if not rows:
        print("\nNo data available.\n")
        return

    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    def format_row(row):
        return " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))

    print("\n" + format_row(headers))
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))

    for row in rows:
        print(format_row(row))


# ============================================================
# LOAD DATA
# ============================================================
def load_logs():
    with open("logs.json", "r") as f:
        return json.load(f)


def load_employees():
    with open("employees.json", "r") as f:
        data = json.load(f)
    return {e["employee_id"]: e for e in data}


# ============================================================
# SCORING HELPERS
# ============================================================
def compute_efficiency(raw_score, total_logs):
    if total_logs == 0:
        return 0
    return raw_score / total_logs


def percentile_function(values):
    sorted_vals = sorted(values)

    def get_percentile(v):
        rank = sum(1 for x in sorted_vals if x <= v)
        return round((rank / len(sorted_vals)) * 100, 2)

    return get_percentile


# ============================================================
# MAIN PIPELINE
# ============================================================
def main():

    system = LogAnalyticsSystem()

    logs = load_logs()
    employees = load_employees()

    # --------------------------------------------------------
    # STEP 1: INGEST LOGS
    # --------------------------------------------------------
    for log in logs:
        system.ingest_log(log)

    # --------------------------------------------------------
    # STEP 2: PROCESS LOGS
    # --------------------------------------------------------
    system.process_logs(limit=10)

    # --------------------------------------------------------
    # STEP 3: BUILD RAW SCORES
    # --------------------------------------------------------
    raw_scores = system.rank_employees(top_n=1000)

    # --------------------------------------------------------
    # STEP 4: COMPUTE LOG COUNTS (FIX HERE)
    # --------------------------------------------------------
    log_counts = defaultdict(int)

    for log in logs:
        log_counts[log["employee_id"]] += 1

    # --------------------------------------------------------
    # STEP 5: ENRICH DATA
    # --------------------------------------------------------
    enriched = []
    efficiency_values = []

    for emp_id, raw_score in raw_scores:

        emp_data = employees.get(emp_id, {})

        total_logs = log_counts.get(emp_id, 1)

        efficiency = compute_efficiency(raw_score, total_logs)
        efficiency_values.append(efficiency)

        enriched.append({
            "emp_id": emp_id,
            "name": emp_data.get("name", "Unknown"),
            "dept": emp_data.get("department", "Unknown"),
            "logs": total_logs,
            "raw": raw_score,
            "eff": efficiency
        })

    # --------------------------------------------------------
    # STEP 6: PERCENTILE SCORING
    # --------------------------------------------------------
    percentile = percentile_function(efficiency_values)

    for e in enriched:
        e["score"] = percentile(e["eff"])

    # --------------------------------------------------------
    # STEP 7: SORT
    # --------------------------------------------------------
    enriched.sort(key=lambda x: x["score"], reverse=True)

    # --------------------------------------------------------
    # STEP 8: TOP EMPLOYEES TABLE
    # --------------------------------------------------------
    print("\n=== Top Employees (Final Score 0–100) ===")

    top_rows = [
        [
            e["emp_id"],
            e["name"],
            e["dept"],
            e["logs"],
            round(e["raw"], 2),
            round(e["eff"], 2),
            e["score"]
        ]
        for e in enriched[:5]
    ]

    print_table(
        ["Emp ID", "Name", "Department", "Logs", "Raw Score", "Efficiency", "Final Score"],
        top_rows
    )

    # --------------------------------------------------------
    # STEP 9: DEPARTMENT ANALYTICS
    # --------------------------------------------------------
    print("\n=== Department Analytics ===")

    emp_dept = {e["employee_id"]: e["department"] for e in employees.values()}

    dept_stats = system.analyze_by_department(emp_dept)

    dept_rows = [
        [dept, stats["total_logs"], stats["total_score"]]
        for dept, stats in dept_stats.items()
    ]

    print_table(
        ["Department", "Total Logs", "Total Score"],
        dept_rows
    )


if __name__ == "__main__":
    main()
