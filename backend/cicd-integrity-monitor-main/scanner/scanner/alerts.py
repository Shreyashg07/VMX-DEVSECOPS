# scanner/scanner/alerts.py
import os
import requests
import smtplib
from email.mime.text import MIMEText

class AlertManager:
    def __init__(self, config=None):
        config = config or {}
        # Only read Discord and SMTP/email config
        self.discord_url = config.get("DISCORD_WEBHOOK") or os.getenv("DISCORD_WEBHOOK")
        self.smtp_host = config.get("SMTP_HOST") or os.getenv("SMTP_HOST")
        self.smtp_port = int(config.get("SMTP_PORT") or os.getenv("SMTP_PORT") or 587)
        self.smtp_user = config.get("SMTP_USER") or os.getenv("SMTP_USER")
        self.smtp_pass = config.get("SMTP_PASS") or os.getenv("SMTP_PASS")
        self.email_from = config.get("EMAIL_FROM") or os.getenv("EMAIL_FROM")
        self.email_to = config.get("EMAIL_TO") or os.getenv("EMAIL_TO")  # comma-separated allowed

    def _send_discord(self, text: str):
        if not self.discord_url:
            # no webhook configured
            return {"ok": False, "reason": "no_discord_url"}
        payload = {"content": text}
        try:
            r = requests.post(self.discord_url, json=payload, timeout=8)
            return {"ok": r.status_code in (200, 204), "status_code": r.status_code, "text": r.text}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _send_email(self, subject: str, body: str):
        if not (self.smtp_host and self.email_to and self.email_from):
            return {"ok": False, "reason": "smtp_not_configured"}

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = self.email_to

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
                server.starttls()
                if self.smtp_user:
                    server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.email_from, [a.strip() for a in self.email_to.split(",")], msg.as_string())
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_alert(self, incident: dict):
        """
        Sends alerts for an incident. This implementation only sends if incident.action == "fail".
        Returns a dict with results from channels for debugging.
        """
        results = {"discord": None, "email": None}

        action = (incident.get("action") or "").lower()
        if action != "fail":
            # Only alert on fails (adjust if you want warn/high too)
            return {"skipped": True, "reason": "action_not_fail"}

        # Build a compact alert message
        meta = incident.get("meta", {})
        path = meta.get("path", "unknown")
        score = incident.get("risk_score", incident.get("score", "n/a"))
        level = incident.get("risk_level", "unknown")
        repo = incident.get("repo", "unknown")

        text = (
            f"**CI/CD Security Alert**\n"
            f"Repository / Path: `{path}`\n"
            f"Repo: {repo}\n"
            f"Risk Level: **{str(level).upper()}**\n"
            f"Risk Score: **{score}**\n"
            f"Action: **{action.upper()}**\n"
            f"Findings: {len(incident.get('findings', []))}\n\n"
            f"View details in dashboard (if available).\n"
        )

        # Discord
        results["discord"] = self._send_discord(text)

        # Email
        subject = f"[ALERT] CI/CD Risk: {str(level).upper()} ({score})"
        results["email"] = self._send_email(subject, text)

        return results
