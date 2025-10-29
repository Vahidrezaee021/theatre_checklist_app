from database import DatabaseManager
from datetime import datetime

class ChecklistManager:
    def __init__(self, project_id):
        self.db = DatabaseManager()
        self.project_id = project_id
    
    def get_checklist_items(self, category_filter=None):
        try:
            query = '''
                SELECT id, category, task, is_custom, is_completed, notes, due_date, completed_date
                FROM checklist_items 
                WHERE project_id = ?
            '''
            params = [self.project_id]
            
            if category_filter and category_filter != "All":
                query += ' AND category = ?'
                params.append(category_filter)
            
            query += ' ORDER BY category, created_at'
            
            results = self.db.fetch_all(query, params)
            
            items = []
            for row in results:
                items.append({
                    'id': row[0],
                    'category': row[1],
                    'task': row[2],
                    'is_custom': bool(row[3]),
                    'is_completed': bool(row[4]),
                    'notes': row[5],
                    'due_date': row[6],
                    'completed_date': row[7]
                })
            
            return items
        except Exception as e:
            print(f"Error getting checklist items: {e}")
            return []
    
    def get_categories(self):
        try:
            results = self.db.fetch_all('''
                SELECT DISTINCT category 
                FROM checklist_items 
                WHERE project_id = ? 
                ORDER BY category
            ''', (self.project_id,))
            
            categories = [row[0] for row in results]
            return categories
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def add_custom_item(self, category, task, due_date=None):
        try:
            category = category.strip()
            task = task.strip()
            
            if not category:
                return None, "Category is required"
            if not task:
                return None, "Task description is required"
            if len(task) > 200:
                return None, "Task description too long (max 200 characters)"
            
            cursor = self.db.execute_query('''
                INSERT INTO checklist_items 
                (project_id, category, task, is_custom, is_completed, due_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.project_id, category, task, True, False, due_date))
            
            return cursor.lastrowid, "Task added successfully"
        except Exception as e:
            print(f"Error adding custom item: {e}")
            return None, "Failed to add task"
    
    def update_item_status(self, item_id, is_completed):
        try:
            completed_date = datetime.now() if is_completed else None
            
            self.db.execute_query('''
                UPDATE checklist_items 
                SET is_completed = ?, completed_date = ?
                WHERE id = ? AND project_id = ?
            ''', (is_completed, completed_date, item_id, self.project_id))
            
            return True
        except Exception as e:
            print(f"Error updating item status: {e}")
            return False
    
    def update_item_notes(self, item_id, notes):
        try:
            self.db.execute_query('''
                UPDATE checklist_items 
                SET notes = ?
                WHERE id = ? AND project_id = ?
            ''', (notes, item_id, self.project_id))
            
            return True
        except Exception as e:
            print(f"Error updating item notes: {e}")
            return False
    
    def delete_custom_item(self, item_id):
        try:
            self.db.execute_query('''
                DELETE FROM checklist_items 
                WHERE id = ? AND project_id = ? AND is_custom = 1
            ''', (item_id, self.project_id))
            
            return True
        except Exception as e:
            print(f"Error deleting custom item: {e}")
            return False
    
    def get_item_count(self):
        try:
            result = self.db.fetch_one(
                'SELECT COUNT(*) as count FROM checklist_items WHERE project_id = ?',
                (self.project_id,)
            )
            return result[0] if result else 0
        except Exception as e:
            print(f"Error getting item count: {e}")
            return 0