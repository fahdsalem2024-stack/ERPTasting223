"""
Queue Manager - Manages running and queued tests
+ Full logging of stdout/stderr
"""
import threading
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "reports" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class QueueManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_task = None
        self.queue = []
        self.process = None
        self.stopped = False
        self.current_log_file = None

    def is_running(self):
        with self.lock:
            return self.current_task is not None

    def get_status(self):
        with self.lock:
            return {
                "running": self.current_task,
                "queue": list(self.queue),
                "queue_length": len(self.queue),
            }

    def add(self, task_id, test_path, test_name):
        task = {
            "task_id": task_id,
            "test_path": test_path,
            "test_name": test_name,
            "added_at": datetime.now().isoformat(),
        }

        with self.lock:
            if self.current_task is None:
                self.current_task = task
                self.stopped = False
                should_start = True
            else:
                self.queue.append(task)
                should_start = False

        if should_start:
            self._run_task(task)
            return {"queued": False, "position": 0}
        else:
            position = len(self.queue)
            return {"queued": True, "position": position}

    def stop_current(self):
        with self.lock:
            if self.process and self.process.poll() is None:
                self.stopped = True
                try:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except Exception:
                        self.process.kill()
                    return True
                except Exception as e:
                    print(f"[stop_current] error: {e}")
                    return False
        return False

    def _run_task(self, task):
        thread = threading.Thread(target=self._execute, args=(task,), daemon=True)
        thread.start()

    def _execute(self, task):
        """Execute pytest with FULL logging"""
        task_id = task["task_id"]
        log_file = LOGS_DIR / f"{task_id}.log"
        self.current_log_file = log_file

        try:
            results_dir = BASE_DIR / "reports" / "results"
            results_dir.mkdir(parents=True, exist_ok=True)

            cmd = [
                sys.executable, "-m", "pytest",
                task["test_path"],
                "-v",
                "-s",  # ← مهم: يعرض print و loguru
                "--json-report",
                f"--json-report-file={results_dir}/raw_{task_id}.json",
                "--tb=long",  # ← تفاصيل أكتر
                "--log-cli-level=INFO",  # ← إظهار اللوج
            ]

            # نكتب في ملف اللوج
            with open(log_file, "w", encoding="utf-8") as lf:
                lf.write(f"===== START {datetime.now().isoformat()} =====\n")
                lf.write(f"CMD: {' '.join(cmd)}\n")
                lf.write(f"CWD: {BASE_DIR}\n")
                lf.write("=" * 60 + "\n\n")
                lf.flush()

                self.process = subprocess.Popen(
                    cmd,
                    cwd=str(BASE_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,  # line buffering
                )

                task["pid"] = self.process.pid
                task["status"] = "running"
                task["log_file"] = str(log_file)
                lf.write(f"PID: {self.process.pid}\n\n")
                lf.flush()

                # نقرأ الـ output سطر بسطر
                for line in self.process.stdout:
                    lf.write(line)
                    lf.flush()
                    # نطبعه في PowerShell كمان
                    print(f"[{task_id}] {line}", end="", flush=True)

                self.process.wait()

                lf.write(f"\n===== END {datetime.now().isoformat()} =====\n")
                lf.write(f"Exit code: {self.process.returncode}\n")

            if self.stopped:
                task["status"] = "stopped"
                self.stopped = False
            else:
                task["status"] = "completed" if self.process.returncode == 0 else "failed"
                task["exit_code"] = self.process.returncode

        except Exception as e:
            task["status"] = "error"
            task["error"] = str(e)[:500]
            try:
                with open(log_file, "a", encoding="utf-8") as lf:
                    lf.write(f"\n\n[FATAL ERROR] {str(e)}\n")
            except Exception:
                pass

        finally:
            self.process = None
            self._next()

    def _next(self):
        next_task = None
        with self.lock:
            if self.queue:
                next_task = self.queue.pop(0)
                self.current_task = next_task
                self.stopped = False
            else:
                self.current_task = None

        if next_task:
            self._run_task(next_task)

    def read_log(self, task_id, max_lines=200):
        """يقرأ ملف اللوج"""
        log_file = LOGS_DIR / f"{task_id}.log"
        if not log_file.exists():
            return {"success": False, "error": "Log not found"}

        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            # آخر max_lines سطر
            tail = lines[-max_lines:] if len(lines) > max_lines else lines
            return {
                "success": True,
                "task_id": task_id,
                "total_lines": len(lines),
                "lines": [l.rstrip() for l in tail],
                "log_file": str(log_file),
            }
        except Exception as e:
            return {"success": False, "error": str(e)[:200]}


_manager = None


def get_manager():
    global _manager
    if _manager is None:
        _manager = QueueManager()
    return _manager