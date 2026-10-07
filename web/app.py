"""
ERP Test Automation - Web Interface v4.2
"""
import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, send_from_directory, flash, Response
)
from web.config import Config
from web.i18n_helper import t, get_current_lang, get_dir
from web import data_helper, export_helper, settings_helper, auth
from web.queue_manager import get_manager as get_qm

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)


# ==================== Context Processors ====================
@app.context_processor
def inject_globals():
    site_config = settings_helper.load_site_config()
    lang = get_current_lang()
    site_name = site_config["site_name_ar"] if lang == "ar" else site_config["site_name_en"]

    return {
        "t": t,
        "current_lang": lang,
        "text_dir": get_dir(),
        "site_name": site_name,
        "site_name_en": site_config["site_name_en"],
        "site_config": site_config,
        "logo": site_config.get("logo_filename", ""),
        "favicon": site_config.get("favicon_filename", ""),
        "current_user": auth.current_user(),
    }


# ==================== Language ====================
@app.route("/set-lang/<lang>")
def set_lang(lang):
    if lang in ["ar", "en"]:
        session["lang"] = lang
        session.permanent = True
    return redirect(request.referrer or url_for("index"))


# ==================== Auth ====================
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if auth.login_user(username, password):
            next_url = request.args.get("next", url_for("index"))
            return redirect(next_url)
        else:
            error = "اسم المستخدم أو كلمة المرور غير صحيحة" if get_current_lang() == "ar" \
                else "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    auth.logout_user()
    return redirect(url_for("login"))


# ==================== Main ====================
@app.route("/")
@auth.login_required
def index():
    lang = get_current_lang()
    tests = data_helper.get_tests_registry(lang)
    stats = data_helper.get_stats()
    recent_runs = data_helper.load_recent_runs(limit=5)
    return render_template("index.html", tests=tests, stats=stats, recent_runs=recent_runs)


@app.route("/tests")
@auth.login_required
def tests():
    lang = get_current_lang()
    tests_list = data_helper.get_tests_registry(lang)
    return render_template("tests.html", tests=tests_list)


@app.route("/reports")
@auth.login_required
def reports():
    status_filter = request.args.get("status", "all")
    category_filter = request.args.get("category", "all")
    search_query = request.args.get("search", "").strip()

    summaries = data_helper.load_summaries()

    filtered = []
    for s in summaries:
        passed = s.get("passed", 0)
        failed = s.get("failed", 0) + s.get("errors", 0)

        if status_filter == "passed" and failed > 0:
            continue
        if status_filter == "failed" and failed == 0:
            continue

        if search_query:
            text = (s.get("test_name", "") + s.get("run_id", "")).lower()
            if search_query.lower() not in text:
                continue

        filtered.append(s)

    # Chart data
    trend_labels = []
    trend_passed = []
    trend_failed = []
    trend_duration = []

    for s in reversed(filtered[:20]):
        ts = s.get("run_id", "")
        label = f"{ts[9:11]}:{ts[11:13]}" if len(ts) >= 13 else ts
        trend_labels.append(label)
        trend_passed.append(s.get("passed", 0))
        trend_failed.append(s.get("failed", 0) + s.get("errors", 0))
        trend_duration.append(int(s.get("duration_seconds", 0)))

    total_passed = sum(s.get("passed", 0) for s in filtered)
    total_failed = sum(s.get("failed", 0) + s.get("errors", 0) for s in filtered)
    total_runs = len(filtered)
    success_rate = round((total_passed / (total_passed + total_failed) * 100)
                        if (total_passed + total_failed) > 0 else 0, 1)

    chart_data = {
        "trend_labels": trend_labels,
        "trend_passed": trend_passed,
        "trend_failed": trend_failed,
        "trend_duration": trend_duration,
        "donut_passed": total_passed,
        "donut_failed": total_failed,
        "total_runs": total_runs,
        "success_rate": success_rate,
    }

    return render_template(
        "reports.html",
        reports=filtered,
        status_filter=status_filter,
        category_filter=category_filter,
        search_query=search_query,
        chart_data=chart_data,
    )


@app.route("/reports/<run_id>")
@auth.login_required
def report_detail(run_id):
    summaries = data_helper.load_summaries()
    report = next((s for s in summaries if s.get("run_id") == run_id), None)
    if not report:
        return redirect(url_for("reports"))
    screenshots = data_helper.get_screenshots_for_run(run_id)
    return render_template("report_detail.html", report=report, screenshots=screenshots)


@app.route("/schedule")
@auth.login_required
def schedule():
    lang = get_current_lang()
    schedules = data_helper.load_schedules()
    tests_list = data_helper.get_tests_registry(lang)
    return render_template("schedule.html", schedules=schedules, tests=tests_list)


@app.route("/schedule/add", methods=["POST"])
@auth.login_required
def schedule_add():
    name = request.form.get("name", "").strip()
    test_id = request.form.get("test_id", "").strip()
    time_val = request.form.get("time", "").strip()
    frequency = request.form.get("frequency", "daily")

    if name and test_id and time_val:
        schedules = data_helper.load_schedules()
        schedules.append({
            "id": f"sch_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": name,
            "test_id": test_id,
            "time": time_val,
            "frequency": frequency,
            "enabled": True,
            "created_at": datetime.now().isoformat(),
        })
        data_helper.save_schedules(schedules)

    return redirect(url_for("schedule"))


@app.route("/schedule/delete/<sch_id>", methods=["POST"])
@auth.login_required
def schedule_delete(sch_id):
    schedules = data_helper.load_schedules()
    schedules = [s for s in schedules if s.get("id") != sch_id]
    data_helper.save_schedules(schedules)
    return redirect(url_for("schedule"))


@app.route("/compare")
@auth.login_required
def compare():
    all_runs = data_helper.load_summaries()
    run_a = request.args.get("a", "")
    run_b = request.args.get("b", "")

    data_a = next((r for r in all_runs if r.get("run_id") == run_a), None)
    data_b = next((r for r in all_runs if r.get("run_id") == run_b), None)

    return render_template(
        "compare.html",
        all_runs=all_runs,
        run_a=run_a,
        run_b=run_b,
        data_a=data_a,
        data_b=data_b,
    )


@app.route("/queue")
@auth.login_required
def queue():
    qm = get_qm()
    status = qm.get_status()
    return render_template("queue.html", status=status)


# ==================== Settings ====================
@app.route("/settings")
@auth.login_required
def settings():
    site_config = settings_helper.load_site_config()
    slack_config = _load_json(Config.SLACK_CONFIG)
    email_config = _load_json(Config.EMAIL_CONFIG)
    users = settings_helper.load_users()

    from web import test_sites_helper as _tsh

    test_sites_data = _tsh.load_all()
    return render_template(
        "settings.html",
        site_config=site_config,
        slack_config=slack_config,
        email_config=email_config,
        users=users,
        test_sites_data=test_sites_data,
        tunnel_config=__import__("web.tunnel_helper", fromlist=["load_config"]).load_config(),
    )


@app.route("/settings/site", methods=["POST"])
@auth.login_required
def settings_site_save():
    config = settings_helper.load_site_config()
    config["site_name_ar"] = request.form.get("site_name_ar", "").strip()
    config["site_name_en"] = request.form.get("site_name_en", "").strip()
    config["company_name_ar"] = request.form.get("company_name_ar", "").strip()
    config["company_name_en"] = request.form.get("company_name_en", "").strip()
    config["company_address"] = request.form.get("company_address", "").strip()
    config["company_phone"] = request.form.get("company_phone", "").strip()
    config["company_email"] = request.form.get("company_email", "").strip()
    settings_helper.save_site_config(config)
    flash("✅ تم حفظ إعدادات الموقع", "success")
    return redirect(url_for("settings"))


@app.route("/settings/upload-logo", methods=["POST"])
@auth.login_required
def settings_upload_logo():
    file = request.files.get("logo")
    if not file or not file.filename:
        flash("❌ لم يتم اختيار ملف", "danger")
        return redirect(url_for("settings"))
    uploads_dir = settings_helper.get_uploads_dir()
    ext = Path(file.filename).suffix.lower()
    filename = f"logo{ext}"
    file.save(str(uploads_dir / filename))
    config = settings_helper.load_site_config()
    config["logo_filename"] = filename
    settings_helper.save_site_config(config)
    flash("✅ تم رفع الشعار", "success")
    return redirect(url_for("settings"))


@app.route("/settings/upload-favicon", methods=["POST"])
@auth.login_required
def settings_upload_favicon():
    file = request.files.get("favicon")
    if not file or not file.filename:
        flash("❌ لم يتم اختيار ملف", "danger")
        return redirect(url_for("settings"))
    uploads_dir = settings_helper.get_uploads_dir()
    ext = Path(file.filename).suffix.lower()
    filename = f"favicon{ext}"
    file.save(str(uploads_dir / filename))
    config = settings_helper.load_site_config()
    config["favicon_filename"] = filename
    settings_helper.save_site_config(config)
    flash("✅ تم رفع الأيقونة", "success")
    return redirect(url_for("settings"))


@app.route("/settings/slack", methods=["POST"])
@auth.login_required
def settings_slack_save():
    from config import slack_notifier
    config = slack_notifier.load_config() or {}
    config["enabled"] = "slack_enabled" in request.form
    config["webhook_url"] = request.form.get("slack_webhook", "").strip()
    config["notify_on"] = request.form.get("slack_notify_on", "failure")
    slack_notifier.save_config(config)
    flash("✅ تم حفظ إعدادات Slack", "success")
    return redirect(url_for("settings"))


# ==================== Users ====================
@app.route("/users")
@auth.login_required
def users():
    if not auth.is_admin():
        flash("❌ غير مصرح لك بالوصول", "danger")
        return redirect(url_for("index"))
    all_users = settings_helper.load_users()
    return render_template("users.html", users=all_users)


@app.route("/users/add", methods=["POST"])
@auth.login_required
def users_add():
    if not auth.is_admin():
        return redirect(url_for("index"))
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    full_name = request.form.get("full_name", "").strip()
    role = request.form.get("role", "user")
    if not username or not password:
        flash("❌ اسم المستخدم وكلمة المرور مطلوبان", "danger")
        return redirect(url_for("users"))
    success, result = settings_helper.add_user(username, password, full_name, role)
    if success:
        flash(f"✅ تم إضافة المستخدم: {username}", "success")
    else:
        flash(f"❌ {result}", "danger")
    return redirect(url_for("users"))


@app.route("/users/delete/<user_id>", methods=["POST"])
@auth.login_required
def users_delete(user_id):
    if not auth.is_admin():
        return redirect(url_for("index"))
    if user_id == session.get("user_id"):
        flash("❌ لا يمكنك حذف حسابك الحالي", "danger")
        return redirect(url_for("users"))
    if settings_helper.delete_user(user_id):
        flash("✅ تم حذف المستخدم", "success")
    else:
        flash("❌ فشل الحذف", "danger")
    return redirect(url_for("users"))


# ==================== Screenshots ====================
@app.route("/screenshots/<filename>")
def serve_screenshot(filename):
    return send_from_directory(str(Config.SCREENSHOTS_DIR), filename)



@app.route("/live")
@auth.login_required
def live_viewer():
    from web import tunnel_helper
    config = tunnel_helper.load_config()
    vnc_full_url = tunnel_helper.get_vnc_full_url()
    return render_template(
        "live_viewer.html",
        vnc_full_url=vnc_full_url,
        tunnel_config=config,
    )


@app.route("/api/grid-status")
@auth.login_required
def grid_status():
    import requests
    try:
        r = requests.get(f"{os.getenv('SELENIUM_HUB', 'http://localhost:4444')}/status", timeout=3)
        data = r.json()
        return jsonify({
            "success": True,
            "ready": data.get("value", {}).get("ready", False),
            "nodes": len(data.get("value", {}).get("nodes", [])),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)[:100]})


# ==================== Export ====================
@app.route("/export/json")
@auth.login_required
def export_json():
    summaries = data_helper.load_summaries()
    content = export_helper.export_to_json(summaries)
    filename = f"erp_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return Response(content, mimetype="application/json",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


@app.route("/export/csv")
@auth.login_required
def export_csv():
    summaries = data_helper.load_summaries()
    content = export_helper.export_to_csv(summaries)
    filename = f"erp_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(content, mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


@app.route("/export/excel")
@auth.login_required
def export_excel():
    summaries = data_helper.load_summaries()
    content = export_helper.export_to_excel(summaries)
    filename = f"erp_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return Response(content,
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


@app.route("/export/pdf")
@auth.login_required
def export_pdf():
    summaries = data_helper.load_summaries()
    content = export_helper.export_to_pdf(summaries)
    filename = f"erp_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return Response(content, mimetype="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


# ==================== API ====================
@app.route("/api/run-test", methods=["POST"])
@auth.login_required
def run_test():
    data = request.get_json() or {}
    test_path = data.get("test_path", "").strip()
    test_name = data.get("test_name", "اختبار").strip()

    if not test_path:
        return jsonify({"success": False, "error": "test_path required"}), 400

    task_id = f"run_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    qm = get_qm()
    result = qm.add(task_id, test_path, test_name)

    return jsonify({
        "success": True,
        "task_id": task_id,
        "queued": result["queued"],
        "position": result["position"],
    })


@app.route("/api/status/<task_id>")
@auth.login_required
def task_status(task_id):
    qm = get_qm()
    status = qm.get_status()

    if status["running"] and status["running"]["task_id"] == task_id:
        return jsonify({
            "status": status["running"].get("status", "running"),
            "running": True,
            "queue_length": status["queue_length"],
        })

    for i, task in enumerate(status["queue"]):
        if task["task_id"] == task_id:
            return jsonify({
                "status": "queued",
                "queued": True,
                "position": i + 1,
                "queue_length": status["queue_length"],
            })

    if (Config.RESULTS_DIR / f"summary_{task_id}.json").exists():
        return jsonify({"status": "completed", "running": False})

    return jsonify({"status": "unknown", "running": False})


@app.route("/api/queue")
@auth.login_required
def queue_status():
    qm = get_qm()
    return jsonify(qm.get_status())


@app.route("/api/stop", methods=["POST"])
@auth.login_required
def stop_test():
    qm = get_qm()
    if qm.stop_current():
        return jsonify({"success": True, "message": "Test stopping"})
    return jsonify({"success": False, "message": "No test running"})


# ==================== Helper ====================
def _load_json(path):
    p = Path(path)
    if not p.exists():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (UnicodeDecodeError, json.JSONDecodeError):
        try:
            with open(p, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception:
            return {}
    except Exception:
        return {}

# ==================== Email Settings ====================
@app.route("/settings/email", methods=["POST"])
@auth.login_required
def settings_email_save():
    recipients_raw = request.form.get("recipients", "").strip()
    recipients = [r.strip() for r in recipients_raw.replace("\n", ",").split(",") if r.strip()]

    config = {
        "enabled": "email_enabled" in request.form,
        "smtp_host": request.form.get("smtp_host", "").strip(),
        "smtp_port": int(request.form.get("smtp_port", 587) or 587),
        "sender_email": request.form.get("sender_email", "").strip(),
        "sender_password": request.form.get("sender_password", "").strip(),
        "recipients": recipients,
        "notify_on": request.form.get("notify_on", "failure"),
    }

    settings_helper.save_email_config(config)
    flash("Email settings saved", "success")
    return redirect(url_for("settings"))


@app.route("/settings/email/test", methods=["POST"])
@auth.login_required
def settings_email_test():
    from config import emailer as email_module
    to_email = request.form.get("test_email", "").strip()
    if not to_email:
        return jsonify({"success": False, "message": "Enter target email"})
    success, message = email_module.send_test_email(to_email)
    return jsonify({"success": success, "message": message})



# ==================== Test Sites (Profiles) ====================
@app.route("/settings/test-sites", methods=["POST"])
@auth.login_required
def settings_test_sites_save():
    from web import test_sites_helper as tsh
    profile_id = request.form.get("profile_id", "").strip()
    name = request.form.get("name", "").strip()
    base_url = request.form.get("base_url", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    notes = request.form.get("notes", "").strip()

    if not name or not base_url or not username:
        flash("الاسم والرابط واسم المستخدم مطلوبين", "danger")
        return redirect(url_for("settings") + "#test-sites")

    if profile_id:
        success, result = tsh.update_profile(
            profile_id,
            name=name, base_url=base_url,
            username=username, password=password, notes=notes
        )
        flash("تم تحديث الموقع" if success else "فشل التحديث",
              "success" if success else "danger")
    else:
        success, result = tsh.add_profile(
            name=name, base_url=base_url,
            username=username, password=password, notes=notes
        )
        flash("تم إضافة الموقع: " + name if success else "فشل الإضافة",
              "success" if success else "danger")

    return redirect(url_for("settings") + "#test-sites")


@app.route("/settings/test-sites/delete/<profile_id>", methods=["POST"])
@auth.login_required
def settings_test_sites_delete(profile_id):
    from web import test_sites_helper as tsh
    success, message = tsh.delete_profile(profile_id)
    flash("تم حذف الموقع" if success else message,
          "success" if success else "danger")
    return redirect(url_for("settings") + "#test-sites")


@app.route("/settings/test-sites/activate/<profile_id>", methods=["POST"])
@auth.login_required
def settings_test_sites_activate(profile_id):
    from web import test_sites_helper as tsh
    success = tsh.set_active_profile(profile_id)
    flash("تم تفعيل الموقع" if success else "فشل التفعيل",
          "success" if success else "danger")
    return redirect(url_for("settings") + "#test-sites")


# ==================== End Test Sites ====================



# ==================== Tunnel Settings ====================
@app.route("/settings/tunnel", methods=["POST"])
@auth.login_required
def tunnel_settings_save():
    from web import tunnel_helper
    flask_url = request.form.get("flask_url", "").strip()
    vnc_url = request.form.get("vnc_url", "").strip()
    provider = request.form.get("provider", "cloudflare").strip()

    tunnel_helper.save_config(flask_url, vnc_url, provider)
    flash("✅ تم حفظ إعدادات Tunnel", "success")
    return redirect(url_for("settings") + "#tunnel")


@app.route("/settings/tunnel/reload", methods=["POST"])
@auth.login_required
def tunnel_settings_reload():
    """يعيد قراءة الروابط من config/tunnel_config.json"""
    flash("✅ تم إعادة تحميل الإعدادات", "success")
    return redirect(url_for("settings") + "#tunnel")


@app.route("/api/tunnel-info")
@auth.login_required
def api_tunnel_info():
    from web import tunnel_helper
    config = tunnel_helper.load_config()
    config["vnc_full_url"] = tunnel_helper.get_vnc_full_url()
    return jsonify(config)


# ==================== End Tunnel ====================

if __name__ == "__main__":
    print("=" * 60)
    print("  ERP Test Automation - Web Interface v4.2")
    print("=" * 60)
    print(f"  Open: http://localhost:5000")
    print(f"  Login: admin / password")
    print("=" * 60)
    import os
port = int(os.environ.get("PORT", 5000))
debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
app.run(host="0.0.0.0", port=port, debug=debug_mode, use_reloader=False)






