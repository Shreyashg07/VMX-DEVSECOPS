#!/usr/bin/env bash
set -e
REPO_PATH=${1:-"."}
python -m scanner.scanner.cli "$REPO_PATH" --output "./scan_report.json" --html "./scan_report.html"
echo "JSON report: ./scan_report.json"
echo "HTML report: ./scan_report.html"
