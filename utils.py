import re
import json


def write_to_file(filename, text):
    with open(f"./files/{filename}", 'a') as file:
        file.write(text + '\n')


def get_content(filename):
    lines = []
    try:
        with open(f"./files/{filename}", 'r') as file:
            for line in file:
                lines.append(line.strip())
        return lines
    except FileNotFoundError:
        return []


def get_from_file_id_lines(file_name, line_identifier):
    lines = []
    pattern = fr"\[{line_identifier}\]"

    try:
        with open(f"./files/{file_name}", 'r') as file:
            for line in file:
                if re.search(pattern, line):
                    lines.append(line.strip())
    except FileNotFoundError:
        return []

    return lines


def load_config():
    try:
        with open("./config.json", 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "welcome": True,
            "questions": {
                "process": True,
                "question1": {
                    "process": True,
                    "delay_time": 5
                },
                "question2": {
                    "process": True,
                    "delay_time": 10
                },
                "question3": {
                    "process": True,
                    "delay_time": 15
                },
                "question4": {
                    "process": True,
                    "delay_time": 20
                },
                "question5": {
                    "process": True,
                    "delay_time": 25
                },
                "question6": {
                    "process": True,
                    "delay_time": 30
                },
                "question7": {
                    "process": True,
                    "delay_time": 30
                },
                "question8": {
                    "process": True,
                    "delay_time": 30
                },
                "question9": {
                    "process": True,
                    "delay_time": 30
                }
            },
            "pig": {
                "process": True,
                "duration": 100
            },
            "lottery": True,
            "eye": True
        }


def try_parse_int(value):
    try:
        return int(value), True
    except ValueError:
        return None, False


def split_separator_nick(nickname):
    if "|" in nickname:
        return nickname.split("|")[0]
    return nickname
