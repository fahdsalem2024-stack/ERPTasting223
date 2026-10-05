/**
 * Test Runner - Live Progress
 */

class TestRunner {
    constructor(options) {
        this.modalId = options.modalId || 'runningModal';
        this.progressId = options.progressId || 'runProgress';
        this.statusId = options.statusId || 'runStatus';
        this.nameId = options.nameId || 'runTestName';
        this.timeId = options.timeId || 'runTime';
        this.logId = options.logId || 'runLog';
        this.pollInterval = 2000;
        this.startTime = null;
        this.pollTimer = null;
    }

    openModal(testName) {
        const nameEl = document.getElementById(this.nameId);
        if (nameEl) nameEl.textContent = testName;

        this.resetProgress();
        this.startTime = Date.now();
        this.startTimer();

        const modalEl = document.getElementById(this.modalId);
        if (modalEl) {
            this.modal = new bootstrap.Modal(modalEl);
            this.modal.show();
        }
    }

    resetProgress() {
        const bar = document.getElementById(this.progressId);
        if (bar) bar.style.width = '0%';

        const status = document.getElementById(this.statusId);
        if (status) status.textContent = 'جاري البدء...';

        const log = document.getElementById(this.logId);
        if (log) log.innerHTML = '';
    }

    startTimer() {
        if (this.timerInterval) clearInterval(this.timerInterval);
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const mins = Math.floor(elapsed / 60);
            const secs = elapsed % 60;
            const timeEl = document.getElementById(this.timeId);
            if (timeEl) {
                timeEl.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
            }
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    setProgress(percent, statusText) {
        const bar = document.getElementById(this.progressId);
        if (bar) bar.style.width = percent + '%';

        const status = document.getElementById(this.statusId);
        if (status && statusText) status.textContent = statusText;
    }

    addLog(message, type = 'info') {
        const log = document.getElementById(this.logId);
        if (!log) return;

        const time = new Date().toLocaleTimeString('en-GB', { hour12: false });
        const colors = {
            info: 'text-muted',
            success: 'text-success',
            error: 'text-danger',
            warning: 'text-warning',
        };
        const icons = {
            info: 'bi-info-circle',
            success: 'bi-check-circle',
            error: 'bi-x-circle',
            warning: 'bi-exclamation-triangle',
        };

        const entry = document.createElement('div');
        entry.className = `small ${colors[type] || 'text-muted'} mb-1`;
        entry.innerHTML = `<i class="bi ${icons[type]}"></i> <span class="text-muted">[${time}]</span> ${message}`;
        log.appendChild(entry);
        log.scrollTop = log.scrollHeight;
    }

    async run(testPath, testName) {
        this.openModal(testName);
        this.setProgress(5, 'جاري إرسال الطلب...');
        this.addLog(`بدء تشغيل: ${testName}`);

        try {
            const res = await fetch('/api/run-test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ test_path: testPath, test_name: testName })
            });

            const data = await res.json();

            if (!data.success) {
                this.addLog(`فشل: ${data.error}`, 'error');
                this.setProgress(100, 'فشل التشغيل');
                this.finish(false);
                return;
            }

            const taskId = data.task_id;
            this.addLog(`Task ID: ${taskId}`, 'info');
            this.setProgress(10, 'جاري التشغيل...');
            this.addLog('تم بدء الاختبار', 'success');

            // Start polling
            this.poll(taskId);

        } catch (e) {
            this.addLog(`خطأ: ${e.message}`, 'error');
            this.setProgress(100, 'خطأ');
            this.finish(false);
        }
    }

    poll(taskId) {
        let attempts = 0;
        const maxAttempts = 300; // ~10 min max

        this.pollTimer = setInterval(async () => {
            attempts++;

            if (attempts > maxAttempts) {
                this.addLog('انتهى الوقت المسموح', 'error');
                this.finish(false);
                return;
            }

            try {
                const res = await fetch(`/api/status/${taskId}`);
                const data = await res.json();

                // Simulated progress (unknown real progress)
                const baseProgress = 15;
                const maxProgress = 95;
                const p = Math.min(baseProgress + (attempts * 1.5), maxProgress);
                this.setProgress(p, 'جاري التشغيل...');

                if (data.status === 'completed') {
                    this.setProgress(100, 'اكتمل بنجاح');
                    this.addLog('✅ اكتمل التشغيل', 'success');
                    this.finish(true, taskId);
                } else if (data.status === 'failed') {
                    this.setProgress(100, 'فشل');
                    this.addLog(`❌ فشل: ${data.error || 'غير معروف'}`, 'error');
                    this.finish(false, taskId);
                }

            } catch (e) {
                console.error('Poll error:', e);
            }
        }, this.pollInterval);
    }

    finish(success, taskId) {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
        this.stopTimer();

        // Show finish buttons
        setTimeout(() => {
            const finishArea = document.getElementById('finishArea');
            if (finishArea) {
                finishArea.classList.remove('d-none');
                const viewBtn = document.getElementById('viewReportBtn');
                if (viewBtn) {
                    viewBtn.onclick = () => { window.location.href = '/reports'; };
                }
            }
        }, 1500);
    }

    async stopTest(taskId) {
        this.addLog('⏹️ إيقاف الاختبار...', 'warning');
        try {
            const res = await fetch('/api/stop', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.addLog('تم إيقاف الاختبار', 'success');
                this.setProgress(100, 'تم الإيقاف');
                this.stopTimer();
                if (this.pollTimer) {
                    clearInterval(this.pollTimer);
                    this.pollTimer = null;
                }
            } else {
                this.addLog(data.message || 'فشل الإيقاف', 'error');
            }
        } catch (e) {
            this.addLog('خطأ في الإيقاف: ' + e.message, 'error');
        }
    }
}

// Extend poll to show stop button
const originalPoll = TestRunner.prototype.poll;
TestRunner.prototype.poll = function(taskId) {
    // Show stop button
    const stopBtn = document.getElementById('stopBtn');
    if (stopBtn) {
        stopBtn.classList.remove('d-none');
        stopBtn.onclick = () => this.stopTest(taskId);
    }
    originalPoll.call(this, taskId);
};

// Extend finish to hide stop button
const originalFinish = TestRunner.prototype.finish;
TestRunner.prototype.finish = function(success, taskId) {
    const stopBtn = document.getElementById('stopBtn');
    if (stopBtn) stopBtn.classList.add('d-none');
    originalFinish.call(this, success, taskId);
};

// ==================== Global Helper ====================
window.TestRunner = TestRunner;

window.runTest = function(testPath, testName) {
    const runner = new TestRunner({});
    runner.run(testPath, testName);
};

