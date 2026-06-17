from sqlalchemy.orm import Session
from app.repositories.task_repository import TaskRepository
from app.models.task_model import Task

VALID_STATUSES = {"pending", "in_progress", "done"}

class TaskService:
    def __init__(self, db: Session):
        self.repo = TaskRepository(db)

    def create_task(self, title: str, description: str, assigned_to: str) -> Task:

        if not title or not title.strip():
            raise ValueError("Task title cannot be empty.")

        if not assigned_to or not assigned_to.strip():
            raise ValueError("A task must be assigned to someone.")

        return self.repo.create(
            title=title.strip(),
            description=description,
            assigned_to=assigned_to.strip(),
        )

    def get_all_tasks(self) -> list[Task]:
        return self.repo.get_all()

    def update_status(self, task_id: str, status: str) -> Task:
        if status not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {sorted(VALID_STATUSES)}")

        task = self.repo.update_status(task_id, status)

        if not task:
            raise LookupError(f"No task found with id '{task_id}'.")

        return task