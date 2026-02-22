from pathlib import Path
import json
BASE_DIR = Path(__file__).resolve().parent
TASKS_FILE_TXT = BASE_DIR / "tasks.txt"
TASKS_FILE_JSON = BASE_DIR / "tasks.json"


def tasks_txt_to_json():
    with open(TASKS_FILE_TXT, "r", encoding="utf-8") as f:
        tasks_list = f.readlines()
    tasks = []
    for line in tasks_list:
        if line.startswith("[ ]"):
            done = False
            line = line.replace("[ ] ", "")
        elif line.startswith("[X]"):
            done = True
            line = line.replace("[X] ", "")
        else:
            print("Txt file corrupted")
            return
        tasks.append({
            "text": line.strip(),
            "done": done
        })
    save_tasks(tasks)
    old_file = BASE_DIR / "tasks_old.txt"
    if old_file.exists():
        old_file.unlink()
    TASKS_FILE_TXT.rename(old_file)
    print("Migration complete.")


def load_tasks():
    if not TASKS_FILE_JSON.exists() or TASKS_FILE_JSON.stat().st_size == 0:
        return []
    try:
        with open(TASKS_FILE_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("tasks.json is corrupted (invalid JSON).")
        return []


def save_tasks(tasks):
    with open(TASKS_FILE_JSON, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def validate_input(the_input, len_tasks):
    if the_input.isdigit():
        the_input = int(the_input) - 1
        if not (0 <= the_input < len_tasks):
            print("Wrong index!\n")
            return None
        return the_input
    else:
        print("Wrong input!\n")
        return None


def filter_tasks_by_done(tasks, done_value: bool):
    return [(i, task) for i, task in enumerate(tasks) if task["done"] == done_value]


def search_tasks_by_text(tasks, query: str):
    query = query.strip().lower()
    return [(i, task) for i, task in enumerate(tasks) if query in task["text"].lower()]


def print_tasks_subset(items):
    if not items:
        return
    for index, task in items:
        mark = "[X]" if task["done"] else "[ ]"
        print(f"{index+1}. {mark} {task['text']}")


def pick_task_index(tasks, prompt: str):
    if not tasks:
        print("No tasks")
        return None
    print_tasks(tasks)
    user_input = input(prompt)
    return validate_input(user_input, len(tasks))


def menu():
    options = [add_task, print_tasks, mark_done, delete_task,
               toggle_task, show_done_tasks, show_undone_tasks, search_tasks]
    while True:
        tasks = load_tasks()
        option_pick = input("WHAT TO DO\n"
                            "1. Add task\n"
                            "2. Show tasks\n"
                            "3. Mark task as done\n"
                            "4. Delete task\n"
                            "5. Toggle task done/undone\n"
                            "6. Show only done\n"
                            "7. Show only undone\n"
                            "8. Search tasks\n"
                            "9. Exit\n\n"
                            "Choose: ")
        if option_pick == "9":
            break
        elif option_pick.isdigit() and 1 <= int(option_pick) <= len(options):
            options[int(option_pick)-1](tasks)
        else:
            print("\nWrong input!\nCorrect form: 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8 / 9\n")


def add_task(tasks):
    text = input("Task: ").strip()
    if not text:
        print("Task cannot be empty")
        return
    tasks.append({
        "text": text,
        "done": False
    })
    save_tasks(tasks)


def print_tasks(tasks):
    items = list(enumerate(tasks))  # (index, task)
    if not items:
        print("No tasks")
        return
    print_tasks_subset(items)


def mark_done(tasks):
    index = pick_task_index(tasks, "Delete: ")
    if index is None:
        return
    elif tasks[index]["done"]:
        print("Task already done")
        return
    tasks[index]["done"] = True
    save_tasks(tasks)
    print_tasks(tasks)


def delete_task(tasks):
    index = pick_task_index(tasks, "Delete: ")
    if index is None:
        return
    tasks.pop(index)
    save_tasks(tasks)
    print_tasks(tasks)


def toggle_task(tasks):
    index = pick_task_index(tasks, "Delete: ")
    if index is None:
        return
    tasks[index]["done"] = not tasks[index]["done"]
    save_tasks(tasks)
    print_tasks(tasks)


def show_done_tasks(tasks):
    done = filter_tasks_by_done(tasks, True)
    if not done:
        print("You have no done tasks!")
        return
    print_tasks(done)


def show_undone_tasks(tasks):
    undone = filter_tasks_by_done(tasks, False)
    if not undone:
        print("You have no undone tasks!")
        return
    print_tasks(undone)


def search_tasks(tasks):
    query = input("Find task: ")
    results = search_tasks_by_text(tasks, query)
    if not results:
        print("No matching tasks.")
        return
    print_tasks(results)


if TASKS_FILE_TXT.exists() and (not TASKS_FILE_JSON.exists() or TASKS_FILE_JSON.stat().st_size == 0):
    tasks_txt_to_json()

menu()
