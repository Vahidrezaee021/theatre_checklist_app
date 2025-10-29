from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.checkbox import CheckBox
import os
import json

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.toast import toast

from auth import AuthManager
from project_manager import ProjectManager
from checklist_manager import ChecklistManager
from stats_manager import StatsManager
from export_manager import ExportManager
from dialogs import CreateProjectDialog, AddCustomItemDialog, NotesDialog, StatsDialog, ExportDialog, ConfirmationDialog

# Set window size for mobile development
Window.size = (360, 640)

Builder.load_string('''
<LoginScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'

        MDLabel:
            text: '🎭 Theatre Checklist'
            theme_text_color: 'Primary'
            font_style: 'H4'
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1]

        MDLabel:
            text: 'Professional checklist manager for stage productions'
            theme_text_color: 'Secondary'
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1]

        Widget:
            size_hint_y: 0.2

        MDTextField:
            id: email_input
            hint_text: "Email"
            icon_right: "email"
            mode: "rectangle"
            size_hint_y: None
            height: "50dp"

        MDTextField:
            id: password_input
            hint_text: "Password"
            icon_right: "key"
            mode: "rectangle"
            password: True
            size_hint_y: None
            height: "50dp"

        MDRaisedButton:
            text: "LOGIN"
            on_press: root.login()
            size_hint_y: None
            height: "50dp"

        MDFlatButton:
            text: "Create new account"
            on_press: root.go_to_register()
            size_hint_y: None
            height: "30dp"

<RegisterScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'

        MDLabel:
            text: 'Create Account'
            theme_text_color: 'Primary'
            font_style: 'H4'
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: email_input
            hint_text: "Email"
            icon_right: "email"
            mode: "rectangle"
            size_hint_y: None
            height: "50dp"

        MDTextField:
            id: password_input
            hint_text: "Password (min 6 characters)"
            icon_right: "key"
            mode: "rectangle"
            password: True
            size_hint_y: None
            height: "50dp"

        MDTextField:
            id: confirm_password_input
            hint_text: "Confirm Password"
            icon_right: "key"
            mode: "rectangle"
            password: True
            size_hint_y: None
            height: "50dp"

        MDRaisedButton:
            text: "CREATE ACCOUNT"
            on_press: root.register()
            size_hint_y: None
            height: "50dp"

        MDFlatButton:
            text: "Already have an account? Login"
            on_press: root.go_to_login()
            size_hint_y: None
            height: "30dp"

<ProjectsScreen>:
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "My Projects"
            elevation: 4
            left_action_items: [["logout", lambda x: root.logout()]]
            right_action_items: [["plus", lambda x: root.create_new_project()]]

        ScrollView:
            MDList:
                id: projects_list
                padding: "10dp"
                spacing: "10dp"

<ChecklistScreen>:
    project_name: "Project"
    
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: root.project_name
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["chart-box", lambda x: root.show_stats()], ["export", lambda x: root.export_data()], ["plus", lambda x: root.add_custom_item()]]

        MDBoxLayout:
            orientation: 'vertical'
            spacing: '10dp'
            padding: '10dp'
            size_hint_y: None
            height: '120dp'

            MDLabel:
                text: "Filter by Category:"
                size_hint_y: None
                height: self.texture_size[1]

            ScrollView:
                MDBoxLayout:
                    id: categories_container
                    orientation: 'horizontal'
                    adaptive_size: True
                    spacing: '5dp'
                    size_hint_x: None
                    width: self.minimum_width

            MDLabel:
                id: progress_label
                text: "Loading..."
                theme_text_color: "Secondary"
                size_hint_y: None
                height: self.texture_size[1]

        ScrollView:
            MDList:
                id: checklist_list
                padding: "10dp"
                spacing: "10dp"
''')


class LoginScreen(MDScreen):
    def login(self):
        app = MDApp.get_running_app()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text
        
        if not email or not password:
            app.show_toast("Please enter both email and password")
            return
            
        app.show_loading("Logging in...")
        # Use Clock to prevent UI freezing during login
        Clock.schedule_once(lambda dt: self._perform_login(email, password), 0.1)
    
    def _perform_login(self, email, password):
        app = MDApp.get_running_app()
        success, message = app.auth_manager.login_user(email, password)
        
        app.hide_loading()
        
        if success:
            app.user_id = app.auth_manager.current_user['id']
            self.manager.current = 'projects'
            self.ids.email_input.text = ""
            self.ids.password_input.text = ""
            app.show_toast("Welcome back!")
        else:
            app.show_toast(message)
    
    def go_to_register(self):
        self.manager.current = 'register'
        self.ids.email_input.text = ""
        self.ids.password_input.text = ""


class RegisterScreen(MDScreen):
    def register(self):
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text
        confirm_password = self.ids.confirm_password_input.text
        
        if not email or not password or not confirm_password:
            MDApp.get_running_app().show_toast("Please fill all fields")
            return
            
        if password != confirm_password:
            MDApp.get_running_app().show_toast("Passwords don't match")
            return
        
        app = MDApp.get_running_app()
        app.show_loading("Creating account...")
        Clock.schedule_once(lambda dt: self._perform_registration(email, password), 0.1)
    
    def _perform_registration(self, email, password):
        app = MDApp.get_running_app()
        success, message = app.auth_manager.register_user(email, password)
        
        app.hide_loading()
        
        if success:
            app.show_toast("Account created! Please log in.")
            self.manager.current = 'login'
            self.clear_fields()
        else:
            app.show_toast(message)
    
    def go_to_login(self):
        self.manager.current = 'login'
        self.clear_fields()
    
    def clear_fields(self):
        self.ids.email_input.text = ""
        self.ids.password_input.text = ""
        self.ids.confirm_password_input.text = ""


class ProjectsScreen(MDScreen):
    def on_enter(self):
        self.load_projects()
    
    def load_projects(self):
        app = MDApp.get_running_app()
        self.ids.projects_list.clear_widgets()
        
        if not app.user_id:
            app.show_toast("Please log in first")
            return
            
        app.show_loading("Loading projects...")
        Clock.schedule_once(lambda dt: self._load_projects_async(), 0.1)
    
    def _load_projects_async(self):
        app = MDApp.get_running_app()
        project_manager = ProjectManager(app.user_id)
        projects = project_manager.get_user_projects()
        
        app.hide_loading()
        self.ids.projects_list.clear_widgets()
        
        if not projects:
            empty_label = OneLineListItem(
                text="No projects yet. Create your first project!",
                theme_text_color="Secondary"
            )
            self.ids.projects_list.add_widget(empty_label)
            return
        
        for project in projects:
            item = TwoLineListItem(
                text=project['name'],
                secondary_text=project['description'] or "No description",
                on_release=lambda x, pid=project['id']: self.open_project(pid)
            )
            self.ids.projects_list.add_widget(item)
    
    def open_project(self, project_id):
        app = MDApp.get_running_app()
        app.current_project_id = project_id
        
        # Load project details
        project_manager = ProjectManager(app.user_id)
        project_details = project_manager.get_project_details(project_id)
        
        if project_details:
            checklist_screen = self.manager.get_screen('checklist')
            checklist_screen.project_name = project_details['name']
        
        self.manager.current = 'checklist'
    
    def create_new_project(self):
        app = MDApp.get_running_app()
        if not hasattr(app, 'create_project_dialog'):
            app.create_project_dialog = CreateProjectDialog(app, self.create_project_callback)
        app.create_project_dialog.open()
    
    def create_project_callback(self, name, description):
        app = MDApp.get_running_app()
        if not name:
            app.show_toast("Project name is required")
            return
            
        app.show_loading("Creating project...")
        Clock.schedule_once(lambda dt: self._create_project_async(name, description), 0.1)
    
    def _create_project_async(self, name, description):
        app = MDApp.get_running_app()
        project_manager = ProjectManager(app.user_id)
        project_id, message = project_manager.create_project(name, description)
        
        app.hide_loading()
        
        if project_id:
            self.load_projects()
            app.show_toast(f"Project '{name}' created!")
        else:
            app.show_toast(message)
    
    def logout(self):
        app = MDApp.get_running_app()
        confirmation = ConfirmationDialog(
            app, 
            "Logout", 
            "Are you sure you want to logout?",
            self._perform_logout
        )
        confirmation.open()
    
    def _perform_logout(self):
        app = MDApp.get_running_app()
        app.auth_manager.logout()
        app.user_id = None
        app.current_project_id = None
        self.manager.current = 'login'
        app.show_toast("Logged out successfully")


class ChecklistItem(MDBoxLayout):
    def __init__(self, item_id, task_text, category, is_completed, is_custom, notes, **kwargs):
        super().__init__(**kwargs)
        self.item_id = item_id
        self.task_text = task_text
        self.category = category
        self.is_completed = is_completed
        self.is_custom = is_custom
        self.notes = notes
        
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = "80dp"
        self.padding = "10dp"
        self.spacing = "10dp"
        
        # Use standard Kivy CheckBox
        self.checkbox = CheckBox(
            size_hint=(None, None),
            size=("30dp", "30dp"),
            active=bool(is_completed)
        )
        self.checkbox.bind(active=self.on_checkbox_active)
        self.add_widget(self.checkbox)
        
        self.task_label = MDLabel(
            text=task_text,
            size_hint_x=0.5,
            halign="left",
            valign="center",
            theme_text_color="Primary"
        )
        self.add_widget(self.task_label)
        
        self.notes_btn = MDFlatButton(
            text="Notes",
            theme_text_color="Custom",
            text_color=MDApp.get_running_app().theme_cls.primary_color,
            on_release=self.show_notes_dialog,
            size_hint=(None, None),
            size=("60dp", "40dp")
        )
        self.add_widget(self.notes_btn)
        
        if is_custom:
            self.delete_btn = MDFlatButton(
                text="Delete",
                theme_text_color="Custom",
                text_color=MDApp.get_running_app().theme_cls.error_color,
                on_release=self.delete_item,
                size_hint=(None, None),
                size=("60dp", "40dp")
            )
            self.add_widget(self.delete_btn)
        
        # Set initial state
        self.update_visual_state()
    
    def update_visual_state(self):
        if self.checkbox.active:
            self.task_label.text = f"[s]{self.task_text}[/s]"
            self.md_bg_color = (0.95, 0.95, 0.95, 1)
        else:
            self.task_label.text = self.task_text
            self.md_bg_color = (1, 1, 1, 1)
    
    def on_checkbox_active(self, checkbox, value):
        app = MDApp.get_running_app()
        checklist_manager = ChecklistManager(app.current_project_id)
        success = checklist_manager.update_item_status(self.item_id, value)
        
        if success:
            self.update_visual_state()
        else:
            app.show_toast("Failed to update task")
            # Revert checkbox state
            checkbox.active = not value
    
    def show_notes_dialog(self, instance):
        app = MDApp.get_running_app()
        
        def update_notes_callback(notes):
            checklist_manager = ChecklistManager(app.current_project_id)
            if checklist_manager.update_item_notes(self.item_id, notes):
                self.notes = notes
                app.show_toast("Notes updated!")
            else:
                app.show_toast("Failed to update notes")
        
        notes_dialog = NotesDialog(app, self.task_text, self.notes, update_notes_callback)
        notes_dialog.open()
    
    def delete_item(self, instance):
        app = MDApp.get_running_app()
        confirmation = ConfirmationDialog(
            app,
            "Delete Task",
            "Are you sure you want to delete this task?",
            lambda: self._perform_delete(app)
        )
        confirmation.open()
    
    def _perform_delete(self, app):
        checklist_manager = ChecklistManager(app.current_project_id)
        if checklist_manager.delete_custom_item(self.item_id):
            checklist_screen = app.root.get_screen('checklist')
            checklist_screen.load_checklist_items()
            app.show_toast("Task deleted!")
        else:
            app.show_toast("Failed to delete task")


class ChecklistScreen(MDScreen):
    project_name = StringProperty("Project")
    current_category = StringProperty("All")
    
    def on_enter(self):
        self.load_checklist_items()
    
    def load_categories(self):
        app = MDApp.get_running_app()
        if not app.current_project_id:
            return
            
        checklist_manager = ChecklistManager(app.current_project_id)
        categories = checklist_manager.get_categories()
        
        self.ids.categories_container.clear_widgets()
        
        # Add "All" category chip
        all_chip = MDChip(
            text="All",
            on_release=lambda x: self.filter_by_category("All")
        )
        if self.current_category == "All":
            all_chip.md_bg_color = app.theme_cls.primary_color
            all_chip.text_color = (1, 1, 1, 1)
        self.ids.categories_container.add_widget(all_chip)
        
        for category in categories:
            chip = MDChip(
                text=category,
                on_release=lambda x, cat=category: self.filter_by_category(cat)
            )
            if self.current_category == category:
                chip.md_bg_color = app.theme_cls.primary_color
                chip.text_color = (1, 1, 1, 1)
            self.ids.categories_container.add_widget(chip)
    
    def filter_by_category(self, category):
        self.current_category = category
        self.load_checklist_items()
        self.load_categories()
    
    def load_checklist_items(self):
        app = MDApp.get_running_app()
        self.ids.checklist_list.clear_widgets()
        
        if not app.current_project_id:
            empty_label = OneLineListItem(text="No project selected")
            self.ids.checklist_list.add_widget(empty_label)
            return
        
        app.show_loading("Loading tasks...")
        Clock.schedule_once(lambda dt: self._load_items_async(), 0.1)
    
    def _load_items_async(self):
        app = MDApp.get_running_app()
        checklist_manager = ChecklistManager(app.current_project_id)
        items = checklist_manager.get_checklist_items(self.current_category)
        
        app.hide_loading()
        self.ids.checklist_list.clear_widgets()
        
        if not items:
            empty_label = OneLineListItem(
                text="No tasks in this category",
                theme_text_color="Secondary"
            )
            self.ids.checklist_list.add_widget(empty_label)
        else:
            for item in items:
                container = MDCard(
                    orientation='vertical',
                    size_hint_y=None,
                    height="80dp",
                    padding="10dp",
                    elevation=2
                )
                
                checklist_item = ChecklistItem(
                    item_id=item['id'],
                    task_text=item['task'],
                    category=item['category'],
                    is_completed=item['is_completed'],
                    is_custom=item['is_custom'],
                    notes=item['notes'] or ""
                )
                container.add_widget(checklist_item)
                self.ids.checklist_list.add_widget(container)
        
        # Update progress label
        self.update_progress_label()
        self.load_categories()
    
    def update_progress_label(self):
        app = MDApp.get_running_app()
        if not app.current_project_id:
            return
            
        stats_manager = StatsManager(app.current_project_id)
        stats = stats_manager.get_project_stats()
        
        if stats['total_tasks'] > 0:
            progress_text = f"Progress: {stats['completed_tasks']}/{stats['total_tasks']} tasks completed ({stats['overall_percentage']}%)"
            self.ids.progress_label.text = progress_text
        else:
            self.ids.progress_label.text = "No tasks yet"
    
    def add_custom_item(self):
        app = MDApp.get_running_app()
        if not app.current_project_id:
            app.show_toast("No project selected")
            return
            
        checklist_manager = ChecklistManager(app.current_project_id)
        categories = checklist_manager.get_categories()
        
        if not hasattr(app, 'add_item_dialog'):
            app.add_item_dialog = AddCustomItemDialog(app, categories, self.add_item_callback)
        app.add_item_dialog.open()
    
    def add_item_callback(self, category, task, due_date):
        app = MDApp.get_running_app()
        if not category or not task:
            app.show_toast("Category and task are required")
            return
        
        app.show_loading("Adding task...")
        Clock.schedule_once(lambda dt: self._add_item_async(category, task, due_date), 0.1)
    
    def _add_item_async(self, category, task, due_date):
        app = MDApp.get_running_app()
        checklist_manager = ChecklistManager(app.current_project_id)
        item_id, message = checklist_manager.add_custom_item(category, task, due_date)
        
        app.hide_loading()
        
        if item_id:
            self.load_checklist_items()
            app.show_toast("Task added!")
        else:
            app.show_toast(message)
    
    def show_stats(self):
        app = MDApp.get_running_app()
        if not app.current_project_id:
            app.show_toast("No project selected")
            return
            
        stats_manager = StatsManager(app.current_project_id)
        stats_data = stats_manager.get_project_stats()
        
        stats_dialog = StatsDialog(
            app, 
            stats_data, 
            lambda: self.export_data()
        )
        stats_dialog.open()
    
    def export_data(self):
        app = MDApp.get_running_app()
        if not app.current_project_id:
            app.show_toast("No project selected")
            return
        
        export_dialog = ExportDialog(
            app,
            self.project_name,
            self.export_format_selected
        )
        export_dialog.open()
    
    def export_format_selected(self, format_type):
        app = MDApp.get_running_app()
        
        # Create exports directory if it doesn't exist
        exports_dir = "exports"
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in self.project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        if format_type == 'csv':
            file_path = os.path.join(exports_dir, f"{safe_name}_{timestamp}.csv")
            success, message = self._export_to_csv(file_path)
        else:
            file_path = os.path.join(exports_dir, f"{safe_name}_{timestamp}.json")
            success, message = self._export_to_json(file_path)
        
        if success:
            app.show_toast(f"Exported to {file_path}")
        else:
            app.show_toast(message)
    
    def _export_to_csv(self, file_path):
        try:
            export_manager = ExportManager(app.current_project_id)
            return export_manager.export_to_csv(file_path)
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def _export_to_json(self, file_path):
        try:
            export_manager = ExportManager(app.current_project_id)
            return export_manager.export_to_json(file_path)
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def go_back(self):
        self.manager.current = 'projects'


class TheatreChecklistApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_manager = AuthManager()
        self.user_id = None
        self.current_project_id = None
        self.loading_dialog = None
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Amber"
        
        self.sm = MDScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(ProjectsScreen(name='projects'))
        self.sm.add_widget(ChecklistScreen(name='checklist'))
        return self.sm
    
    def show_toast(self, message):
        toast(message)
    
    def show_loading(self, message="Loading..."):
        if self.loading_dialog is None:
            self.loading_dialog = MDDialog(
                title=message,
                type="simple",
                auto_dismiss=False
            )
        else:
            self.loading_dialog.title = message
        
        self.loading_dialog.open()
    
    def hide_loading(self):
        if self.loading_dialog:
            self.loading_dialog.dismiss()
            self.loading_dialog = None

if __name__ == '__main__':
    TheatreChecklistApp().run()