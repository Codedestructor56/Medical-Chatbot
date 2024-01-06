import csv
import random

def csv_to_text(input_csv_path, output_text_path):
    with open(input_csv_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)

    random.shuffle(rows)
    rows = rows[:2000]

    with open(output_text_path, 'w', encoding='utf-8') as text_file:
        text_file.write("This is a file which contains details about medical conditions, diagnoses, and histories.\n")
        for row in rows:
            question = row['question']
            answer = row['answer']
            source = row['source']

            text_file.write(f"Question: {question}\n")
            text_file.write(f"Answer: {answer}\n")
            text_file.write(f"The source for the previous passage of information is: {source}\n")

# Example usage
csv_to_text('data/medquad.csv', 'data/medquad.txt')
