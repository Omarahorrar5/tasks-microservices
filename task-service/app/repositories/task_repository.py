from sqlalchemy.orm import Session
from app.models.task_model import Task

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, description: str, assigned_to: str) -> Task:
        task = Task(title=title, description=description, assigned_to=assigned_to)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_all(self) -> list[Task]:
        """SELECT * FROM tasks ORDER BY created_at DESC"""
        return self.db.query(Task).order_by(Task.created_at.desc()).all()

    def get_by_id(self, task_id: str) -> Task | None:
        """SELECT * FROM tasks WHERE id = task_id LIMIT 1"""
        return self.db.query(Task).filter(Task.id == task_id).first()

    def update_status(self, task_id: str, status: str) -> Task | None:
        """UPDATE tasks SET status = ? WHERE id = ?"""
        task = self.get_by_id(task_id)
        if task:
            task.status = status
            self.db.commit()
            self.db.refresh(task)
        return task