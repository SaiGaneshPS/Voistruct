import logging
from datetime import datetime
from typing import List, Optional
from database.db_handler import DatabaseHandler
from database.models import Task
from utils.exceptions import TaskError

logger = logging.getLogger(__name__)

class TaskManager:
    def __init__(self):
        try:
            logger.info("Initializing TaskManager")
            self.db = DatabaseHandler()
        except Exception as e:
            logger.error(f"Failed to initialize TaskManager: {str(e)}")
            raise TaskError(f"TaskManager initialization failed: {str(e)}")

    def create_task(self, 
                   title: str, 
                   description: str = "", 
                   category: str = "Other",
                   due_date: Optional[datetime] = None,
                   priority: str = "Medium",
                   reminder: Optional[datetime] = None) -> Task:
        try:
            logger.info(f"Creating new task: {title}")
            task = Task(
                id=None,
                title=title,
                description=description,
                category=category,
                due_date=due_date,
                priority=priority,
                status="pending",
                reminder=reminder
            )
            task_id = self.db.create_task(task)
            logger.debug(f"Task created with ID: {task_id}")
            return self.db.get_task(task_id)
        except Exception as e:
            logger.error(f"Failed to create task '{title}': {str(e)}")
            raise TaskError(f"Failed to create task: {str(e)}")

    def get_task(self, task_id: int) -> Optional[Task]:
        try:
            logger.debug(f"Fetching task with ID: {task_id}")
            task = self.db.get_task(task_id)
            if not task:
                logger.warning(f"Task not found with ID: {task_id}")
            return task
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {str(e)}")
            raise TaskError(f"Failed to fetch task: {str(e)}")

    def get_all_tasks(self) -> List[Task]:
        try:
            logger.debug("Fetching all tasks")
            return self.db.get_all_tasks()
        except Exception as e:
            logger.error(f"Error fetching all tasks: {str(e)}")
            raise TaskError(f"Failed to fetch tasks: {str(e)}")

    def update_task(self, task: Task) -> bool:
        try:
            logger.info(f"Updating task {task.id}: {task.title}")
            success = self.db.update_task(task)
            if success:
                logger.debug(f"Successfully updated task {task.id}")
            else:
                logger.warning(f"Task {task.id} not found for update")
            return success
        except Exception as e:
            logger.error(f"Error updating task {task.id}: {str(e)}")
            raise TaskError(f"Failed to update task: {str(e)}")

    def delete_task(self, task_id: int) -> bool:
        try:
            logger.info(f"Deleting task {task_id}")
            success = self.db.delete_task(task_id)
            if success:
                logger.debug(f"Successfully deleted task {task_id}")
            else:
                logger.warning(f"Task {task_id} not found for deletion")
            return success
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise TaskError(f"Failed to delete task: {str(e)}")

    def get_tasks_by_status(self, status: str) -> List[Task]:
        try:
            logger.debug(f"Fetching tasks with status: {status}")
            return [task for task in self.get_all_tasks() if task.status == status]
        except Exception as e:
            logger.error(f"Error fetching tasks by status {status}: {str(e)}")
            raise TaskError(f"Failed to fetch tasks by status: {str(e)}")

    def get_upcoming_tasks(self, days: int = 7) -> List[Task]:
        try:
            logger.debug(f"Fetching upcoming tasks for next {days} days")
            current_date = datetime.now()
            return [
                task for task in self.get_all_tasks()
                if task.due_date and (task.due_date - current_date).days <= days
            ]
        except Exception as e:
            logger.error(f"Error fetching upcoming tasks: {str(e)}")
            raise TaskError(f"Failed to fetch upcoming tasks: {str(e)}")