"""
log_system.py

Phase 2 - Log Analytics System

Implements:
- Log Ingestion (Hash Table)
- Sequential Processing (Queue)
- Activity Scoring (Config-driven)
- Ranking (Heap-based Priority Queue)
- Department-level Analytics

"""

from collections import deque
import heapq
import json
from typing import List, Dict, Tuple, Any


class LogAnalyticsSystem:
    """
    Core Log Analytics System implementing key data structures:
    - Hash Table (dict)
    - Queue (deque)
    - Priority Queue (heapq)
    """

    def __init__(self, score_file: str = "scores.json"):
        """
        Initialize system and load scoring configuration.
        """
        self.employee_logs: Dict[str, List[dict]] = {}
        self.log_queue: deque = deque()

        # Load scoring rules
        with open(score_file, "r") as f:
            self.score_data = json.load(f)

    # -----------------------------
    # INGESTION (HASH TABLE + QUEUE)
    # -----------------------------
    def ingest_log(self, log: Dict[str, Any]) -> None:
        """
        Store log in hash table and queue.

        Args:
            log (dict): log entry
        """
        emp_id = log["employee_id"]

        if emp_id not in self.employee_logs:
            self.employee_logs[emp_id] = []

        self.employee_logs[emp_id].append(log)
        self.log_queue.append(log)

    # -----------------------------
    # SEQUENTIAL PROCESSING (QUEUE)
    # -----------------------------
    def process_logs(self, limit: int = 10) -> None:
        """
        Process logs sequentially (FIFO).

        Args:
            limit (int): number of logs to display
        """
        print("\n=== Processing Logs (FIFO) ===\n")

        count = 0
        while self.log_queue and count < limit:
            log = self.log_queue.popleft()
            print(log)
            count += 1

    # -----------------------------
    # SCORING FUNCTION
    # -----------------------------
    def get_activity_score(self, activity: str) -> int:
        """
        Compute score for an activity using config rules.
        """
        activity = activity.lower()

        for category in ["high", "medium", "neutral", "negative"]:
            if any(keyword in activity for keyword in self.score_data[category]):
                return self.score_data["values"][category]

        return 0

    # -----------------------------
    # EMPLOYEE SCORING
    # -----------------------------
    def compute_employee_score(self, emp_id: str) -> int:
        """
        Compute total score for an employee.

        Returns:
            int
        """
        return sum(
            self.get_activity_score(log["activity"])
            for log in self.employee_logs.get(emp_id, [])
        )

    # -----------------------------
    # TOP-N RANKING (PRIORITY QUEUE)
    # -----------------------------
    def rank_employees(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        Rank employees by productivity score.

        Returns:
            List of (employee_id, score)
        """
        heap = []

        for emp_id in self.employee_logs:
            score = self.compute_employee_score(emp_id)
            heapq.heappush(heap, (-score, emp_id))

        ranking = []
        for _ in range(min(top_n, len(heap))):
            score, emp = heapq.heappop(heap)
            ranking.append((emp, -score))

        return ranking

    # -----------------------------
    # DEPARTMENT ANALYSIS
    # -----------------------------
    def analyze_by_department(self, emp_department: Dict[str, str]) -> Dict[str, Dict]:
        """
        Aggregate logs and scores by department.

        Returns:
            dict: department-wise analytics
        """
        dept_result = {}

        for emp_id, logs in self.employee_logs.items():
            dept = emp_department.get(emp_id, "Unknown")

            if dept not in dept_result:
                dept_result[dept] = {
                    "total_logs": 0,
                    "total_score": 0
                }

            dept_result[dept]["total_logs"] += len(logs)
            dept_result[dept]["total_score"] += self.compute_employee_score(emp_id)

        return dept_result
