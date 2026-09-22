import os
import csv
import json
import urllib.request
import urllib.parse

BOT_TOKEN = os.environ["BOT_TOKEN"]
SSC_CHAT_ID = os.environ["SSC_CHAT_ID"]

QUESTIONS_PER_RUN = 8

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def send_quiz(chat_id, question, options, correct_answer, explanation):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"

    data = {
        "chat_id": chat_id,
        "question": question,
        "options": json.dumps(options, ensure_ascii=False),
        "type": "quiz",
        "correct_option_id": correct_answer,
        "is_anonymous": True,
        "explanation": explanation
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
        print("CSV file is empty.")
        return

    selected = rows[:QUESTIONS_PER_RUN]

    for row in selected:

        question = row["question"]

        options = [
            row["option1"],
            row["option2"],
            row["option3"],
            row["option4"]
        ]

        correct_answer = int(row["answer"]) - 1

        explanation = row["explanation"]

        send_quiz(
            chat_id,
            question,
            options,
            correct_answer,
            explanation
        )


print("Starting SSC Quiz Bot...")

print("Sending 8 SSC polls...")

send_from_csv(
    "ssc_8_2.csv",
    SSC_CHAT_ID
)

print("All 8 SSC polls sent successfully!")
