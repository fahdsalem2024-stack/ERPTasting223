Set-Location "D:\50505050505050505050050505050\erp-automation"

$backupDir = ".\_backup_ui2_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Copy-Item ".\web\templates\index.html" "$backupDir\" -Force
Copy-Item ".\web\templates\reports.html" "$backupDir\" -Force
Write-Host "Backup: $backupDir" -ForegroundColor Green

# ============================================================
# index.html — Dashboard
# ============================================================
$indexFile = ".\web\templates\index.html"
$newIndex = @"
{% extends "base.html" %}
{% block title %}{{ t('home') }} - {{ site_name }}{% endblock %}
{% block page_title %}Home{% endblock %}

{% block content %}
<div class="page-header">
    <h1>Welcome, {{ current_user.full_name or current_user.username }}</h1>
    <p>Dashboard - Quick system overview</p>
</div>

<div class="row g-3 mb-4">
    <div class="col-md-3 col-6">
        <div class="stat-card">
            <div class="stat-icon primary"><i class="bi bi-clipboard-check"></i></div>
            <div class="stat-value">{{ stats.total_runs or 0 }}</div>
            <div class="stat-label">Total Runs</div>
        </div>
    </div>
    <div class="col-md-3 col-6">
        <div class="stat-card">
            <div class="stat-icon success"><i class="bi bi-check-circle"></i></div>
            <div class="stat-value text-success">{{ stats.total_passed or 0 }}</div>
            <div class="stat-label">Passed</div>
        </div>
    </div>
    <div class="col-md-3 col-6">
        <div class="stat-card">
            <div class="stat-icon danger"><i class="bi bi-x-circle"></i></div>
            <div class="stat-value text-danger">{{ stats.total_failed or 0 }}</div>
            <div class="stat-label">Failed</div>
        </div>
    </div>
    <div class="col-md-3 col-6">
        <div class="stat-card">
            <div class="stat-icon warning"><i class="bi bi-graph-up"></i></div>
            <div class="stat-value">{{ stats.success_rate or 0 }}%</div>
            <div class="stat-label">Success Rate</div>
        </div>
    </div>
</div>

<div class="row g-3 mb-4">
    <div class="col-lg-8">
        <div class="chart-card">
            <h5><i class="bi bi-graph-up-arrow text-primary"></i> Trend</h5>
            <canvas id="trendChart" style="max-height: 280px;"></canvas>
        </div>
    </div>
    <div class="col-lg-4">
        <div class="chart-card">
            <h5><i class="bi bi-pie-chart text-primary"></i> Distribution</h5>
            <canvas id="donutChart" style="max-height: 280px;"></canvas>
        </div>
    </div>
</div>

<div class="chart-card">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="mb-0"><i class="bi bi-clock-history text-primary"></i> Recent Runs</h5>
        <a href="{{ url_for('reports') }}" class="btn btn-sm btn-outline-primary">View All</a>
    </div>

    {% if recent_runs %}
        {% for run in recent_runs %}
        {% set is_passed = (run.failed or 0) == 0 and (run.errors or 0) == 0 %}
        <a href="{{ url_for('report_detail', run_id=run.run_id) }}" class="activity-item">
            <div class="activity-icon {% if is_passed %}success{% else %}danger{% endif %}">
                <i class="bi bi-{% if is_passed %}check-circle{% else %}x-circle{% endif %}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">{{ run.test_name or 'Test' }}</div>
                <div class="activity-meta">{{ run.run_id }} - {{ run.duration_seconds|round(0)|int }}s</div>
            </div>
            <i class="bi bi-chevron-left text-muted"></i>
        </a>
        {% endfor %}
    {% else %}
        <div class="empty-state">
            <i class="bi bi-inbox"></i>
            <p>No runs yet</p>
            <a href="{{ url_for('tests') }}" class="btn btn-primary"><i class="bi bi-play"></i> Run Test</a>
        </div>
    {% endif %}
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
(function() {
    const stats = { passed: {{ stats.total_passed or 0 }}, failed: {{ stats.total_failed or 0 }} };

    const donutEl = document.getElementById('donutChart');
    if (donutEl && (stats.passed + stats.failed) > 0) {
        new Chart(donutEl, {
            type: 'doughnut',
            data: {
                labels: ['Passed', 'Failed'],
                datasets: [{
                    data: [stats.passed, stats.failed],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 0, hoverOffset: 8
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '70%',
                plugins: { legend: { position: 'bottom', labels: { padding: 16 } } }
            }
        });
    }

    const trendEl = document.getElementById('trendChart');
    {% if recent_runs %}
    const recentRuns = {{ recent_runs|tojson|safe }};
    const labels = [], passedData = [], failedData = [];
    recentRuns.slice().reverse().forEach(r => {
        labels.push(r.run_id ? r.run_id.substr(9, 4) : '');
        passedData.push(r.passed || 0);
        failedData.push((r.failed || 0) + (r.errors || 0));
    });
    if (trendEl) {
        new Chart(trendEl, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Passed', data: passedData, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', tension: 0.4, fill: true, pointRadius: 4 },
                    { label: 'Failed', data: failedData, borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)', tension: 0.4, fill: true, pointRadius: 4 }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
            }
        });
    }
    {% endif %}
})();
</script>
{% endblock %}
"@

[System.IO.File]::WriteAllText($indexFile, $newIndex, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: index.html updated" -ForegroundColor Green

# ============================================================
# reports.html — Charts
# ============================================================
$reportsFile = ".\web\templates\reports.html"
$newReports = @"
{% extends "base.html" %}
{% block title %}Reports - {{ site_name }}{% endblock %}
{% block page_title %}Reports{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div class="page-header mb-0">
        <h1>Reports</h1>
        <p>Test runs history</p>
    </div>
    <div>
        <a href="{{ url_for('export_pdf') }}" class="btn btn-outline-danger btn-sm"><i class="bi bi-file-pdf"></i> PDF</a>
        <a href="{{ url_for('export_excel') }}" class="btn btn-outline-success btn-sm"><i class="bi bi-file-excel"></i> Excel</a>
        <a href="{{ url_for('export_csv') }}" class="btn btn-outline-info btn-sm"><i class="bi bi-file-csv"></i> CSV</a>
        <a href="{{ url_for('export_json') }}" class="btn btn-outline-secondary btn-sm"><i class="bi bi-file-json"></i> JSON</a>
    </div>
</div>

<div class="row g-3 mb-4">
    <div class="col-md-3 col-6">
        <div class="stat-card">
            <div class="stat-icon primary"><i class="bi bi-clipboard-data"></i></div>
            <div class="stat-value">{{ chart_data.total_runs or 0 }}</div>
            <div class="stat-label">Total Reports</div>
        </div>
    </div>
    <div class="col-md-3 col-6">
        <div class="stat-card">
            <div class="stat-icon success"><i class="bi bi-check-circle"></i></div>
            <div class="stat-value text-success">{{ chart_data.donut_passed or 0 }}</div>
            <div class="stat-label">Passed</div>
        </div>
    </div>
    <div class="col-md-3 col-6">
        <div class="stat-card">
            <div class="stat-icon danger"><i class="bi bi-x-circle"></i></div>
            <div class="stat-value text-danger">{{ chart_data.donut_failed or 0 }}</div>
            <div class="stat-label">Failed</div>
        </div>
    </div>
    <div class="col-md-3 col-6">
        <div class="stat-card">
            <div class="stat-icon warning"><i class="bi bi-graph-up"></i></div>
            <div class="stat-value">{{ chart_data.success_rate or 0 }}%</div>
            <div class="stat-label">Success Rate</div>
        </div>
    </div>
</div>

<div class="row g-3 mb-4">
    <div class="col-lg-8">
        <div class="chart-card">
            <h5><i class="bi bi-graph-up-arrow text-primary"></i> Trend</h5>
            <canvas id="trendChart" style="max-height: 300px;"></canvas>
        </div>
    </div>
    <div class="col-lg-4">
        <div class="chart-card">
            <h5><i class="bi bi-pie-chart text-primary"></i> Distribution</h5>
            <canvas id="donutChart" style="max-height: 300px;"></canvas>
        </div>
    </div>
</div>

<div class="card mb-4">
    <div class="card-body">
        <form method="get" class="row g-3">
            <div class="col-md-3">
                <label class="form-label">Filter by Status</label>
                <select name="status" class="form-select">
                    <option value="all" {% if status_filter == 'all' %}selected{% endif %}>All</option>
                    <option value="passed" {% if status_filter == 'passed' %}selected{% endif %}>Passed Only</option>
                    <option value="failed" {% if status_filter == 'failed' %}selected{% endif %}>Failed Only</option>
                </select>
            </div>
            <div class="col-md-6">
                <label class="form-label">Search</label>
                <input type="text" name="search" class="form-control" value="{{ search_query }}" placeholder="Search...">
            </div>
            <div class="col-md-3 d-flex align-items-end">
                <button type="submit" class="btn btn-primary me-2"><i class="bi bi-funnel"></i> Filter</button>
                <a href="{{ url_for('reports') }}" class="btn btn-outline-secondary"><i class="bi bi-x-circle"></i></a>
            </div>
        </form>
    </div>
</div>

<div class="card">
    <div class="card-body p-0">
        {% if reports %}
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Date</th>
                        <th style="width: 80px;">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for r in reports %}
                    {% set is_passed = (r.failed or 0) == 0 and (r.errors or 0) == 0 %}
                    <tr>
                        <td>
                            <strong>{{ r.test_name or 'Test' }}</strong>
                            <br><small class="text-muted">{{ r.run_id }}</small>
                        </td>
                        <td>
                            {% if is_passed %}
                            <span class="badge bg-success">Passed</span>
                            {% else %}
                            <span class="badge bg-danger">Failed</span>
                            {% endif %}
                        </td>
                        <td>{{ r.duration_seconds|round(0)|int }}s</td>
                        <td><small class="text-muted">{{ r.run_id }}</small></td>
                        <td>
                            <a href="{{ url_for('report_detail', run_id=r.run_id) }}" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-eye"></i>
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="empty-state">
            <i class="bi bi-inbox"></i>
            <p>No reports</p>
            <a href="{{ url_for('tests') }}" class="btn btn-primary"><i class="bi bi-play"></i> Run Test</a>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
(function() {
    const data = {{ chart_data|tojson|safe }};

    const trendEl = document.getElementById('trendChart');
    if (trendEl && data.trend_labels && data.trend_labels.length > 0) {
        new Chart(trendEl, {
            type: 'line',
            data: {
                labels: data.trend_labels,
                datasets: [
                    { label: 'Passed', data: data.trend_passed, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', tension: 0.4, fill: true, pointRadius: 4 },
                    { label: 'Failed', data: data.trend_failed, borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)', tension: 0.4, fill: true, pointRadius: 4 }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
            }
        });
    }

    const donutEl = document.getElementById('donutChart');
    if (donutEl && (data.donut_passed + data.donut_failed) > 0) {
        new Chart(donutEl, {
            type: 'doughnut',
            data: {
                labels: ['Passed', 'Failed'],
                datasets: [{
                    data: [data.donut_passed, data.donut_failed],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 0, hoverOffset: 8
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '70%',
                plugins: { legend: { position: 'bottom', labels: { padding: 16 } } }
            }
        });
    }
})();
</script>
{% endblock %}
"@

[System.IO.File]::WriteAllText($reportsFile, $newReports, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: reports.html updated" -ForegroundColor Green

Write-Host ""
Write-Host "Done! All 3 files updated." -ForegroundColor Green
Write-Host "Now refresh browser (Ctrl+F5)" -ForegroundColor Yellow