import os
import csv
import json
from datetime import datetime
from analyzer import analyze_log, take_action

log_folder = os.path.join(os.path.dirname(__file__), "..", "data")

# MTTR lookup table — maps issue type to (without_ai, with_ai) in minutes
MTTR_TABLE = {
    "Flaky Test":          (10, 2),
    "Dependency Issue":    (12, 3),
    "Infrastructure Issue":(15, 4),
    "Code Defect":         (20, 7),
    "Configuration Error": (18, 5),
    "Timeout":             (8,  2),
    "Unknown":             (25, 10),
}


def process_file(filename):
    file_path = os.path.join(log_folder, filename)

    with open(file_path, "r") as file:
        log = file.read()

    result = analyze_log(log)

    print(f"\n{'='*50}")
    print(f"📄  FILE     : {filename}")
    print(f"{'='*50}")
    print(f"   Type      : {result['type']}")
    print(f"   Category  : {result['category']}")
    print(f"   Reason    : {result['reason']}")
    print(f"   Fix       : {result['fix']}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Source    : {result.get('source', 'regex')}")

    result = take_action(result)

    actions = result.get("action_taken", [])
    if actions:
        print(f"   Action    : {actions[0]}")

    # Save result to analysis_log.csv for dashboard + accuracy report
    _save_to_csv(filename, result)

    return result


def _save_to_csv(filename, result):
    csv_path = "analysis_log.csv"
    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "filename", "type", "category",
            "reason", "fix", "confidence", "source", "action_taken"
        ])
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename":     filename,
            "type":         result.get("type", ""),
            "category":     result.get("category", ""),
            "reason":       result.get("reason", ""),
            "fix":          result.get("fix", ""),
            "confidence":   result.get("confidence", ""),
            "source":       result.get("source", "regex"),
            "action_taken": str(result.get("action_taken", []))
        })


def analyze_all_logs():
    total = 0
    stats = {}
    total_time_without_ai = 0
    total_time_with_ai = 0
    confidence_counts = {"High": 0, "Medium": 0, "Low": 0}
    source_counts = {"regex": 0, "llm": 0}

    print("\n🚀 Starting AI DevOps Agent Analysis...")
    print(f"   Scanning folder: {os.path.abspath(log_folder)}\n")

    log_files = [f for f in os.listdir(log_folder) if f.endswith(".txt")]

    if not log_files:
        print("❌ No .txt log files found in data/ folder")
        return

    for filename in sorted(log_files):
        result = process_file(filename)
        issue_type = result["type"]

        # Failure distribution
        stats[issue_type] = stats.get(issue_type, 0) + 1
        total += 1

        # Confidence distribution
        conf = result.get("confidence", "Low")
        confidence_counts[conf] = confidence_counts.get(conf, 0) + 1

        # Source distribution
        src = result.get("source", "regex")
        source_counts[src] = source_counts.get(src, 0) + 1

        # MTTR
        without_ai, with_ai = MTTR_TABLE.get(issue_type, (15, 6))
        total_time_without_ai += without_ai
        total_time_with_ai += with_ai

    # ── ANALYTICS REPORT ──────────────────────────────────────────────────
    print("\n")
    print("📊  ══════════════════════════════════════")
    print("         ANALYTICS REPORT")
    print("    ══════════════════════════════════════")
    print(f"   Total Logs Analyzed : {total}")
    print(f"   Regex Classified    : {source_counts.get('regex', 0)}")
    print(f"   LLM Classified      : {source_counts.get('llm', 0)}")

    print("\n   Failure Distribution:")
    print("   " + "-"*36)
    for issue_type, count in sorted(stats.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"   {issue_type:<25} {count:>2}  {bar}")

    print("\n   Confidence Breakdown:")
    print(f"   High   : {confidence_counts['High']}")
    print(f"   Medium : {confidence_counts['Medium']}")
    print(f"   Low    : {confidence_counts['Low']}")

    if stats:
        most_common = max(stats, key=stats.get)
        print(f"\n   Most Frequent Issue : {most_common}")

    # ── MTTR REPORT ───────────────────────────────────────────────────────
    avg_without_ai = total_time_without_ai / total
    avg_with_ai    = total_time_with_ai    / total
    improvement    = ((avg_without_ai - avg_with_ai) / avg_without_ai) * 100
    time_saved     = avg_without_ai - avg_with_ai

    print("\n⏱️  ══════════════════════════════════════")
    print("            MTTR REPORT")
    print("    ══════════════════════════════════════")
    print(f"   Avg MTTR without AI : {avg_without_ai:.1f} min")
    print(f"   Avg MTTR with AI    : {avg_with_ai:.1f} min")
    print(f"   Time Saved per Issue: {time_saved:.1f} min")
    print(f"   Improvement         : {improvement:.1f}% faster resolution")

    # ── SAVE SUMMARY JSON ─────────────────────────────────────────────────
    summary = {
        "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_logs":      total,
        "failure_distribution": stats,
        "confidence_breakdown": confidence_counts,
        "source_counts":   source_counts,
        "mttr": {
            "without_ai":  round(avg_without_ai, 2),
            "with_ai":     round(avg_with_ai, 2),
            "improvement": round(improvement, 2)
        }
    }
    with open("summary_report.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n✅  Results saved to analysis_log.csv")
    print("✅  Summary saved to summary_report.json")
    print("    (Use these files in your Streamlit dashboard)")


def analyze_single_log():
    print("\n📂 Available log files:")
    files = [f for f in os.listdir(log_folder) if f.endswith(".txt")]

    if not files:
        print("❌ No log files found in data/ folder")
        return

    for i, f in enumerate(sorted(files), 1):
        print(f"   {i}. {f}")

    filename = input("\nEnter log file name (e.g., log1.txt): ").strip()

    if not os.path.exists(os.path.join(log_folder, filename)):
        print(f"❌ File '{filename}' not found in data/ folder")
        return

    process_file(filename)


def show_saved_results():
    csv_path = "analysis_log.csv"

    if not os.path.exists(csv_path):
        print("❌ No saved results yet. Run analysis first.")
        return

    print("\n📋 ══════════════════════════════════════")
    print("         SAVED ANALYSIS RESULTS")
    print("    ══════════════════════════════════════")

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"   Total records: {len(rows)}\n")
    print(f"   {'Timestamp':<20} {'File':<12} {'Type':<25} {'Conf':<8} {'Source'}")
    print("   " + "-"*80)

    for row in rows[-20:]:  # show last 20
        print(f"   {row['timestamp']:<20} {row['filename']:<12} "
              f"{row['type']:<25} {row['confidence']:<8} {row['source']}")


def main():
    while True:
        print("\n")
        print("╔══════════════════════════════════╗")
        print("║     🤖  AI DevOps Agent          ║")
        print("║     Jenkins Pipeline Analyzer    ║")
        print("╠══════════════════════════════════╣")
        print("║  1. Analyze all logs             ║")
        print("║  2. Analyze single log           ║")
        print("║  3. View saved results           ║")
        print("║  4. Exit                         ║")
        print("╚══════════════════════════════════╝")

        choice = input("   Enter your choice (1-4): ").strip()

        if choice == "1":
            analyze_all_logs()

        elif choice == "2":
            analyze_single_log()

        elif choice == "3":
            show_saved_results()

        elif choice == "4":
            print("\n👋 Exiting AI DevOps Agent. Goodbye!\n")
            break

        else:
            print("❌ Invalid choice. Enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()