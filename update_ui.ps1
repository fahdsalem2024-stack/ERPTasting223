Set-Location "D:\50505050505050505050050505050\erp-automation"

$backupDir = ".\_backup_ui_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Copy-Item ".\web\templates\base.html" "$backupDir\" -Force
Write-Host "Backup: $backupDir" -ForegroundColor Green

$baseFile = ".\web\templates\base.html"
$newBase = @"
<!DOCTYPE html>
<html lang="{{ current_lang }}" dir="{{ text_dir }}" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ site_name }}{% endblock %}</title>
    {% if text_dir == "rtl" %}
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    {% else %}
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    {% endif %}
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style-dark.css') }}">
    {% if favicon %}
    <link rel="icon" href="{{ url_for('static', filename='uploads/' + favicon) }}">
    {% endif %}
    <script>
        (function() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        })();
    </script>
    {% block extra_css %}{% endblock %}
</head>
<body>

<div class="app-layout">
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <a class="sidebar-brand" href="{{ url_for('index') }}">
                {% if logo %}
                <img src="{{ url_for('static', filename='uploads/' + logo) }}" alt="Logo">
                {% else %}
                <i class="bi bi-cpu"></i>
                {% endif %}
                <span>{{ site_name }}</span>
            </a>
            <button class="sidebar-toggle" id="sidebarToggle" title="toggle">
                <i class="bi bi-chevron-double-right"></i>
            </button>
        </div>

        <nav class="sidebar-nav">
            <div class="nav-section">Main</div>
            <a class="sidebar-link {% if request.endpoint == 'index' %}active{% endif %}" href="{{ url_for('index') }}">
                <i class="bi bi-house-door"></i><span>Home</span>
            </a>
            <a class="sidebar-link {% if request.endpoint == 'tests' %}active{% endif %}" href="{{ url_for('tests') }}">
                <i class="bi bi-clipboard-check"></i><span>Tests</span>
            </a>
            <a class="sidebar-link {% if 'reports' in request.endpoint %}active{% endif %}" href="{{ url_for('reports') }}">
                <i class="bi bi-bar-chart-line"></i><span>Reports</span>
            </a>
            <a class="sidebar-link {% if request.endpoint == 'live_viewer' %}active{% endif %}" href="{{ url_for('live_viewer') }}">
                <i class="bi bi-broadcast text-danger"></i><span>Live</span>
            </a>

            <div class="nav-section">Manage</div>
            <a class="sidebar-link {% if request.endpoint == 'schedule' %}active{% endif %}" href="{{ url_for('schedule') }}">
                <i class="bi bi-calendar-week"></i><span>Schedule</span>
            </a>
            <a class="sidebar-link {% if request.endpoint == 'compare' %}active{% endif %}" href="{{ url_for('compare') }}">
                <i class="bi bi-arrow-left-right"></i><span>Compare</span>
            </a>
            <a class="sidebar-link {% if request.endpoint == 'queue' %}active{% endif %}" href="{{ url_for('queue') }}">
                <i class="bi bi-list-task"></i><span>Queue</span>
            </a>

            <div class="nav-section">System</div>
            <a class="sidebar-link {% if request.endpoint == 'settings' %}active{% endif %}" href="{{ url_for('settings') }}">
                <i class="bi bi-gear"></i><span>Settings</span>
            </a>
            <a class="sidebar-link {% if request.endpoint == 'users' %}active{% endif %}" href="{{ url_for('users') }}">
                <i class="bi bi-people"></i><span>Users</span>
            </a>
        </nav>

        <div class="sidebar-footer">
            {% if current_user %}
            <div class="dropdown">
                <div class="user-card" data-bs-toggle="dropdown">
                    <div class="user-avatar">{{ (current_user.full_name or current_user.username)[0]|upper }}</div>
                    <div class="user-info">
                        <div class="name">{{ current_user.full_name or current_user.username }}</div>
                        <div class="role">{{ current_user.role }}</div>
                    </div>
                    <i class="bi bi-three-dots-vertical text-muted"></i>
                </div>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item" href="{{ url_for('users') }}"><i class="bi bi-people"></i> Users</a></li>
                    <li><a class="dropdown-item" href="{{ url_for('settings') }}"><i class="bi bi-gear"></i> Settings</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item text-danger" href="{{ url_for('logout') }}"><i class="bi bi-box-arrow-right"></i> Logout</a></li>
                </ul>
            </div>
            {% endif %}
        </div>
    </aside>

    <div class="sidebar-overlay" id="sidebarOverlay"></div>

    <main class="main-content">
        <div class="topbar">
            <div class="topbar-left">
                <button class="icon-btn d-lg-none" id="mobileMenuBtn"><i class="bi bi-list"></i></button>
                <h1 class="topbar-title">{% block page_title %}{{ site_name }}{% endblock %}</h1>
            </div>
            <div class="topbar-right">
                <div class="dropdown">
                    <button class="icon-btn" data-bs-toggle="dropdown" title="Language"><i class="bi bi-translate"></i></button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="{{ url_for('set_lang', lang='ar') }}">Arabic</a></li>
                        <li><a class="dropdown-item" href="{{ url_for('set_lang', lang='en') }}">English</a></li>
                    </ul>
                </div>
                <button class="icon-btn" id="themeToggle" title="Theme">
                    <i class="bi bi-moon-stars-fill" id="themeIcon"></i>
                </button>
            </div>
        </div>

        <div class="page-content">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, msg in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                            {{ msg }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </div>

        <footer class="text-center py-4">
            <i class="bi bi-cpu"></i> {{ site_config.company_name_ar or 'ERP Test Automation v4.2' }}
        </footer>
    </main>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="{{ url_for('static', filename='js/runner.js') }}"></script>
<script>
(function() {
    const html = document.documentElement;
    const toggle = document.getElementById('themeToggle');
    const icon = document.getElementById('themeIcon');
    function updateIcon(theme) {
        if (icon) icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    }
    updateIcon(html.getAttribute('data-theme') || 'light');
    if (toggle) {
        toggle.addEventListener('click', function() {
            const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme);
        });
    }
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (localStorage.getItem('sidebar_collapsed') === 'true' && window.innerWidth > 991) {
        sidebar.classList.add('collapsed');
    }
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebar_collapsed', sidebar.classList.contains('collapsed'));
        });
    }
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', () => sidebar.classList.toggle('mobile-open'));
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', () => sidebar.classList.remove('mobile-open'));
})();
</script>
{% block extra_js %}{% endblock %}
</body>
</html>
"@

[System.IO.File]::WriteAllText($baseFile, $newBase, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: base.html updated" -ForegroundColor Green