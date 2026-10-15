"""
Queue Manager - Manages running and queued tests
"""
import threading
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class QueueManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_task = None  # Currently running task
        self.queue = []           # Waiting tasks
        self.process = None       # Subprocess handle
        self.stopped = False

    def is_running(self):
        """Check if a test is currently running"""
        with self.lock:
            return self.current_task is not None

    def get_status(self):
        """Get current status"""
        with self.lock:
            return {
                "running": self.current_task,
                "queue": list(self.queue),
                "queue_length": len(self.queue),
            }

    def add(self, task_id, test_path, test_name):
        """Add a task to queue"""
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
        """Stop the current running test"""
        with self.lock:
            if self.process and self.process.poll() is None:
                self.stopped = True
                try:
                    self.process.terminate()
                    return True
                except Exception:
                    return False
        return False

    def _run_task(self, task):
        """Run a task in background thread"""
        thread = threading.Thread(target=self._execute, args=(task,), daemon=True)
        thread.start()

    def _execute(self, task):
        """Execute pytest subprocess"""
        try:
            results_dir = BASE_DIR / "reports" / "results"
            results_dir.mkdir(parents=True, exist_ok=True)

            cmd = [
                sys.executable, "-m", "pytest",
                task["test_path"],
                "-v",
                "--json-report",
                f"--json-report-file={results_dir}/raw_{task['task_id']}.json",
                "--tb=short",
            ]

            self.process = subprocess.Popen(
                cmd,
                cwd=str(BASE_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            # Store process so we can terminate it
            task["pid"] = self.process.pid
            task["status"] = "running"

            # Wait for completion
            output, _ = self.process.communicate()

            if self.stopped:
                task["status"] = "stopped"
                self.stopped = False
            else:
                task["status"] = "completed" if self.process.returncode == 0 else "failed"

        except Exception as e:
            task["status"] = "error"
            task["error"] = str(e)[:200]

        finally:
            self.process = None
            # Try to run next in queue
            self._next()

    def _next(self):
        """Run next task in queue"""
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


# Singleton
_manager = None


def get_manager():
    global _manager
    if _manager is None:
        _manager = QueueManager()
    return _manager
