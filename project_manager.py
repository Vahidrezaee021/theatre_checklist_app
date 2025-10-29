import json
import os
from database import DatabaseManager
from datetime import datetime

class ProjectManager:
    def __init__(self, user_id):
        self.db = DatabaseManager()
        self.user_id = user_id
    
    def create_project(self, name, description=""):
        try:
            # Validate input
            name = name.strip()
            if not name:
                return None, "Project name cannot be empty"
            
            if len(name) > 100:
                return None, "Project name too long (max 100 characters)"
            
            # Check for duplicate project names for this user
            existing = self.db.fetch_one(
                "SELECT id FROM projects WHERE user_id = ? AND name = ?", 
                (self.user_id, name)
            )
            if existing:
                return None, "You already have a project with this name"
            
            # Create project
            cursor = self.db.execute_query(
                'INSERT INTO projects (user_id, name, description) VALUES (?, ?, ?)',
                (self.user_id, name, description.strip())
            )
            
            project_id = cursor.lastrowid
            self._add_default_checklist_items(project_id)
            
            return project_id, "Project created successfully"
        except Exception as e:
            print(f"Error creating project: {e}")
            return None, "Failed to create project. Please try again."
    
    def _add_default_checklist_items(self, project_id):
        default_items = self._load_default_checklists()
        
        for category, tasks in default_items.items():
            for task in tasks:
                try:
                    self.db.execute_query('''
                        INSERT INTO checklist_items 
                        (project_id, category, task, is_custom, is_completed) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (project_id, category, task, False, False))
                except Exception as e:
                    print(f"Error adding default item: {e}")
                    continue
    
    def _load_default_checklists(self):
        default_data = {
            "Set Design": [
                "Finalize set design concept",
                "Create technical drawings",
                "Source materials and props",
                "Build set pieces",
                "Paint and finish set",
                "Install set on stage/location"
            ],
            "Costumes": [
                "Finalize costume designs",
                "Take actor measurements",
                "Source fabrics and materials",
                "Construct costumes",
                "Schedule fittings",
                "Complete alterations"
            ],
            "Lighting": [
                "Create lighting plot",
                "Hang and circuit lights",
                "Program cues",
                "Focus lights",
                "Run lighting tests"
            ],
            "Sound": [
                "Design soundscape",
                "Source sound effects",
                "Record dialogue if needed",
                "Set up sound system",
                "Program sound cues"
            ],
            "Rehearsal": [
                "Blocking rehearsals",
                "Line rehearsals",
                "Technical rehearsals",
                "Dress rehearsals",
                "Final run-through"
            ],
            "Production": [
                "Finalize script",
                "Cast actors",
                "Schedule production meetings",
                "Coordinate with department heads",
                "Create production timeline"
            ],
            "Marketing": [
                "Design posters and programs",
                "Create social media campaign",
                "Press releases",
                "Ticket sales setup",
                "Opening night preparations"
            ]
        }
        return default_data
    
    def get_user_projects(self):
        try:
            results = self.db.fetch_all(
                '''SELECT id, name, description, created_at 
                   FROM projects WHERE user_id = ? 
                   ORDER BY created_at DESC''',
                (self.user_id,)
            )
            
            projects = []
            for row in results:
                projects.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'created_at': row[3]
                })
            
            return projects
        except Exception as e:
            print(f"Error getting user projects: {e}")
            return []
    
    def delete_project(self, project_id):
        try:
            # Verify project belongs to user
            project = self.db.fetch_one(
                "SELECT id FROM projects WHERE id = ? AND user_id = ?",
                (project_id, self.user_id)
            )
            
            if not project:
                return False, "Project not found"
            
            self.db.execute_query('DELETE FROM projects WHERE id = ?', (project_id,))
            return True, "Project deleted successfully"
        except Exception as e:
            print(f"Error deleting project: {e}")
            return False, "Failed to delete project"
    
    def get_project_details(self, project_id):
        try:
            result = self.db.fetch_one(
                'SELECT name, description FROM projects WHERE id = ? AND user_id = ?',
                (project_id, self.user_id)
            )
            
            if result:
                return {'name': result[0], 'description': result[1]}
            return None
        except Exception as e:
            print(f"Error getting project details: {e}")
            return None
    
    def update_project(self, project_id, name, description):
        try:
            name = name.strip()
            if not name:
                return False, "Project name cannot be empty"
            
            self.db.execute_query(
                'UPDATE projects SET name = ?, description = ? WHERE id = ? AND user_id = ?',
                (name, description.strip(), project_id, self.user_id)
            )
            
            return True, "Project updated successfully"
        except Exception as e:
            print(f"Error updating project: {e}")
            return False, "Failed to update project"