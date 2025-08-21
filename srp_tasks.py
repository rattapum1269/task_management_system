from abc import ABC, abstractmethod

VALID_PRIORITIES = {"low", "medium", "high"}

class TaskStorage(ABC):
    @abstractmethod
    def load_tasks(self):
        pass
    @abstractmethod
    def save_tasks(self, tasks):
        pass


class FileTaskStorage(TaskStorage):
    def __init__(self, filename="tasks.txt"):
        self.filename = filename

    def load_tasks(self):
        loaded_tasks = []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.rstrip("\n").split(",")
                    # รองรับทั้งรูปแบบเก่า (4 ฟิลด์) และใหม่ (5 ฟิลด์: id, desc, due, completed, priority)
                    if len(parts) == 4 or len(parts) == 5:
                        task_id = int(parts[0])
                        description = parts[1]
                        due_date = parts[2] if parts[2] != "None" and parts[2] != "" else None
                        completed = parts[3] == "True"
                        priority = (parts[4].lower() if len(parts) == 5 else "medium")
                        if priority not in VALID_PRIORITIES:
                            priority = "medium"
                        loaded_tasks.append(Task(task_id, description, due_date, completed, priority))
        except FileNotFoundError:
            print(f"No existing task file '{self.filename}' found. Starting fresh.")
        return loaded_tasks

    def save_tasks(self, tasks):
        with open(self.filename, "w", encoding="utf-8") as f:
            for task in tasks:
                due = task.due_date if task.due_date is not None else ""
                f.write(f"{task.id},{task.description},{due},{task.completed},{task.priority}\n")
        print(f"Tasks saved to {self.filename}")


class Task:
    def __init__(self, task_id, description, due_date=None, completed=False, priority="medium"):
        self.id = task_id
        self.description = description
        self.due_date = due_date
        self.completed = completed
        pr = (priority or "medium").lower()
        if pr not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got: {priority}")
        self.priority = pr

    def mark_completed(self):
        self.completed = True
        print(f"Task {self.id} '{self.description}' marked as completed.")

    def __str__(self):
        status = "✓" if self.completed else " "
        due = f" (Due: {self.due_date})" if self.due_date else ""
        return f"[{status}] {self.id}. ({self.priority}) {self.description}{due}"


class TaskManager:
    def __init__(self, storage: TaskStorage):  # รับ storage object เข้ามา
        self.storage = storage
        self.tasks = self.storage.load_tasks()
        self.next_id = (max([t.id for t in self.tasks]) + 1) if self.tasks else 1
        print(f"Loaded {len(self.tasks)} tasks. Next ID: {self.next_id}")

    def add_task(self, description, due_date=None, priority="medium"):
        task = Task(self.next_id, description, due_date, False, priority)
        self.tasks.append(task)
        self.next_id += 1
        self.storage.save_tasks(self.tasks)  # Save after adding
        print(f"Task '{description}' added with priority '{task.priority}'.")
        return task

    def list_tasks(self):
        print("\n--- Current Tasks ---")
        if not self.tasks:
            print("No tasks available.")
            return
        # เรียงตาม priority: high > medium > low แล้วตาม id
        order = {"high": 0, "medium": 1, "low": 2}
        for task in sorted(self.tasks, key=lambda t: (order[t.priority], t.id)):
            print(task)
        print("---------------------")

    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def mark_task_completed(self, task_id):
        task = self.get_task_by_id(task_id)
        if task:
            task.mark_completed()
            self.storage.save_tasks(self.tasks)  # Save after marking
            return True
        print(f"Task {task_id} not found.")
        return False


if __name__ == "__main__":
    file_storage = FileTaskStorage("my_tasks.txt")
    manager = TaskManager(file_storage)  # ส่ง FileTaskStorage เข้าไปเป็นอากิวเมนต์

    manager.list_tasks()
    manager.add_task("Review SOLID Principles", "2024-08-10", priority="high")
    manager.add_task("Prepare for Final Exam", "2024-08-15", priority="medium")
    manager.add_task("Refill water", priority="low")
    manager.list_tasks()
    manager.mark_task_completed(1)
    manager.list_tasks()
