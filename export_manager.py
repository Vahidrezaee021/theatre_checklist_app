import csv
import json
from datetime import datetime
from database import DatabaseManager

class ExportManager:
    def __init__(self, project_id):
        self.db = DatabaseManager()
        self.project_id = project_id
    
    def export_to_csv(self, file_path):
        try:
            items = self._get_all_project_items()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Category', 'Task', 'Status', 'Completed_Date', 'Notes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for item in items:
                    writer.writerow({
                        'Category': item['category'],
                        'Task': item['task'],
                        'Status': 'Completed' if item['is_completed'] else 'Pending',
                        'Completed_Date': item['completed_date'] or '',
                        'Notes': item['notes'] or ''
                    })
            
            return True, f"Exported {len(items)} tasks to CSV"
        except Exception as e:
            print(f"Export error: {e}")
            return False, f"Export failed: {str(e)}"
    
    def export_to_json(self, file_path):
        try:
            items = self._get_all_project_items()
            
            export_data = {
                'export_date': datetime.now().isoformat(),
                'total_tasks': len(items),
                'completed_tasks': sum(1 for item in items if item['is_completed']),
                'tasks': items
            }
            
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            return True, f"Exported {len(items)} tasks to JSON"
        except Exception as e:
            print(f"Export error: {e}")
            return False, f"Export failed: {str(e)}"
    
    def _get_all_project_items(self):
        try:
            results = self.db.fetch_all('''
                SELECT category, task, is_completed, completed_date, notes
                FROM checklist_items 
                WHERE project_id = ?
                ORDER BY category, created_at
            ''', (self.project_id,))
            
            items = []
            for row in results:
                items.append({
                    'category': row[0],
                    'task': row[1],
                    'is_completed': bool(row[2]),
                    'completed_date': row[3],
                    'notes': row[4]
                })
            
            return items
        except Exception as e:
            print(f"Error getting project items: {e}")
            return []