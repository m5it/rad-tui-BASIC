"""
Database Module for RAD-TUI v2.2.0
Provides SQLite database connectivity and operations
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple


class QueryResult:
    """Represents the result of a database query"""
    
    def __init__(self, rows=None, columns=None, error=None):
        self.rows = rows or []
        self.columns = columns or []
        self.error = error
        self.row_count = len(self.rows)
        self.column_count = len(self.columns)
        
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert rows to list of dictionaries"""
        result = []
        for row in self.rows:
            row_dict = {}
            for i, col in enumerate(self.columns):
                row_dict[col] = row[i]
            result.append(row_dict)
        return result
        
    def get_value(self, row_index: int, column: str) -> Any:
        """Get value from specific row and column"""
        if 0 <= row_index < len(self.rows):
            col_index = self.columns.index(column) if column in self.columns else -1
            if col_index >= 0:
                return self.rows[row_index][col_index]
        return None
        
    def first(self) -> Optional[Tuple]:
        """Get first row"""
        return self.rows[0] if self.rows else None
        
    def is_empty(self) -> bool:
        """Check if result has no rows"""
        return len(self.rows) == 0


class Database:
    """Database connection and operations manager"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.database_path = None
        self.connected = False
        self.in_transaction = False
        
        # Events
        self.on_query_complete = None
        self.on_error = None
        
    def connect(self, database_path: str) -> bool:
        """
        Connect to SQLite database
        
        Args:
            database_path: Path to SQLite database file
            
        Returns:
            True if connection successful
        """
        try:
            self.connection = sqlite3.connect(database_path)
            self.cursor = self.connection.cursor()
            self.database_path = database_path
            self.connected = True
            
            # Enable foreign keys
            self.execute_non_query("PRAGMA foreign_keys = ON")
            
            return True
            
        except sqlite3.Error as e:
            self._handle_error(f"Connection error: {e}")
            return False
            
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            if self.in_transaction:
                self.rollback()
            self.cursor.close()
            self.connection.close()
            self.connection = None
            self.cursor = None
            self.connected = False
            
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connected and self.connection is not None
        
    def execute_query(self, sql: str, parameters: tuple = None) -> QueryResult:
        """
        Execute SELECT query
        
        Args:
            sql: SQL query string
            parameters: Query parameters (for parameterized queries)
            
        Returns:
            QueryResult with rows and columns
        """
        if not self.is_connected():
            return QueryResult(error="Not connected to database")
            
        try:
            if parameters:
                self.cursor.execute(sql, parameters)
            else:
                self.cursor.execute(sql)
                
            # Get column names
            columns = [description[0] for description in self.cursor.description] if self.cursor.description else []
            
            # Fetch all rows
            rows = self.cursor.fetchall()
            
            result = QueryResult(rows=rows, columns=columns)
            
            if self.on_query_complete:
                self.on_query_complete(sql, result)
                
            return result
            
        except sqlite3.Error as e:
            self._handle_error(f"Query error: {e}")
            return QueryResult(error=str(e))
            
    def execute_non_query(self, sql: str, parameters: tuple = None) -> int:
        """
        Execute non-SELECT query (INSERT, UPDATE, DELETE)
        
        Args:
            sql: SQL statement
            parameters: Statement parameters
            
        Returns:
            Number of rows affected
        """
        if not self.is_connected():
            return -1
            
        try:
            if parameters:
                self.cursor.execute(sql, parameters)
            else:
                self.cursor.execute(sql)
                
            if not self.in_transaction:
                self.connection.commit()
                
            return self.cursor.rowcount
            
        except sqlite3.Error as e:
            self._handle_error(f"Execution error: {e}")
            return -1
            
    def get_tables(self) -> List[str]:
        """Get list of tables in database"""
        result = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in result.rows] if not result.error else []
        
    def get_columns(self, table_name: str) -> List[Dict[str, str]]:
        """
        Get column information for a table
        
        Returns:
            List of dicts with 'name', 'type', 'notnull', 'default', 'pk'
        """
        result = self.execute_query(f"PRAGMA table_info({table_name})")
        
        columns = []
        for row in result.rows:
            columns.append({
                'cid': row[0],
                'name': row[1],
                'type': row[2],
                'notnull': row[3],
                'default': row[4],
                'pk': row[5]
            })
            
        return columns
        
    def get_table_schema(self, table_name: str) -> str:
        """Get CREATE TABLE statement for table"""
        result = self.execute_query(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return result.rows[0][0] if result.rows else ""
        
    def begin_transaction(self):
        """Begin database transaction"""
        if self.is_connected():
            self.in_transaction = True
            
    def commit(self):
        """Commit current transaction"""
        if self.is_connected() and self.in_transaction:
            self.connection.commit()
            self.in_transaction = False
            
    def rollback(self):
        """Rollback current transaction"""
        if self.is_connected() and self.in_transaction:
            self.connection.rollback()
            self.in_transaction = False
            
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        Insert row into table
        
        Args:
            table: Table name
            data: Dictionary of column names and values
            
        Returns:
            Row ID of inserted row or -1 on error
        """
        if not data:
            return -1
            
        columns = list(data.keys())
        values = list(data.values())
        
        placeholders = ', '.join(['?' for _ in values])
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        if self.execute_non_query(sql, tuple(values)) >= 0:
            return self.cursor.lastrowid
        return -1
        
    def update(self, table: str, data: Dict[str, Any], where: str, 
               where_params: tuple = None) -> int:
        """
        Update rows in table
        
        Args:
            table: Table name
            data: Dictionary of column names and values to update
            where: WHERE clause
            where_params: Parameters for WHERE clause
            
        Returns:
            Number of rows updated
        """
        if not data:
            return -1
            
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        values = list(data.values())
        
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        if where_params:
            values.extend(where_params)
            
        return self.execute_non_query(sql, tuple(values))
        
    def delete(self, table: str, where: str, 
               where_params: tuple = None) -> int:
        """
        Delete rows from table
        
        Args:
            table: Table name
            where: WHERE clause
            where_params: Parameters for WHERE clause
            
        Returns:
            Number of rows deleted
        """
        sql = f"DELETE FROM {table} WHERE {where}"
        return self.execute_non_query(sql, where_params)
        
    def _handle_error(self, message: str):
        """Handle database error"""
        if self.on_error:
            self.on_error(message)
            
    def __enter__(self):
        """Context manager entry"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Utility functions

def create_in_memory_database() -> Database:
    """Create in-memory database for testing"""
    db = Database()
    db.connect(":memory:")
    return db


def escape_identifier(name: str) -> str:
    """
    Escape SQL identifier (table/column name)
    
    Args:
        name: Identifier to escape
        
    Returns:
        Escaped identifier
    """
    # Replace double quotes with two double quotes
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


def validate_sql(sql: str) -> Tuple[bool, str]:
    """
    Basic SQL validation
    
    Args:
        sql: SQL to validate
        
    Returns:
        (is_valid, error_message)
    """
    # Check for dangerous operations
    dangerous = ['DROP DATABASE', 'DELETE FROM', 'TRUNCATE']
    
    sql_upper = sql.upper()
    for danger in dangerous:
        if danger in sql_upper:
            return False, f"Potentially dangerous operation detected: {danger}"
            
    return True, ""


def create_sample_database(db: Database):
    """
    Create sample database with test data
    
    Args:
        db: Connected Database instance
    """
    # Create tables
    db.execute_non_query("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    db.execute_non_query("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL,
            category TEXT,
            stock INTEGER DEFAULT 0
        )
    """)
    
    # Insert sample data
    sample_users = [
        ('Alice Johnson', 'alice@example.com', 28),
        ('Bob Smith', 'bob@example.com', 35),
        ('Carol White', 'carol@example.com', 42),
        ('David Brown', 'david@example.com', 31),
    ]
    
    for user in sample_users:
        db.execute_non_query(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            user
        )
        
    sample_products = [
        ('Laptop', 999.99, 'Electronics', 15),
        ('Mouse', 29.99, 'Electronics', 100),
        ('Keyboard', 79.99, 'Electronics', 50),
        ('Desk Chair', 249.99, 'Furniture', 20),
        ('Coffee Mug', 12.99, 'Kitchen', 200),
    ]
    
    for product in sample_products:
        db.execute_non_query(
            "INSERT INTO products (name, price, category, stock) VALUES (?, ?, ?, ?)",
            product
        )
        
    db.commit()
