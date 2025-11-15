import os
import json
from datetime import datetime
import requests


class AlertManager:
    """Manages alerts and notifications for pipeline events"""

    def __init__(self, webhook_url=None):
        """Initialize AlertManager with optional webhook URL"""
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")

    def send_slack_alert(self, title, message, severity="info"):
        """Send alert to Slack webhook"""
        color_map = {"info": "#36a64f", "warning": "#ff9900", "error": "#ff0000", "critical": "#8b0000"}
        payload = {
            "attachments": [
                {
                    "color": color_map.get(severity, "#36a64f"),
                    "title": title,
                    "text": message,
                    "footer": "DataOps Monitoring",
                    "ts": int(datetime.now().timestamp()),
                }
            ]
        }

        # For testing without Slack webhook
        print("=== ALERT TRIGGERED ===")
        print(f"Severity: {severity}")
        print(f"Title: {title}")
        print(f"Message: {message}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print("======================")

        if not self.webhook_url:
            print("⚠️  No Slack webhook configured. Alert only printed to console.")
            return True

        try:
            response = requests.post(
                self.webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=10
            )
            print(f"Slack API Response: Status={response.status_code}, " f"Body={response.text}")
            if response.status_code == 200:
                print("Alert successfully sent to Slack!")
                return True
            else:
                print(f"Slack returned error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to send alert: {e}")
            return False

    def alert_pipeline_failure(self, dag_id, task_id, error_message):
        """Send alert for pipeline failure"""
        title = f"Pipeline Failure: {dag_id}"
        message = f"Task {task_id} failed\n\nError: {error_message}"
        return self.send_slack_alert(title, message, "error")

    def alert_test_failure(self, test_name, failure_count):
        """Send alert for test failure"""
        title = "Data Quality Alert"
        message = f"Test {test_name} failed\n\nFailures: {failure_count}"
        return self.send_slack_alert(title, message, "warning")

    def alert_slow_pipeline(self, dag_id, execution_time, threshold):
        """Send alert for slow pipeline execution"""
        title = f"Slow Pipeline: {dag_id}"
        message = f"Execution time: {execution_time:.2f}s " f"(threshold: {threshold}s)"
        return self.send_slack_alert(title, message, "warning")
