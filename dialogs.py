from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, OneLineListItem
from kivy.uix.scrollview import ScrollView
from datetime import datetime
import os

class CreateProjectDialog:
    def __init__(self, app, callback):
        self.app = app
        self.callback = callback
        self.dialog = None
        self.create_dialog()
    
    def create_dialog(self):
        self.project_name = MDTextField(
            hint_text="Project Name *",
            mode="rectangle",
            max_text_length=100
        )
        
        self.project_description = MDTextField(
            hint_text="Description (optional)",
            mode="rectangle",
            max_text_length=200,
            multiline=True
        )
        
        content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing="10dp",
            padding="10dp"
        )
        content.add_widget(self.project_name)
        content.add_widget(self.project_description)
        
        self.dialog = MDDialog(
            title="Create New Project",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="CREATE",
                    theme_text_color="Custom",
                    on_release=self.create_project
                ),
            ],
        )
    
    def create_project(self, instance):
        name = self.project_name.text.strip()
        description = self.project_description.text.strip()
        
        if name:
            self.callback(name, description)
            self.dialog.dismiss()
        else:
            self.app.show_toast("Project name is required")
    
    def open(self):
        self.project_name.text = ""
        self.project_description.text = ""
        self.dialog.open()

class AddCustomItemDialog:
    def __init__(self, app, categories, callback):
        self.app = app
        self.categories = categories
        self.callback = callback
        self.dialog = None
        self.create_dialog()
    
    def create_dialog(self):
        self.task_name = MDTextField(
            hint_text="Task Description *",
            mode="rectangle",
            max_text_length=200,
            multiline=True
        )
        
        self.category_input = MDTextField(
            hint_text="Category *",
            mode="rectangle",
            max_text_length=50
        )
        
        content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing="10dp",
            padding="10dp"
        )
        content.add_widget(self.task_name)
        content.add_widget(self.category_input)
        
        self.dialog = MDDialog(
            title="Add Custom Task",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="ADD",
                    theme_text_color="Custom",
                    on_release=self.add_item
                ),
            ],
        )
    
    def add_item(self, instance):
        task = self.task_name.text.strip()
        category = self.category_input.text.strip()
        
        if task and category:
            self.callback(category, task, None)
            self.dialog.dismiss()
        else:
            self.app.show_toast("Task and category are required")
    
    def open(self):
        self.task_name.text = ""
        self.category_input.text = ""
        self.dialog.open()

class NotesDialog:
    def __init__(self, app, task_name, current_notes, callback):
        self.app = app
        self.callback = callback
        self.dialog = None
        self.create_dialog(task_name, current_notes)
    
    def create_dialog(self, task_name, current_notes):
        self.notes_input = MDTextField(
            hint_text="Add notes...",
            mode="rectangle",
            multiline=True,
            max_text_length=1000
        )
        self.notes_input.text = current_notes or ""
        
        content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing="10dp",
            padding="10dp",
            size_hint_y=None,
            height="200dp"
        )
        content.add_widget(self.notes_input)
        
        self.dialog = MDDialog(
            title=f"Notes: {task_name}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="SAVE",
                    theme_text_color="Custom",
                    on_release=self.save_notes
                ),
            ],
        )
    
    def save_notes(self, instance):
        notes = self.notes_input.text.strip()
        self.callback(notes)
        self.dialog.dismiss()
    
    def open(self):
        self.dialog.open()

class StatsDialog:
    def __init__(self, app, stats_data, callback):
        self.app = app
        self.callback = callback
        self.dialog = None
        self.create_dialog(stats_data)
    
    def create_dialog(self, stats_data):
        from kivymd.uix.list import MDList, OneLineListItem
        from kivy.uix.scrollview import ScrollView
        
        content = ScrollView()
        list_layout = MDList()
        
        # Overall progress
        overall_item = OneLineListItem(
            text=f"📊 Overall Progress: {stats_data['overall_percentage']}%",
            theme_text_color="Primary"
        )
        list_layout.add_widget(overall_item)
        
        # Tasks summary
        tasks_item = OneLineListItem(
            text=f"✅ Tasks: {stats_data['completed_tasks']}/{stats_data['total_tasks']} completed",
            theme_text_color="Primary"
        )
        list_layout.add_widget(tasks_item)
        
        # Recent activity
        recent_item = OneLineListItem(
            text=f"📈 Recent (7 days): {stats_data['recent_activity']} tasks completed",
            theme_text_color="Primary"
        )
        list_layout.add_widget(recent_item)
        
        # Pending tasks
        pending_item = OneLineListItem(
            text=f"⏳ Pending: {stats_data['pending_tasks']} tasks remaining",
            theme_text_color="Primary"
        )
        list_layout.add_widget(pending_item)
        
        # Category breakdown
        category_header = OneLineListItem(
            text="🎯 Category Breakdown:",
            theme_text_color="Secondary"
        )
        list_layout.add_widget(category_header)
        
        for category, cat_stats in stats_data['category_stats'].items():
            cat_item = OneLineListItem(
                text=f"   {category}: {cat_stats['completed']}/{cat_stats['total']} ({cat_stats['percentage']}%)",
                theme_text_color="Primary"
            )
            list_layout.add_widget(cat_item)
        
        content.add_widget(list_layout)
        
        self.dialog = MDDialog(
            title="Project Statistics",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="EXPORT DATA",
                    theme_text_color="Custom",
                    on_release=self.export_data
                ),
                MDFlatButton(
                    text="CLOSE",
                    theme_text_color="Custom",
                    on_release=lambda x: self.dialog.dismiss()
                ),
            ],
        )
    
    def export_data(self, instance):
        self.dialog.dismiss()
        self.callback()
    
    def open(self):
        self.dialog.open()

class ExportDialog:
    def __init__(self, app, project_name, callback):
        self.app = app
        self.callback = callback
        self.dialog = None
        self.create_dialog(project_name)
    
    def create_dialog(self, project_name):
        content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing="10dp",
            padding="10dp"
        )
        
        self.dialog = MDDialog(
            title=f"Export: {project_name}",
            text="Choose export format:",
            type="simple",
            items=[
                "CSV Format (Excel compatible)",
                "JSON Format (Backup)"
            ],
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    on_release=lambda x: self.dialog.dismiss()
                ),
            ],
        )
        
        # Add custom buttons for export options
        self.dialog.buttons[0].parent.add_widget(MDFlatButton(
            text="CSV",
            theme_text_color="Custom",
            on_release=lambda x: self.export_selected('csv')
        ))
        
        self.dialog.buttons[0].parent.add_widget(MDFlatButton(
            text="JSON",
            theme_text_color="Custom",
            on_release=lambda x: self.export_selected('json')
        ))
    
    def export_selected(self, format_type):
        self.dialog.dismiss()
        self.callback(format_type)
    
    def open(self):
        self.dialog.open()

class ConfirmationDialog:
    def __init__(self, app, title, message, confirm_callback):
        self.app = app
        self.confirm_callback = confirm_callback
        self.dialog = None
        self.create_dialog(title, message)
    
    def create_dialog(self, title, message):
        self.dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="DELETE",
                    theme_text_color="Custom",
                    on_release=self.confirm_action
                ),
            ],
        )
    
    def confirm_action(self, instance):
        self.dialog.dismiss()
        self.confirm_callback()
    
    def open(self):
        self.dialog.open()