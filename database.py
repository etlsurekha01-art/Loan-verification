"""
Database module for loan verification system.
Handles SQLite operations for task persistence and state management.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import aiosqlite
import os

from models import LoanTask, TaskStatus

# Configure logging
logger = logging.getLogger(__name__)


class Database:
    """
    Database manager for loan verification tasks.
    Uses SQLite for persistence with async support.
    """
    
    def __init__(self, db_path: str = "./loan_verification.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        logger.info(f"Database initialized at {db_path}")
    
    async def initialize(self):
        """Create database tables if they don't exist"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS loan_tasks (
                        task_id TEXT PRIMARY KEY,
                        applicant_name TEXT NOT NULL,
                        status TEXT NOT NULL,
                        request_data TEXT NOT NULL,
                        result_data TEXT,
                        error_message TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    )
                """)
                
                # Create index for faster queries
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_applicant_name 
                    ON loan_tasks(applicant_name)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_status 
                    ON loan_tasks(status)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_at 
                    ON loan_tasks(created_at DESC)
                """)
                
                await db.commit()
                logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def create_task(self, task: LoanTask) -> bool:
        """
        Create a new loan verification task.
        
        Args:
            task: LoanTask object to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO loan_tasks 
                    (task_id, applicant_name, status, request_data, result_data, 
                     error_message, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task.task_id,
                    task.applicant_name,
                    task.status.value,
                    json.dumps(task.request_data),
                    json.dumps(task.result_data) if task.result_data else None,
                    task.error_message,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat()
                ))
                await db.commit()
                logger.info(f"Task {task.task_id} created for {task.applicant_name}")
                return True
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False
    
    async def get_task(self, task_id: str) -> Optional[LoanTask]:
        """
        Retrieve a task by ID.
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            LoanTask object or None if not found
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT * FROM loan_tasks WHERE task_id = ?
                """, (task_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return self._row_to_task(row)
                    return None
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {e}")
            return None
    
    async def update_task_status(
        self, 
        task_id: str, 
        status: TaskStatus,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update task status and result.
        
        Args:
            task_id: Task identifier
            status: New task status
            result_data: Optional result data
            error_message: Optional error message
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE loan_tasks 
                    SET status = ?, 
                        result_data = ?,
                        error_message = ?,
                        updated_at = ?
                    WHERE task_id = ?
                """, (
                    status.value,
                    json.dumps(result_data) if result_data else None,
                    error_message,
                    datetime.utcnow().isoformat(),
                    task_id
                ))
                await db.commit()
                logger.info(f"Task {task_id} updated to status: {status.value}")
                return True
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return False
    
    async def get_tasks_by_applicant(self, applicant_name: str) -> list[LoanTask]:
        """
        Get all tasks for a specific applicant.
        
        Args:
            applicant_name: Applicant's name
            
        Returns:
            List of LoanTask objects
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT * FROM loan_tasks 
                    WHERE applicant_name = ?
                    ORDER BY created_at DESC
                """, (applicant_name,)) as cursor:
                    rows = await cursor.fetchall()
                    return [self._row_to_task(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving tasks for {applicant_name}: {e}")
            return []
    
    async def get_recent_tasks(self, limit: int = 10) -> list[LoanTask]:
        """
        Get most recent tasks.
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            List of LoanTask objects
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT * FROM loan_tasks 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    return [self._row_to_task(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving recent tasks: {e}")
            return []
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    DELETE FROM loan_tasks WHERE task_id = ?
                """, (task_id,))
                await db.commit()
                logger.info(f"Task {task_id} deleted")
                return True
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False
    
    async def check_connection(self) -> bool:
        """
        Check if database connection is working.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    def _row_to_task(self, row: aiosqlite.Row) -> LoanTask:
        """
        Convert database row to LoanTask object.
        
        Args:
            row: Database row
            
        Returns:
            LoanTask object
        """
        return LoanTask(
            task_id=row['task_id'],
            applicant_name=row['applicant_name'],
            status=TaskStatus(row['status']),
            request_data=json.loads(row['request_data']),
            result_data=json.loads(row['result_data']) if row['result_data'] else None,
            error_message=row['error_message'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total tasks
                async with db.execute("SELECT COUNT(*) FROM loan_tasks") as cursor:
                    total = (await cursor.fetchone())[0]
                
                # Tasks by status
                async with db.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM loan_tasks 
                    GROUP BY status
                """) as cursor:
                    status_counts = {row[0]: row[1] async for row in cursor}
                
                return {
                    "total_tasks": total,
                    "by_status": status_counts,
                    "database_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}


# Global database instance
db_instance: Optional[Database] = None


def get_database() -> Database:
    """
    Get or create global database instance.
    
    Returns:
        Database instance
    """
    global db_instance
    if db_instance is None:
        db_path = os.getenv("DATABASE_PATH", "./loan_verification.db")
        db_instance = Database(db_path)
    return db_instance
