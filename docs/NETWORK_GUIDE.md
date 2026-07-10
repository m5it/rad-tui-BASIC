# Network Operations Guide for RAD-TUI v2.2.0

## Table of Contents

1. [Introduction](#introduction)
2. [Making HTTP Requests](#making-http-requests)
3. [Handling Responses](#handling-responses)
4. [Working with JSON APIs](#working-with-json-apis)
5. [File Downloads](#file-downloads)
6. [File Uploads](#file-uploads)
7. [Error Handling](#error-handling)
8. [Authentication](#authentication)
9. [Practical Examples](#practical-examples)
10. [Best Practices](#best-practices)

---

## Introduction

RAD-TUI v2.2.0 includes a comprehensive network module for HTTP operations. This guide covers everything from simple GET requests to complex API integrations.

### Features

- HTTP methods: GET, POST, PUT, DELETE
- JSON automatic parsing
- File upload/download with progress
- Custom headers and timeouts
- Error handling
- Authentication support

---

## Making HTTP Requests

### Simple GET Request

```python
from network import NetworkManager, http_get

# Method 1: Using convenience function
response = http_get("https://api.example.com/users")

# Method 2: Using NetworkManager
nm = NetworkManager()
response = nm.get("https://api.example.com/users")

# Check if successful
if response.is_success():
    print(response.body)
```

### POST Request with Data

```python
# POST with form data
data = {"username": "john", "password": "secret"}
response = nm.post("https://api.example.com/login", data)

# POST with JSON (automatic)
user_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin"
}
response = nm.post("https://api.example.com/users", user_data)
```

### Other HTTP Methods

```python
# PUT request (update)
update_data = {"status": "active"}
response = nm.put("https://api.example.com/users/123", update_data)

# DELETE request
response = nm.delete("https://api.example.com/users/123")

# Check status
if response.status_code == 204:
    print("User deleted successfully")
```

### Custom Headers

```python
headers = {
    "Accept": "application/json",
    "X-API-Key": "your-api-key",
    "User-Agent": "MyApp/1.0"
}

response = nm.get("https://api.example.com/data", headers=headers)

# Set default headers for all requests
nm.set_default_header("Authorization", "Bearer token123")
response = nm.get("https://api.example.com/protected")
```

### Timeout Configuration

```python
# Set timeout for specific request (seconds)
response = nm.get("https://slow-api.com", timeout=60)

# Or use NetworkManager default
nm.timeout = 30  # Default 30 seconds
```

---

## Handling Responses

### Response Properties

```python
response = nm.get("https://api.example.com/users")

# Status information
print(f"Status: {response.status_code}")
print(f"Success: {response.is_success()}")
print(f"URL: {response.url}")

# Response body
print(f"Body: {response.body}")

# Headers
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"All headers: {response.headers}")
```

### Status Code Helpers

```python
if response.is_success():      # 200-299
    print("Request succeeded")
    
elif response.is_redirect():   # 300-399
    print("Redirect received")
    
elif response.is_client_error(): # 400-499
    print(f"Client error: {response.status_code}")
    
elif response.is_server_error(): # 500-599
    print(f"Server error: {response.status_code}")
```

### Error Handling

```python
response = nm.get("https://api.example.com/data")

if response.error:
    print(f"Error: {response.error}")
    
elif not response.is_success():
    print(f"HTTP Error {response.status_code}")
    print(f"Response: {response.body}")
    
else:
    # Process successful response
    process_data(response.body)
```

---

## Working with JSON APIs

### Automatic JSON Parsing

```python
response = nm.get("https://api.example.com/users")

# Parse JSON
data = response.json()

if data:
    for user in data:
        print(f"{user['name']} - {user['email']}")
```

### Working with Nested Data

```python
response = nm.get("https://api.example.com/orders/123")
order = response.json()

if order:
    print(f"Order ID: {order['id']}")
    print(f"Customer: {order['customer']['name']}")
    print("Items:")
    for item in order['items']:
        print(f"  - {item['product']}: ${item['price']}")
```

### POST with JSON Response

```python
new_user = {
    "name": "Jane Smith",
    "email": "jane@example.com"
}

response = nm.post("https://api.example.com/users", new_user)

if response.is_success():
    created_user = response.json()
    print(f"Created user ID: {created_user['id']}")
```

### Fetch Helper Function

```python
def fetch_json(url, default=None):
    """Fetch JSON with error handling"""
    response = nm.get(url)
    if response.is_success():
        return response.json()
    return default

# Usage
users = fetch_json("https://api.example.com/users", [])
for user in users:
    print(user['name'])
```

---

## File Downloads

### Basic Download

```python
success = nm.download_file(
    "https://example.com/file.pdf",
    "downloads/file.pdf"
)

if success:
    print("Download complete")
else:
    print("Download failed")
```

### Download with Progress

```python
from progressbar import ProgressBar

# Create progress bar
progress = ProgressBar(name_id="dlProgress", width=40)
progress.set_range(0, 100)

def on_progress(loaded, total):
    """Update progress bar"""
    if total > 0:
        percent = int(loaded / total * 100)
        progress.set_value(percent)
        print(f"\\rDownloading: {percent}%", end="")

# Download with progress callback
success = nm.download_file(
    "https://example.com/large-file.zip",
    "downloads/file.zip",
    on_progress=on_progress
)

print("\\nDownload complete!")
```

### Download with NetworkManager Events

```python
nm = NetworkManager()

def on_download_progress(loaded, total):
    percent = loaded / total * 100 if total > 0 else 0
    print(f"Progress: {percent:.1f}%")

# Set event handler
nm.on_download_progress = on_download_progress

# Download
nm.download_file(
    "https://example.com/file.zip",
    "local/file.zip"
)
```

### Batch Downloads

```python
files = [
    ("https://site.com/file1.pdf", "downloads/file1.pdf"),
    ("https://site.com/file2.pdf", "downloads/file2.pdf"),
    ("https://site.com/file3.pdf", "downloads/file3.pdf"),
]

for url, local_path in files:
    print(f"Downloading {url}...")
    success = nm.download_file(url, local_path)
    if success:
        print("  ✓ Complete")
    else:
        print("  ✗ Failed")
```

---

## File Uploads

### Simple Upload

```python
response = nm.upload_file(
    "https://api.example.com/upload",
    "documents/report.pdf",
    field_name="document"
)

if response.is_success():
    result = response.json()
    print(f"Uploaded: {result['file_url']}")
```

### Upload with Additional Fields

```python
additional_fields = {
    "title": "Q4 Report",
    "category": "financial",
    "tags": "quarterly,2024"
}

response = nm.upload_file(
    "https://api.example.com/upload",
    "documents/report.pdf",
    field_name="document",
    additional_fields=additional_fields
)
```

### Upload Progress (when implemented)

```python
def on_upload_progress(sent, total):
    percent = sent / total * 100
    print(f"Uploading: {percent:.1f}%")

# Future implementation
response = nm.upload_file(
    "https://api.example.com/upload",
    "large-file.zip",
    on_progress=on_upload_progress
)
```

---

## Error Handling

### Try-Except Pattern

```python
try:
    response = nm.get("https://api.example.com/data")
    
    if response.error:
        handle_network_error(response.error)
    elif response.status_code == 404:
        handle_not_found()
    elif response.status_code == 401:
        handle_unauthorized()
    elif not response.is_success():
        handle_http_error(response.status_code)
    else:
        process_data(response.json())
        
except Exception as e:
    handle_exception(e)
```

### NetworkManager Events

```python
nm = NetworkManager()

def on_request_complete(request, response):
    """Called after every request"""
    print(f"{request.method} {request.url} -> {response.status_code}")

def on_request_error(request, error):
    """Called on request errors"""
    print(f"Request failed: {error}")

nm.on_request_complete = on_request_complete
nm.on_request_error = on_request_error

# Now all requests will trigger events
response = nm.get("https://api.example.com/data")
```

### Retry Logic

```python
def fetch_with_retry(url, max_retries=3):
    """Fetch with automatic retry"""
    for attempt in range(max_retries):
        response = nm.get(url)
        
        if response.is_success():
            return response
            
        if response.status_code in [500, 502, 503, 504]:
            # Server error, retry
            print(f"Attempt {attempt + 1} failed, retrying...")
            import time
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            # Client error, don't retry
            break
            
    return response

# Usage
response = fetch_with_retry("https://api.example.com/data")
```

---

## Authentication

### API Key Authentication

```python
# Method 1: Header
nm.set_default_header("X-API-Key", "your-secret-key")

# Method 2: Query parameter
from network import build_url

url = build_url(
    "https://api.example.com/data",
    {"api_key": "your-secret-key"}
)
response = nm.get(url)
```

### Bearer Token Authentication

```python
# Set authorization header
token = "your-jwt-token"
nm.set_default_header("Authorization", f"Bearer {token}")

# Now all requests include the token
response = nm.get("https://api.example.com/protected")
```

### Basic Authentication (when implemented)

```python
import base64

credentials = base64.b64encode(b"username:password").decode()
nm.set_default_header("Authorization", f"Basic {credentials}")
```

### OAuth Flow (simplified)

```python
def authenticate_oauth(client_id, client_secret, token_url):
    """OAuth2 client credentials flow"""
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    response = nm.post(token_url, auth_data)
    
    if response.is_success():
        token_data = response.json()
        access_token = token_data["access_token"]
        nm.set_default_header("Authorization", f"Bearer {access_token}")
        return True
        
    return False

# Authenticate
if authenticate_oauth("client_id", "secret", "https://oauth.server/token"):
    # Now make authenticated requests
    data = nm.get("https://api.example.com/data")
```

---

## Practical Examples

### Weather App

```python
class WeatherApp:
    def __init__(self):
        self.nm = NetworkManager()
        self.api_key = "your-weather-api-key"
        
    def get_weather(self, city):
        """Fetch weather for a city"""
        url = build_url(
            "https://api.weather.com/v1/current",
            {
                "city": city,
                "appid": self.api_key,
                "units": "metric"
            }
        )
        
        response = self.nm.get(url)
        
        if response.is_success():
            data = response.json()
            return {
                "city": data["name"],
                "temp": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"]
            }
        return None
        
    def display_weather(self, city):
        """Display weather in UI"""
        weather = self.get_weather(city)
        
        if weather:
            print(f"Weather in {weather['city']}:")
            print(f"  Temperature: {weather['temp']}°C")
            print(f"  Conditions: {weather['description']}")
            print(f"  Humidity: {weather['humidity']}%")
        else:
            print(f"Could not fetch weather for {city}")

# Usage
app = WeatherApp()
app.display_weather("London")
```

### News Reader

```python
class NewsReader:
    def __init__(self):
        self.nm = NetworkManager()
        self.api_key = "news-api-key"
        
    def fetch_headlines(self, category="general", count=10):
        """Fetch news headlines"""
        url = build_url(
            "https://newsapi.org/v2/top-headlines",
            {
                "category": category,
                "pageSize": count,
                "apiKey": self.api_key
            }
        )
        
        response = self.nm.get(url)
        
        if response.is_success():
            data = response.json()
            return data.get("articles", [])
        return []
        
    def display_headlines(self, articles):
        """Display articles in list"""
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   Source: {article['source']['name']}")
            print(f"   {article['description'][:100]}...")
            print()

# Usage
reader = NewsReader()
articles = reader.fetch_headlines("technology", 5)
reader.display_headlines(articles)
```

### File Sync Application

```python
class FileSync:
    def __init__(self, server_url):
        self.nm = NetworkManager()
        self.server = server_url
        
    def sync_file(self, local_path):
        """Upload file to server"""
        filename = local_path.split("/")[-1]
        
        # Check if file exists on server
        check_url = f"{self.server}/files/{filename}"
        check_response = self.nm.get(check_url)
        
        if check_response.status_code == 404:
            # File doesn't exist, upload it
            print(f"Uploading {filename}...")
            
            response = self.nm.upload_file(
                f"{self.server}/upload",
                local_path,
                field_name="file"
            )
            
            return response.is_success()
        else:
            print(f"{filename} already exists")
            return True
            
    def sync_directory(self, local_dir):
        """Sync all files in directory"""
        import os
        
        for filename in os.listdir(local_dir):
            local_path = os.path.join(local_dir, filename)
            if os.path.isfile(local_path):
                self.sync_file(local_path)
```

### REST API Client

```python
class APIClient:
    def __init__(self, base_url, api_key=None):
        self.nm = NetworkManager()
        self.base_url = base_url
        
        if api_key:
            self.nm.set_default_header("X-API-Key", api_key)
            
    def get(self, endpoint):
        """GET request"""
        url = f"{self.base_url}{endpoint}"
        return self.nm.get(url)
        
    def post(self, endpoint, data):
        """POST request"""
        url = f"{self.base_url}{endpoint}"
        return self.nm.post(url, data)
        
    def put(self, endpoint, data):
        """PUT request"""
        url = f"{self.base_url}{endpoint}"
        return self.nm.put(url, data)
        
    def delete(self, endpoint):
        """DELETE request"""
        url = f"{self.base_url}{endpoint}"
        return self.nm.delete(url)

# Usage
client = APIClient("https://api.example.com", "my-api-key")

# CRUD operations
users = client.get("/users").json()
new_user = client.post("/users", {"name": "John"}).json()
updated = client.put("/users/1", {"name": "Johnny"}).json()
client.delete("/users/1")
```

---

## Best Practices

### Performance

1. **Reuse NetworkManager**: Don't create new instances for every request
2. **Set appropriate timeouts**: Balance between reliability and responsiveness
3. **Use connection pooling**: When available
4. **Limit concurrent requests**: Don't overwhelm servers

### Security

1. **Never hardcode credentials**: Use environment variables
2. **Use HTTPS**: Always for production
3. **Validate SSL certificates**: Don't disable verification
4. **Sanitize inputs**: Before using in URLs

### Error Handling

1. **Always check responses**: Don't assume success
2. **Handle timeouts**: Network can be unreliable
3. **Log errors**: For debugging
4. **Provide user feedback**: Don't fail silently

### Data Handling

1. **Validate JSON**: Before accessing properties
2. **Handle missing fields**: Use .get() with defaults
3. **Check content type**: Ensure expected format
4. **Limit response size**: For large downloads

---

## Common Patterns

### Caching Responses

```python
import json
import time

class CachedAPI:
    def __init__(self, cache_duration=300):
        self.nm = NetworkManager()
        self.cache = {}
        self.cache_duration = cache_duration
        
    def get(self, url):
        """Get with caching"""
        now = time.time()
        
        # Check cache
        if url in self.cache:
            data, timestamp = self.cache[url]
            if now - timestamp < self.cache_duration:
                return data
                
        # Fetch fresh data
        response = self.nm.get(url)
        if response.is_success():
            data = response.json()
            self.cache[url] = (data, now)
            return data
            
        return None
```

### Rate Limiting

```python
import time

class RateLimitedClient:
    def __init__(self, requests_per_second=1):
        self.nm = NetworkManager()
        self.min_interval = 1.0 / requests_per_second
        self.last_request = 0
        
    def request(self, method, url, **kwargs):
        """Rate-limited request"""
        # Wait if needed
        elapsed = time.time() - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
            
        # Make request
        if method == "GET":
            response = self.nm.get(url, **kwargs)
        elif method == "POST":
            response = self.nm.post(url, **kwargs)
        # ... etc
            
        self.last_request = time.time()
        return response
```

### Request Builder

```python
class RequestBuilder:
    def __init__(self, base_url):
        self.nm = NetworkManager()
        self.base_url = base_url
        self.headers = {}
        self.params = {}
        
    def with_header(self, key, value):
        self.headers[key] = value
        return self
        
    def with_param(self, key, value):
        self.params[key] = value
        return self
        
    def get(self, endpoint):
        url = build_url(f"{self.base_url}{endpoint}", self.params)
        return self.nm.get(url, headers=self.headers)

# Usage
response = (RequestBuilder("https://api.example.com")
    .with_header("Accept", "application/json")
    .with_param("limit", 10)
    .with_param("offset", 0)
    .get("/users"))
```

---

## Troubleshooting

### Connection Errors

```python
# Check if URL is valid
from network import is_valid_url

if not is_valid_url(url):
    print("Invalid URL format")

# Check connectivity
response = nm.get("https://httpbin.org/get", timeout=5)
if response.error:
    print("No internet connection")
```

### SSL/TLS Issues

```python
# For development only - disable SSL verification
# WARNING: Not secure for production!

import ssl
import urllib.request

# Create unverified context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Use with urllib (advanced usage)
```

### Debugging Requests

```python
# Print request details
def debug_request(nm, method, url, **kwargs):
    print(f"Request: {method} {url}")
    print(f"Headers: {nm.default_headers}")
    
    if method == "GET":
        response = nm.get(url, **kwargs)
    # ...
    
    print(f"Response: {response.status_code}")
    print(f"Headers: {response.headers}")
    return response
```

---

## Resources

- [HTTP Status Codes](https://httpstatuses.com/)
- [REST API Best Practices](https://restfulapi.net/)
- [JSON API Specification](https://jsonapi.org/)
- [RAD-TUI API Reference](API_REFERENCE_V22.md)

---

*Last Updated: 2025*
