import sqlite3
import json
import os
from datetime import datetime
import threading
import atexit

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, db_name='theatre_checklists.db'):
        if not self._initialized:
            self.db_name = db_name
            self._connection = None
            self._initialized = True
            self.init_database()
            atexit.register(self.close_connection)
    
    def get_connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_name, 
                check_same_thread=False,
                timeout=30.0
            )
            self._connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection
    
    def close_connection(self):
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Checklist items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                task TEXT NOT NULL,
                is_custom BOOLEAN DEFAULT 0,
                is_completed BOOLEAN DEFAULT 0,
                notes TEXT,
                due_date DATETIME,
                completed_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_project_id ON checklist_items(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_category ON checklist_items(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_completed ON checklist_items(is_completed)')
        
        conn.commit()
    
    def execute_query(self, query, params=()):
        """Execute a query with proper error handling"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            # Try to reconnect if connection is lost
            if "database is locked" in str(e):
                self.close_connection()
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor
            raise
    
    def fetch_all(self, query, params=()):
        cursor = self.execute_query(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query, params=()):
        cursor = self.execute_query(query, params)
        return cursor.fetchone()