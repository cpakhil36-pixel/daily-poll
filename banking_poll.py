
import os
import csv
import json
import urllib.request
import urllib.parse
import urllib.error

BOT_TOKEN = os.environ["BOT_TOKEN"]
BANKING_CHAT_ID = os.environ["BANKING_CHAT_ID"]

QUESTIONS_PER_RUN = 8
CSV_FILE = "Banking_11.csv"

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
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

            if result.get("ok"):
                print("Banking poll sent successfully.")
                return True

            print("Telegram rejected the poll:")
            print(result)
            return False

    except urllib.error.HTTPError as e:
        print("Telegram API Error:")
        print(e.read().decode("utf-8"))
        return False

    except Exception as e:
        print("Unexpected Error:")
        print(str(e))
        return False


def send_from_csv(filename, chat_id):
    filepath = os.path.join(BASE_DIR, filename)

    print(f"Reading file: {filename}")

    try:
        with open(
            filepath,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:
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
            question = (row.get("question") or "").strip()

            options = [
                (row.get("option1") or "").strip(),
                (row.get("option2") or "").strip(),
                (row.get("option3") or "").strip(),
                (row.get("option4") or "").strip()
            ]

            answer_text = (row.get("answer") or "").strip()
            explanation = (row.get("explanation") or "").strip()

            if not question:
                print(f"Question {number}: Question is empty.")
                continue

            if any(not option for option in options):
                print(f"Question {number}: An option is empty.")
                continue

            try:
                answer = int(answer_text)
            except ValueError:
                print(
                    f"Question {number}: "
                    "Answer must be 1, 2, 3, or 4."
                )
                continue

            if answer not in [1, 2, 3, 4]:
                print(f"Question {number}: Invalid answer number.")
                continue

            print(f"Sending Banking question {number}...")

            success = send_quiz(
                chat_id,
                question,
                options,
                answer - 1,
                explanation
            )

            if success:
                success_count += 1

        except Exception as e:
            print(f"Question {number} skipped: {str(e)}")

    print("--------------------------------")
    print(
        f"Banking Quiz completed: "
        f"{success_count}/{len(selected)} polls sent."
    )


if __name__ == "__main__":
    print("================================")
    print("Starting Banking Quiz Bot")
    print("================================")

    send_from_csv(CSV_FILE, BANKING_CHAT_ID)

    print("================================")
    print("Banking Quiz Bot Finished")
    print("================================")
