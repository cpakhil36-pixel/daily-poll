import os
import csv
import json
import urllib.request
import urllib.parse
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]

SSC_CHAT_ID = os.environ["SSC_CHAT_ID"]
BANKING_CHAT_ID = os.environ["BANKING_CHAT_ID"]

QUESTIONS_PER_DAY = 15

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def send_quiz(chat_id, question, options, correct_answer):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"

    data = {
        "chat_id": chat_id,
        "question": question,
        "options": json.dumps(options, ensure_ascii=False),
        "type": "quiz",
        "correct_option_id": correct_answer,
        "is_anonymous": True
    }

    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode("utf-8"),
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        print(response.read().decode("utf-8"))


def send_from_csv(filename, chat_id):
    filepath = os.path.join(BASE_DIR, filename)

    print(f"Reading file: {filepath}")

    with open(filepath, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        print(f"{filename} is empty")
        return

    day_number = datetime.utcnow().date().toordinal()
    start = ((day_number - 1) * QUESTIONS_PER_DAY) % len(rows)

    selected = [
        rows[(start + i) % len(rows)]
        for i in range(QUESTIONS_PER_DAY)
    ]

    for row in selected:
        question = row["question"]

        options = [
            row["option1"],
            row["option2"],
            row["option3"],
            row["option4"]
        ]

        correct_answer = int(row["answer"]) - 1

        send_quiz(
            chat_id,
            question,
            options,
            correct_answer
        )


print("Starting Telegram Quiz Bot...")

print("Sending SSC polls...")
send_from_csv("ssc.csv", SSC_CHAT_ID)

print("Sending Banking polls...")
send_from_csv("banking.csv", BANKING_CHAT_ID)

print("All 30 polls sent successfully!")
