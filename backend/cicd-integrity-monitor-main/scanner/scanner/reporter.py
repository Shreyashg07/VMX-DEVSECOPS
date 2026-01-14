import json
import os
import requests
from rich.console import Console
from rich.table import Table
from jinja2 import Template

# ------------------------------------------------------------------------------------
# HTML TEMPLATE (card-style UI + attack_type support)
# ------------------------------------------------------------------------------------
HTML_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title>CI/CD Scan Report</title>
<style>
    body {
        background: #0a192f;
        color: #ccd6f6;
        font-family: 'Segoe UI', sans-serif;
        margin: 0;
        padding: 30px;
    }
    h1 {
        text-align: center;
        color: #64ffda;
        margin-bottom: 40px;
        font-size: 32px;
    }
    .report-meta {
        background: #112240;
        border: 1px solid #233554;
        padding: 18px 24px;
        border-radius: 10px;
        margin-bottom: 40px;
    }
    .report-meta b {
        color: #64ffda;
    }
    .card {
        background: #112240;
        border: 1px solid #233554;
        border-radius: 10px;
        margin-bottom: 25px;
        padding: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        color: #fff;
        font-weight: bold;
    }
    .low { background: #3b82f6; }
    .medium { background: #f59e0b; }
    .high { background: #ef4444; }
    pre {
        background: #0a192f;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #233554;
        overflow-x: auto;
        color: #64ffda;
    }
</style>
</head>
<body>

<h1>CI/CD Integrity Scan Report</h1>

<div class="report-meta">
    <p><b>Repository Path:</b> {{ meta.path }}</p>
    <p><b>Overall Score:</b> {{ score }}</p>
    <p><b>Action:</b>
        {% if action == "fail" %}
            <span class="badge high">FAIL</span>
        {% elif action == "warn" %}
            <span class="badge medium">WARN</span>
        {% else %}
            <span class="badge low">ALLOW</span>
        {% endif %}
    </p>
</div>

{% for f in findings %}
<div class="card">
    <h3 class="{% if f.score >= 7 %}high{% elif f.score >= 4 %}medium{% else %}low{% endif %}">
        {{ f.file }}
    </h3>
    <p><b>Category:</b> {{ f.attack_type or "N/A" }}</p>
    <p><b>Threat %:</b> {{ "%.1f"|format(f.score * 10) }}%</p>
    <p><b>Detector:</b> {{ f.detector }}</p>
    <p><b>ID:</b> {{ f.id }}</p>

    {% if f.meta %}
    <pre>{{ f.meta | safe }}</pre>
    {% endif %}
</div>
{% endfor %}

</body>
</html>
"""

# ------------------------------------------------------------------------------------
# OPTIONAL AUTO-UPLOAD TO API
# ------------------------------------------------------------------------------------
def _post_to_api(json_file, html_file):
    api = os.environ.get("REPORT_API_URL")
    if not api:
        return

    try:
        with open(json_file, "r", encoding="utf-8") as jf:
            payload = json.load(jf)

        try:
            with open(html_file, "r", encoding="utf-8") as hf:
                payload["report_html"] = hf.read()
        except Exception:
            payload["report_html"] = None

        url = api.rstrip("/") + "/incidents"
        requests.post(url, json=payload, timeout=10)

    except Exception as e:
        print(f"[WARN] Failed to upload report to API: {e}")


# ------------------------------------------------------------------------------------
# REPORTER CLASS
# ------------------------------------------------------------------------------------
class Reporter:

    @staticmethod
    def print_console(result):
        console = Console()
        console.print("[bold cyan]CI/CD Integrity Scanner Report[/bold cyan]\n")

        console.print(f"[bold]Path:[/bold] {result['meta']['path']}")
        console.print(
            f"[bold]Score:[/bold] {result['score']}   "
            f"[bold]Action:[/bold] {result['action']}\n"
        )

        findings = result.get("findings", [])

        normal = [f for f in findings if not f["detector"].startswith("ml_")]
        if normal:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Detector")
            table.add_column("ID")
            table.add_column("File")
            table.add_column("Score")
            table.add_column("Description")

            for f in normal:
                table.add_row(
                    f["detector"],
                    f["id"],
                    f["file"],
                    str(f["score"]),
                    f["description"],
                )

            console.print(table)

    @staticmethod
    def write_reports(result, out_json="report.json", out_html="report.html"):
        """
        Writes reports exactly where CLI tells it to.
        """
        out_json_path = os.path.abspath(out_json)
        out_html_path = os.path.abspath(out_html)

        os.makedirs(os.path.dirname(out_json_path), exist_ok=True)

        # Write JSON
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        # Generate HTML
        html = Template(HTML_TEMPLATE).render(
            meta=result["meta"],
            score=result["score"],
            action=result["action"],
            findings=result["findings"],
        )

        with open(out_html_path, "w", encoding="utf-8") as f:
            f.write(html)

        # Optional API upload
        _post_to_api(out_json_path, out_html_path)

        print(
            "[INFO] Reports written to:\n"
            f"{out_json_path}\n{out_html_path}"
        )

        return out_json_path, out_html_path
