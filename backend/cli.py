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

    return result["type"]   # 🔥 return type for analytics


def analyze_all_logs():
    total = 0
    stats = {}

    print("\n🔍 Analyzing all logs...\n")

    for filename in os.listdir(log_folder):
        if filename.endswith(".txt"):

            issue_type = process_file(filename)

            # 🔥 Collect stats
            stats[issue_type] = stats.get(issue_type, 0) + 1
            total += 1

    # 🔥 ANALYTICS REPORT
    print("\n📊 ===== ANALYTICS REPORT =====")
    print(f"Total Logs: {total}")

    print("\nFailure Distribution:")
    for key, value in stats.items():
        print(f"{key}: {value}")

    if stats:
        most_common = max(stats, key=stats.get)
        print(f"\n🔥 Most Frequent Issue: {most_common}")


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