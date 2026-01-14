#!/usr/bin/env python3
import argparse
import json
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import sys

from scanner.scanner.engine import ScannerEngine
from scanner.scanner.reporter import Reporter
from scanner.scanner.uploader import upload_report


def main():
    parser = argparse.ArgumentParser(description="CI/CD Integrity Scanner CLI")

    # Main scan argument
    parser.add_argument("path", help="Path to repository or directory to scan")

    # Output locations (GitHub Action compatible)
    parser.add_argument(
        "--output",
        default="scan_reports/report.json",
        help="Output JSON report path"
    )
    parser.add_argument(
        "--html",
        default="scan_reports/report.html",
        help="Output HTML report path"
    )

    # Policy file
    parser.add_argument(
        "--policy",
        default="policies/default_policy.json",
        help="Policy rules file"
    )

    # Dashboard API integration
    parser.add_argument(
        "--api-url",
        help="Dashboard API URL (optional)",
        required=False
    )
    parser.add_argument(
        "--api-key",
        help="Dashboard API key (optional)",
        required=False
    )

    args = parser.parse_args()

    # Ensure scan_reports/ folder always exists
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Run Engine
    engine = ScannerEngine(policy_path=args.policy)
    result = engine.scan_path(args.path)

    # Console output
    Reporter.print_console(result)

    # Write local JSON + HTML output
    Reporter.write_reports(
        result,
        out_json=args.output,
        out_html=args.html
    )

    # Upload report to dashboard API (optional)
    if args.api_url:
        print(f"Uploading report to dashboard: {args.api_url}")
        try:
            upload_report(args.api_url, args.api_key, result)
            print("✓ Upload successful")
        except Exception as e:
            print(f"✗ Dashboard upload failed: {e}")

    # Handle exit codes AFTER upload
    action = result.get("action", "allow")

    if action == "fail":
        print("Action: FAIL — exiting with code 1")
        sys.exit(1)

    elif action == "warn":
        print("Action: WARN — exiting with code 0 (review findings)")
        sys.exit(0)

    print("Action: ALLOW — clean")
    sys.exit(0)


if __name__ == "__main__":
    main()
