import os
import csv
import json
import urllib.request
import urllib.parse
import urllib.error

BOT_TOKEN = os.environ["BOT_TOKEN"]
SSC_CHAT_ID = os.environ["SSC_CHAT_ID"]

QUESTIONS_PER_RUN = 8
CSV_FILE = "ssc_8_3.csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def send_quiz(chat_id, question, options, correct_answer, explanation):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"

    data = {
        "chat_id": chat_id,
        "question": question[:300],
        "options": json.dumps(options, ensure_ascii=False),
        "type": "quiz",
        "correct_option_id": correct_answer,
        "is_anonymous": True,
        "explanation": explanation[:200]
    }

    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode("utf-8"),
        method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))

            if result.get("ok"):
                print("Poll sent successfully.")
                return True

            print("Telegram rejected the poll:")
            print(result)
            return False

    except urllib.error.HTTPError as e:
        error_message = e.read().decode("utf-8")
        print("Telegram API Error:")
        print(error_message)
        return False

    except Exception as e:
        print("Unexpected Error:")
        print(str(e))
        return False


def send_from_csv(filename, chat_id):

    filepath = os.path.join(BASE_DIR, filename)

    print(f"Reading file: {filename}")

    try:
        with open(filepath, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

    except FileNotFoundError:
        print(f"CSV file not found: {filename}")
        return

    if not rows:
        print("CSV file is empty.")
        return

    selected = rows[:QUESTIONS_PER_RUN]

    print(f"Total questions selected: {len(selected)}")
    print("--------------------------------")

    success_count = 0

    for number, row in enumerate(selected, start=1):

        try:
            question = row["question"].strip()

            options = [
                row["option1"].strip(),
                row["option2"].strip(),
                row["option3"].strip(),
                row["option4"].strip()
            ]

            answer = int(row["answer"].strip())

            if answer not in [1, 2, 3, 4]:
                print(f"Question {number}: Invalid answer number.")
                continue

            correct_answer = answer - 1

            explanation = row["explanation"].strip()

            if not question:
                print(f"Question {number}: Question is empty.")
                continue

            if any(not option for option in options):
                print(f"Question {number}: One or more options are empty.")
                continue

            print(f"Sending question {number}...")

            success = send_quiz(
                chat_id,
                question,
                options,
                correct_answer,
                explanation
            )

            if success:
                success_count += 1

        except Exception as e:
            print(f"Question {number} skipped: {str(e)}")

    print("--------------------------------")
    print(f"Quiz completed: {success_count}/{len(selected)} polls sent.")


print("================================")
print("Starting SSC Quiz Bot")
print("================================")

send_from_csv(
    CSV_FILE,
    SSC_CHAT_ID
)

print("================================")
print("SSC Quiz Bot Finished")
print("================================")
