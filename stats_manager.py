from database import DatabaseManager
from datetime import datetime, timedelta

class StatsManager:
    def __init__(self, project_id):
        self.db = DatabaseManager()
        self.project_id = project_id
    
    def get_project_stats(self):
        try:
            # Get category statistics
            results = self.db.fetch_all('''
                SELECT 
                    category,
                    COUNT(*) as total,
                    SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed
                FROM checklist_items 
                WHERE project_id = ?
                GROUP BY category
                ORDER BY category
            ''', (self.project_id,))
            
            category_stats = {}
            total_tasks = 0
            completed_tasks = 0
            
            for row in results:
                category, total, completed = row
                category_stats[category] = {
                    'total': total,
                    'completed': completed,
                    'percentage': round((completed / total * 100), 1) if total > 0 else 0
                }
                total_tasks += total
                completed_tasks += completed
            
            overall_percentage = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
            
            # Get recent activity (last 7 days)
            recent_result = self.db.fetch_one('''
                SELECT COUNT(*) FROM checklist_items 
                WHERE project_id = ? AND is_completed = 1 
                AND completed_date >= datetime('now', '-7 days')
            ''', (self.project_id,))
            
            recent_activity = recent_result[0] if recent_result else 0
            
            # Get completion rate trend
            trend = self._get_completion_trend()
            
            return {
                'category_stats': category_stats,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'overall_percentage': overall_percentage,
                'recent_activity': recent_activity,
                'pending_tasks': total_tasks - completed_tasks,
                'completion_trend': trend
            }
        except Exception as e:
            print(f"Error getting project stats: {e}")
            return self._get_empty_stats()
    
    def _get_completion_trend(self):
        try:
            results = self.db.fetch_all('''
                SELECT 
                    DATE(completed_date) as date,
                    COUNT(*) as completed
                FROM checklist_items 
                WHERE project_id = ? AND is_completed = 1
                AND completed_date >= datetime('now', '-30 days')
                GROUP BY DATE(completed_date)
                ORDER BY date
            ''', (self.project_id,))
            
            trend = []
            for row in results:
                trend.append({
                    'date': row[0],
                    'completed': row[1]
                })
            
            return trend
        except Exception as e:
            print(f"Error getting completion trend: {e}")
            return []
    
    def _get_empty_stats(self):
        return {
            'category_stats': {},
            'total_tasks': 0,
            'completed_tasks': 0,
            'overall_percentage': 0,
            'recent_activity': 0,
            'pending_tasks': 0,
            'completion_trend': []
        }
    
    def get_completion_timeline(self):
        return self._get_completion_trend()