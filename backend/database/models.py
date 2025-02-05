from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: Optional[int]
    title: str
    description: str
    category: str
    due_date: Optional[datetime]
    priority: str
    status: str
    reminder: Optional[datetime]
    created_at: datetime = datetime.now()

    @staticmethod
    def from_db_row(row) -> 'Task':
        return Task(
            id=row[0],
            title=row[1],
            description=row[2],
            category=row[3],
            due_date=datetime.fromisoformat(row[4]) if row[4] else None,
            priority=row[5],
            status=row[6],
            reminder=datetime.fromisoformat(row[7]) if row[7] else None,
            created_at=datetime.fromisoformat(row[8])
        )