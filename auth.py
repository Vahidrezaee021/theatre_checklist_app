import hashlib
import sqlite3
import re
import secrets
from database import DatabaseManager

class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None
    
    def hash_password(self, password):
        # Add pepper for additional security
        pepper = "theatre_app_pepper_2024"
        return hashlib.sha256((password + pepper).encode()).hexdigest()
    
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        return True, "OK"
    
    def is_email_taken(self, email):
        try:
            result = self.db.fetch_one("SELECT id FROM users WHERE email = ?", (email,))
            return result is not None
        except Exception as e:
            print(f"Error checking email: {e}")
            return True  # Assume taken to prevent duplicates
    
    def register_user(self, email, password):
        try:
            if not self.validate_email(email):
                return False, "Invalid email format"
            
            valid, message = self.validate_password(password)
            if not valid:
                return False, message
            
            if self.is_email_taken(email):
                return False, "Email already registered"
            
            self.db.execute_query(
                'INSERT INTO users (email, password_hash) VALUES (?, ?)',
                (email, self.hash_password(password))
            )
            
            return True, "Registration successful"
        except sqlite3.IntegrityError:
            return False, "Email already exists"
        except Exception as e:
            print(f"Registration error: {e}")
            return False, "Registration failed. Please try again."
    
    def login_user(self, email, password):
        try:
            result = self.db.fetch_one(
                'SELECT id, email FROM users WHERE email = ? AND password_hash = ?',
                (email, self.hash_password(password))
            )
            
            if result:
                self.current_user = {'id': result[0], 'email': result[1]}
                return True, "Login successful"
            else:
                return False, "Invalid email or password"
        except Exception as e:
            print(f"Login error: {e}")
            return False, "Login failed. Please try again."
    
    def logout(self):
        self.current_user = None
        return True