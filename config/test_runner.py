"""
Test Runner
"""
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "reports" / "results"
LOCK_FILE = BASE_DIR / "reports" / ".running"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class TestRunner:
    def run_test(self, test_path, test_name="اختبار"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_report = RESULTS_DIR / f"raw_{timestamp}.json"

        # Create lock file
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(LOCK_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "test_name": test_name,
                    "test_path": test_path,
                    "started_at": datetime.now().isoformat(),
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            "-v",
            "--json-report",
            f"--json-report-file={json_report}",
            "--tb=short",
        ]

        print(f"Running: {' '.join(cmd)}")
        start = datetime.now()

        try:
            result = subprocess.run(
                cmd, cwd=str(BASE_DIR),
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
            )
            returncode = result.returncode
            stdout = result.stdout
        finally:
            # Remove lock file
            if LOCK_FILE.exists():
                try:
                    LOCK_FILE.unlink()
                except Exception:
                    pass

        duration = (datetime.now() - start).total_seconds()

        summary = self._save_summary(
            timestamp, duration, json_report, returncode, test_path, test_name
        )
        return {
            "success": returncode == 0,
            "run_id": timestamp,
            "stdout": stdout,
            "summary": summary,
        }

    def _save_summary(self, run_id, duration, json_report, exit_code, test_path, test_name):
        data = {"summary": {}, "tests": []}
        if json_report.exists():
            try:
                with open(json_report, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass

        summary = {
            "run_id": run_id,
            "timestamp": run_id,
            "test_path": test_path,
            "test_name": test_name,
            "duration_seconds": round(duration, 2),
            "total": data["summary"].get("total", 0),
            "passed": data["summary"].get("passed", 0),
            "failed": data["summary"].get("failed", 0),
            "errors": data["summary"].get("error", 0),
            "skipped": data["summary"].get("skipped", 0),
            "exit_code": exit_code,
            "tests": [
                {
                    "name": t["nodeid"].split("::")[-1],
                    "file": t["nodeid"].split("::")[0],
                    "outcome": t["outcome"],
                    "duration": round(t.get("duration", 0), 2),
                }
                for t in data.get("tests", [])
            ],
        }

        summary_file = RESULTS_DIR / f"summary_{run_id}.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        return summary


_runner = None


def get_runner():
    global _runner
    if _runner is None:
        _runner = TestRunner()
    return _runner
