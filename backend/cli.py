import os
from analyzer import analyze_log, take_action

log_folder = "data"


def process_file(filename):
    file_path = os.path.join(log_folder, filename)

    with open(file_path, "r") as file:
        log = file.read()

    result = analyze_log(log)

    print(f"\n📄 {filename}")
    print("Type:", result["type"])
    print("Category:", result["category"])
    print("Reason:", result["reason"])
    print("Fix:", result["fix"])
    print("Confidence:", result["confidence"])

    take_action(result)

    return result["type"]


def analyze_all_logs():
    total = 0
    stats = {}

    total_time_without_ai = 0
    total_time_with_ai = 0

    print("\n🚀 Starting AI DevOps Agent Analysis...\n")

    for filename in os.listdir(log_folder):
        if filename.endswith(".txt"):

            issue_type = process_file(filename)

            # 🔥 Analytics
            stats[issue_type] = stats.get(issue_type, 0) + 1
            total += 1

            # 🔥 MTTR Simulation
            if issue_type == "Dependency Issue":
                without_ai = 12
                with_ai = 3
            elif issue_type == "Test Failure":
                without_ai = 10
                with_ai = 4
            elif issue_type == "Timeout Error":
                without_ai = 8
                with_ai = 3
            else:
                without_ai = 15
                with_ai = 6

            total_time_without_ai += without_ai
            total_time_with_ai += with_ai

    # 🔥 ANALYTICS REPORT
    print("\n📊 ===== ANALYTICS REPORT =====")
    print(f"Total Logs: {total}")

    print("\nFailure Distribution:")
    for key, value in stats.items():
        print(f"{key}: {value}")

    if stats:
        most_common = max(stats, key=stats.get)
        print(f"\n🔥 Most Frequent Issue: {most_common}")

    # 🔥 MTTR REPORT
    if total > 0:
        avg_without_ai = total_time_without_ai / total
        avg_with_ai = total_time_with_ai / total

        improvement = ((avg_without_ai - avg_with_ai) / avg_without_ai) * 100

        print("\n⏱️ ===== MTTR REPORT =====")
        print(f"Avg MTTR without AI: {avg_without_ai:.2f} minutes")
        print(f"Avg MTTR with AI: {avg_with_ai:.2f} minutes")
        print(f"🚀 Improvement: {improvement:.2f}% faster resolution")


def analyze_single_log():
    filename = input("Enter log file name (e.g., log1.txt): ")

    if not os.path.exists(os.path.join(log_folder, filename)):
        print("❌ File not found")
        return

    process_file(filename)


def main():
    while True:
        print("\n===== 🤖 AI DevOps Agent =====")
        print("1. Analyze all logs")
        print("2. Analyze single log")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            analyze_all_logs()

        elif choice == "2":
            analyze_single_log()

        elif choice == "3":
            print("👋 Exiting Agent")
            break

        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()