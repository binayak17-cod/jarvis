import os
import json
import datetime
from typing import List, Dict, Optional

class TaskManager:
    def __init__(self, file_path: str = None):
        """
        Initialize TaskManager with JSON file for better data structure
        """
        if file_path is None:
            # Use absolute path in the same directory as this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "tasks.json")
        self.file_path = file_path
        self.tasks = self.load_tasks()
    
    def load_tasks(self) -> Dict:
        """
        Load tasks from JSON file or create new if doesn't exist
        """
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                # Create new tasks structure
                return {
                    "tasks": [],
                    "completed": [],
                    "created_date": datetime.datetime.now().isoformat(),
                    "last_modified": datetime.datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error loading tasks: {e}")
            return {
                "tasks": [],
                "completed": [],
                "created_date": datetime.datetime.now().isoformat(),
                "last_modified": datetime.datetime.now().isoformat()
            }
    
    def save_tasks(self) -> bool:
        """
        Save tasks to JSON file
        """
        try:
            self.tasks["last_modified"] = datetime.datetime.now().isoformat()
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(self.tasks, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            return False
    
    def add_task(self, task_text: str, priority: str = "medium", due_date: str = None) -> str:
        """
        Add a new task with metadata
        """
        if not task_text.strip():
            return "Error: Task cannot be empty."
        
        task_id = len(self.tasks["tasks"]) + 1
        new_task = {
            "id": task_id,
            "text": task_text.strip(),
            "priority": priority.lower(),
            "status": "pending",
            "created": datetime.datetime.now().isoformat(),
            "due_date": due_date,
            "completed_date": None
        }
        
        self.tasks["tasks"].append(new_task)
        
        if self.save_tasks():
            return f"Task added successfully: {task_text.strip()}"
        else:
            return "Error: Could not save task."
    
    def delete_task(self, task_identifier: str) -> str:
        """
        Delete task by ID or text
        """
        try:
            # Try to delete by ID first
            task_id = int(task_identifier)
            for i, task in enumerate(self.tasks["tasks"]):
                if task["id"] == task_id:
                    deleted_task = self.tasks["tasks"].pop(i)
                    self.save_tasks()
                    return f"Task deleted: {deleted_task['text']}"
            return "Task not found with that ID."
        except ValueError:
            # Try to delete by text
            task_text = task_identifier.lower()
            for i, task in enumerate(self.tasks["tasks"]):
                if task_text in task["text"].lower():
                    deleted_task = self.tasks["tasks"].pop(i)
                    self.save_tasks()
                    return f"Task deleted: {deleted_task['text']}"
            return "Task not found with that text."
    
    def complete_task(self, task_identifier: str) -> str:
        """
        Mark task as completed
        """
        try:
            # Try to complete by ID first
            task_id = int(task_identifier)
            for task in self.tasks["tasks"]:
                if task["id"] == task_id:
                    task["status"] = "completed"
                    task["completed_date"] = datetime.datetime.now().isoformat()
                    self.tasks["completed"].append(task)
                    self.tasks["tasks"].remove(task)
                    self.save_tasks()
                    return f"Task completed: {task['text']}"
            return "Task not found with that ID."
        except ValueError:
            # Try to complete by text
            task_text = task_identifier.lower()
            for task in self.tasks["tasks"]:
                if task_text in task["text"].lower():
                    task["status"] = "completed"
                    task["completed_date"] = datetime.datetime.now().isoformat()
                    self.tasks["completed"].append(task)
                    self.tasks["tasks"].remove(task)
                    self.save_tasks()
                    return f"Task completed: {task['text']}"
            return "Task not found with that text."
    
    def get_pending_tasks(self) -> List[Dict]:
        """
        Get all pending tasks
        """
        return self.tasks["tasks"]
    
    def get_completed_tasks(self) -> List[Dict]:
        """
        Get all completed tasks
        """
        return self.tasks["completed"]
    
    def get_tasks_by_priority(self, priority: str) -> List[Dict]:
        """
        Get tasks filtered by priority
        """
        priority = priority.lower()
        return [task for task in self.tasks["tasks"] if task["priority"] == priority]
    
    def get_tasks_summary(self) -> str:
        """
        Get a summary of all tasks
        """
        pending_count = len(self.tasks["tasks"])
        completed_count = len(self.tasks["completed"])
        
        if pending_count == 0 and completed_count == 0:
            return "You have no tasks."
        
        summary = f"You have {pending_count} pending task{'s' if pending_count != 1 else ''}"
        if completed_count > 0:
            summary += f" and {completed_count} completed task{'s' if completed_count != 1 else ''}"
        
        return summary
    
    def get_tasks_text(self) -> str:
        """
        Get formatted text of pending tasks for speech
        """
        if not self.tasks["tasks"]:
            return "You have no pending tasks."
        
        task_list = []
        for i, task in enumerate(self.tasks["tasks"], 1):
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task["priority"], "⚪")
            task_list.append(f"{i}. {priority_emoji} {task['text']}")
        
        return "Your pending tasks are: " + ". ".join(task_list)
    
    def clear_completed_tasks(self) -> str:
        """
        Clear all completed tasks
        """
        count = len(self.tasks["completed"])
        self.tasks["completed"] = []
        self.save_tasks()
        return f"Cleared {count} completed task{'s' if count != 1 else ''}."
    
    def search_tasks(self, search_term: str) -> List[Dict]:
        """
        Search tasks by text
        """
        search_term = search_term.lower()
        return [task for task in self.tasks["tasks"] if search_term in task["text"].lower()]

# Global task manager instance
task_manager = TaskManager()

# Convenience functions for Synbi.py
def add_task(task_text: str, priority: str = "medium") -> str:
    """Add a new task"""
    return task_manager.add_task(task_text, priority)

def delete_task(task_identifier: str) -> str:
    """Delete a task"""
    return task_manager.delete_task(task_identifier)

def complete_task(task_identifier: str) -> str:
    """Complete a task"""
    return task_manager.complete_task(task_identifier)

def get_tasks_summary() -> str:
    """Get tasks summary"""
    return task_manager.get_tasks_summary()

def get_tasks_text() -> str:
    """Get formatted tasks for speech"""
    return task_manager.get_tasks_text()

def get_pending_tasks() -> List[Dict]:
    """Get all pending tasks"""
    return task_manager.get_pending_tasks()

def clear_completed_tasks() -> str:
    """Clear completed tasks"""
    return task_manager.clear_completed_tasks()

def search_tasks(search_term: str) -> List[Dict]:
    """Search tasks"""
    return task_manager.search_tasks(search_term)

