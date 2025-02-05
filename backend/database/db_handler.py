import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from .models import Task
from utils.exceptions import DatabaseError

class DatabaseHandler:
    def __init__(self):
        try:
            self.db_path = Path.home() / '.voistruct' / 'voistruct.db'
            self.db_path.parent.mkdir(exist_ok=True)
            self.init_database()
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {str(e)}")

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    due_date TIMESTAMP,
                    priority TEXT,
                    status TEXT DEFAULT 'pending',
                    reminder TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    reminder_time TIMESTAMP,
                    is_notified BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            ''')

    def create_task(self, task: Task) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (
                    title, description, category, due_date, 
                    priority, status, reminder, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.title, task.description, task.category,
                task.due_date.isoformat() if task.due_date else None,
                task.priority, task.status,
                task.reminder.isoformat() if task.reminder else None,
                task.created_at.isoformat()
            ))
            return cursor.lastrowid

    def get_task(self, task_id: int) -> Optional[Task]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            return Task.from_db_row(row) if row else None

    def get_all_tasks(self) -> List[Task]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
            return [Task.from_db_row(row) for row in cursor.fetchall()]

    def update_task(self, task: Task) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tasks 
                SET title=?, description=?, category=?, due_date=?,
                    priority=?, status=?, reminder=?
                WHERE id=?
            ''', (
                task.title, task.description, task.category,
                task.due_date.isoformat() if task.due_date else None,
                task.priority, task.status,
                task.reminder.isoformat() if task.reminder else None,
                task.id
            ))
            return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id=?', (task_id,))
            return cursor.rowcount > 0

    def get_pending_reminders(self) -> List[tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.id, t.title, r.reminder_time 
                FROM tasks t
                JOIN reminders r ON t.id = r.task_id
                WHERE r.is_notified = FALSE 
                AND r.reminder_time <= datetime('now')
            ''')
            return cursor.fetchall()