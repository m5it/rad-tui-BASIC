# Database Tutorial for RAD-TUI v2.2.0

## Table of Contents

1. [Getting Started](#getting-started)
2. [Connecting to a Database](#connecting-to-a-database)
3. [Executing Queries](#executing-queries)
4. [Parameterized Queries](#parameterized-queries)
5. [Transactions](#transactions)
6. [CRUD Operations](#crud-operations)
7. [Working with Results](#working-with-results)
8. [Schema Browser](#schema-browser)
9. [Complete Example](#complete-example)

---

## Getting Started

RAD-TUI v2.2.0 includes a built-in SQLite database module. This tutorial covers everything from basic connections to complete CRUD applications.

### Prerequisites

- RAD-TUI v2.2.0 or later
- Basic understanding of SQL
- A SQLite database file (or use in-memory database)

---

## Connecting to a Database

### Create a Database Connection

```python
# Import the Database class
from database import Database

# Create instance
db = Database()

# Connect to SQLite database file
if db.connect("myapp.db"):
    print("Connected successfully!")
else:
    print("Failed to connect")
```

### In-Memory Database (for testing)

```python
# Create temporary in-memory database
db = Database()
db.connect(":memory:")

# Database exists only while connected
# Useful for testing and prototyping
```

### Connection Status

```python
# Check if connected
if db.is_connected():
    print("Database is ready")
    
# Get current database path
print(f"Connected to: {db.database_path}")
```

---

## Executing Queries

### SELECT Queries

```python
# Simple query
result = db.execute_query("SELECT * FROM users")

if not result.error:
    # Access column names
    print(f"Columns: {result.columns}")
    
    # Iterate through rows
    for row in result.rows:
        print(f"ID: {row[0]}, Name: {row[1]}")
        
    print(f"Total rows: {result.row_count}")
```

### Non-SELECT Queries

```python
# INSERT
rows_affected = db.execute_non_query(
    "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')"
)
print(f"Inserted {rows_affected} row(s)")

# UPDATE
rows_affected = db.execute_non_query(
    "UPDATE users SET active = 1 WHERE id = 1"
)
print(f"Updated {rows_affected} row(s)")

# DELETE
rows_affected = db.execute_non_query(
    "DELETE FROM users WHERE id = 5"
)
print(f"Deleted {rows_affected} row(s)")
```

---

## Parameterized Queries

**Always use parameterized queries to prevent SQL injection!**

### Using Parameters

```python
# Safe parameterized query
user_id = 123  # This could come from user input
result = db.execute_query(
    "SELECT * FROM users WHERE id = ? AND active = ?",
    (user_id, 1)
)

# Multiple parameters
name = "John"
email = "john@example.com"
db.execute_non_query(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    (name, email)
)
```

### Why Parameterize?

```python
# DANGEROUS - Never do this!
user_input = "'; DROP TABLE users; --"
query = f"SELECT * FROM users WHERE name = '{user_input}'"  # NEVER!

# SAFE - Use parameters
result = db.execute_query(
    "SELECT * FROM users WHERE name = ?",
    (user_input,)  # Safely escaped
)
```

---

## Transactions

### Using Transactions

```python
# Begin transaction
db.begin_transaction()

try:
    # Multiple operations
    db.execute_non_query("INSERT INTO accounts (user_id, balance) VALUES (1, 100)")
    db.execute_non_query("UPDATE accounts SET balance = balance - 50 WHERE user_id = 1")
    db.execute_non_query("INSERT INTO transactions (amount) VALUES (50)")
    
    # Commit if all successful
    db.commit()
    print("Transaction committed")
    
except Exception as e:
    # Rollback on error
    db.rollback()
    print(f"Transaction rolled back: {e}")
```

### Context Manager (Python)

```python
# Using with statement (if available)
with Database() as db:
    db.connect("myapp.db")
    db.begin_transaction()
    # ... operations ...
    db.commit()  # Auto-committed on success
# Auto-disconnected
```

---

## CRUD Operations

### Create (Insert)

```python
# Using execute_non_query
db.execute_non_query(
    "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
    ("Laptop", 999.99, "Electronics")
)

# Get last inserted row ID
last_id = db.cursor.lastrowid
print(f"Created product with ID: {last_id}")

# Using convenience method
row_id = db.insert("products", {
    "name": "Mouse",
    "price": 29.99,
    "category": "Electronics",
    "stock": 100
})
```

### Read (Select)

```python
# Single record
result = db.execute_query("SELECT * FROM products WHERE id = ?", (1,))
if result.rows:
    product = result.rows[0]
    print(f"Product: {product[1]}, Price: ${product[2]}")

# Multiple records
result = db.execute_query("SELECT * FROM products WHERE category = ?", ("Electronics",))
for product in result.rows:
    print(f"{product[1]}: ${product[2]}")

# With pagination
page = 1
per_page = 10
offset = (page - 1) * per_page
result = db.execute_query(
    "SELECT * FROM products LIMIT ? OFFSET ?",
    (per_page, offset)
)
```

### Update

```python
# Using execute_non_query
db.execute_non_query(
    "UPDATE products SET price = ?, stock = ? WHERE id = ?",
    (899.99, 50, 1)
)

# Using convenience method
rows_updated = db.update(
    "products",
    {"price": 799.99, "stock": 75},
    "id = ?",
    (1,)
)
print(f"Updated {rows_updated} product(s)")
```

### Delete

```python
# Using execute_non_query
db.execute_non_query("DELETE FROM products WHERE id = ?", (5,))

# Using convenience method
rows_deleted = db.delete(
    "products",
    "category = ? AND stock = ?",
    ("Discontinued", 0)
)
print(f"Deleted {rows_deleted} product(s)")
```

---

## Working with Results

### Convert to Dictionaries

```python
result = db.execute_query("SELECT * FROM users")

# Convert rows to dictionaries
users = result.to_dict_list()
for user in users:
    print(f"{user['name']} ({user['email']})")
```

### Access Specific Values

```python
result = db.execute_query("SELECT * FROM users WHERE id = 1")

# Get first row
first = result.first()
if first:
    print(f"User: {first[1]}")

# Get specific value
name = result.get_value(0, "name")  # Row 0, column "name"
```

### Check for Empty Results

```python
result = db.execute_query("SELECT * FROM users WHERE active = 0")

if result.is_empty():
    print("No inactive users found")
else:
    print(f"Found {result.row_count} inactive users")
```

---

## Schema Browser

### List Tables

```python
tables = db.get_tables()
print(f"Database has {len(tables)} tables:")
for table in tables:
    print(f"  - {table}")
```

### Get Column Information

```python
columns = db.get_columns("users")
print("Columns in 'users' table:")
for col in columns:
    print(f"  {col['name']} ({col['type']})")
    if col['pk']:
        print("    * Primary Key")
    if col['notnull']:
        print("    * Not Null")
```

### Get Table Schema

```python
schema = db.get_table_schema("users")
print(f"CREATE TABLE statement:\\n{schema}")
```

### Building a Schema Tree

```python
# Create TreeView for schema browser
tree = TreeView(name_id="treeSchema", x=2, y=2, width=30, height=15)

# Add root
root = tree.add_root_node("Database", icon="D")

# Add tables
tables_node = root.add_child("Tables", icon="T")
for table_name in db.get_tables():
    table_node = tables_node.add_child(table_name, icon="t")
    
    # Add columns
    for col in db.get_columns(table_name):
        col_text = f"{col['name']} ({col['type']})"
        table_node.add_child(col_text, icon="c")

tree.expand_node(tables_node)
```

---

## Complete Example

### Simple Contact Manager

```python
class ContactManager:
    def __init__(self):
        self.db = Database()
        
    def initialize(self):
        """Create database and tables"""
        if not self.db.connect("contacts.db"):
            return False
            
        # Create contacts table
        self.db.execute_non_query("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        return True
        
    def add_contact(self, name, email, phone):
        """Add new contact"""
        return self.db.insert("contacts", {
            "name": name,
            "email": email,
            "phone": phone
        })
        
    def get_contacts(self, search=None):
        """Get all contacts or search"""
        if search:
            result = self.db.execute_query(
                "SELECT * FROM contacts WHERE name LIKE ? ORDER BY name",
                (f"%{search}%",)
            )
        else:
            result = self.db.execute_query(
                "SELECT * FROM contacts ORDER BY name"
            )
            
        return result.to_dict_list()
        
    def update_contact(self, contact_id, **kwargs):
        """Update contact"""
        return self.db.update(
            "contacts",
            kwargs,
            "id = ?",
            (contact_id,)
        )
        
    def delete_contact(self, contact_id):
        """Delete contact"""
        return self.db.delete(
            "contacts",
            "id = ?",
            (contact_id,)
        )
        
    def close(self):
        """Close database"""
        self.db.disconnect()

# Usage
manager = ContactManager()
if manager.initialize():
    # Add contacts
    manager.add_contact("John Doe", "john@example.com", "555-0100")
    manager.add_contact("Jane Smith", "jane@example.com", "555-0101")
    
    # List contacts
    contacts = manager.get_contacts()
    for contact in contacts:
        print(f"{contact['name']}: {contact['email']}")
    
    # Search
    results = manager.get_contacts(search="John")
    
    # Update
    manager.update_contact(1, phone="555-0200")
    
    # Delete
    manager.delete_contact(2)
    
    manager.close()
```

---

## Best Practices

1. **Always use parameterized queries** - Never concatenate SQL strings
2. **Close connections** - Use `disconnect()` when done
3. **Use transactions** - For multiple related operations
4. **Handle errors** - Check `result.error` after queries
5. **Index columns** - For better performance on large tables
6. **Limit results** - Use `LIMIT` for large datasets

---

## Common Patterns

### Search with Multiple Criteria

```python
def search_products(name=None, category=None, min_price=None):
    conditions = []
    params = []
    
    if name:
        conditions.append("name LIKE ?")
        params.append(f"%{name}%")
        
    if category:
        conditions.append("category = ?")
        params.append(category)
        
    if min_price:
        conditions.append("price >= ?")
        params.append(min_price)
        
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"SELECT * FROM products WHERE {where_clause}"
    return db.execute_query(query, tuple(params))
```

### Pagination

```python
def get_page(table, page=1, per_page=20):
    offset = (page - 1) * per_page
    
    # Get data
    data = db.execute_query(
        f"SELECT * FROM {table} LIMIT ? OFFSET ?",
        (per_page, offset)
    )
    
    # Get total count
    count = db.execute_query(f"SELECT COUNT(*) FROM {table}")
    total = count.rows[0][0]
    
    return {
        "data": data.to_dict_list(),
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page
    }
```

---

## Troubleshooting

### Common Issues

**"Database is locked"**
- Another process has the database open
- Ensure you call `disconnect()` when done

**"No such table"**
- Table doesn't exist
- Check your CREATE TABLE statements

**"UNIQUE constraint failed"**
- Trying to insert duplicate value in unique column
- Check for existing records first

**"FOREIGN KEY constraint failed"**
- Referenced record doesn't exist
- Ensure parent records exist before children

---

## Resources

- [SQLite Documentation](https://sqlite.org/docs.html)
- [SQL Tutorial](https://www.w3schools.com/sql/)
- [RAD-TUI API Reference](API_REFERENCE_V22.md)

---

*Last Updated: 2025*
