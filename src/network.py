"""
Network/HTTP Module for RAD-TUI v2.2.0
Provides HTTP operations and network functionality
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, Optional, Callable, List, Tuple


class HttpResponse:
    """Represents an HTTP response"""
    
    def __init__(self):
        self.status_code = 0
        self.headers = {}
        self.body = ""
        self.url = ""
        self.error = None
        
    def json(self) -> Any:
        """
        Parse response body as JSON
        
        Returns:
            Parsed JSON data or None if parsing fails
        """
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            return None
            
    def is_success(self) -> bool:
        """Check if request was successful (2xx status)"""
        return 200 <= self.status_code < 300
        
    def is_redirect(self) -> bool:
        """Check if response is redirect (3xx status)"""
        return 300 <= self.status_code < 400
        
    def is_client_error(self) -> bool:
        """Check if client error (4xx status)"""
        return 400 <= self.status_code < 500
        
    def is_server_error(self) -> bool:
        """Check if server error (5xx status)"""
        return 500 <= self.status_code < 600


class HttpRequest:
    """HTTP request configuration"""
    
    def __init__(self, method: str = "GET", url: str = "", 
                 headers: Dict[str, str] = None, 
                 body: str = None, timeout: int = 30):
        self.method = method.upper()
        self.url = url
        self.headers = headers or {}
        self.body = body
        self.timeout = timeout
        
    def add_header(self, key: str, value: str):
        """Add header to request"""
        self.headers[key] = value
        
    def set_json_body(self, data: Any):
        """Set JSON body from data"""
        self.body = json.dumps(data)
        self.headers['Content-Type'] = 'application/json'


class NetworkManager:
    """Manages HTTP operations and network state"""
    
    def __init__(self):
        self.default_headers = {
            'User-Agent': 'RAD-TUI/2.2.0'
        }
        self.timeout = 30
        self.follow_redirects = True
        
        # Events
        self.on_request_complete = None
        self.on_request_error = None
        self.on_download_progress = None
        
    def request(self, http_request: HttpRequest) -> HttpResponse:
        """
        Execute HTTP request
        
        Args:
            http_request: HttpRequest configuration
            
        Returns:
            HttpResponse with result
        """
        response = HttpResponse()
        response.url = http_request.url
        
        try:
            # Prepare request
            req = urllib.request.Request(
                http_request.url,
                data=http_request.body.encode('utf-8') if http_request.body else None,
                headers={**self.default_headers, **http_request.headers},
                method=http_request.method
            )
            
            # Execute request
            with urllib.request.urlopen(req, timeout=http_request.timeout) as resp:
                response.status_code = resp.getcode()
                response.headers = dict(resp.headers)
                response.body = resp.read().decode('utf-8')
                
            if self.on_request_complete:
                self.on_request_complete(http_request, response)
                
            return response
            
        except urllib.error.HTTPError as e:
            response.status_code = e.code
            response.headers = dict(e.headers)
            response.body = e.read().decode('utf-8')
            response.error = f"HTTP Error {e.code}: {e.reason}"
            
            if self.on_request_error:
                self.on_request_error(http_request, response.error)
                
            return response
            
        except urllib.error.URLError as e:
            response.error = f"URL Error: {e.reason}"
            
            if self.on_request_error:
                self.on_request_error(http_request, response.error)
                
            return response
            
        except Exception as e:
            response.error = f"Error: {str(e)}"
            
            if self.on_request_error:
                self.on_request_error(http_request, response.error)
                
            return response
            
    def get(self, url: str, headers: Dict[str, str] = None, 
            timeout: int = 30) -> HttpResponse:
        """
        Execute GET request
        
        Args:
            url: URL to request
            headers: Optional headers
            timeout: Request timeout in seconds
            
        Returns:
            HttpResponse
        """
        req = HttpRequest("GET", url, headers, timeout=timeout)
        return self.request(req)
        
    def post(self, url: str, data: Any = None, 
             headers: Dict[str, str] = None,
             timeout: int = 30) -> HttpResponse:
        """
        Execute POST request
        
        Args:
            url: URL to request
            data: Data to send (will be JSON encoded if dict/list)
            headers: Optional headers
            timeout: Request timeout
            
        Returns:
            HttpResponse
        """
        body = None
        if data:
            if isinstance(data, (dict, list)):
                body = json.dumps(data)
                headers = headers or {}
                headers['Content-Type'] = 'application/json'
            else:
                body = str(data)
                
        req = HttpRequest("POST", url, headers, body, timeout)
        return self.request(req)
        
    def put(self, url: str, data: Any = None,
            headers: Dict[str, str] = None,
            timeout: int = 30) -> HttpResponse:
        """Execute PUT request"""
        body = json.dumps(data) if isinstance(data, (dict, list)) else str(data) if data else None
        req = HttpRequest("PUT", url, headers, body, timeout)
        return self.request(req)
        
    def delete(self, url: str, headers: Dict[str, str] = None,
               timeout: int = 30) -> HttpResponse:
        """Execute DELETE request"""
        req = HttpRequest("DELETE", url, headers, timeout=timeout)
        return self.request(req)
        
    def download_file(self, url: str, local_path: str,
                     on_progress: Callable[[int, int], None] = None,
                     chunk_size: int = 8192) -> bool:
        """
        Download file with progress callback
        
        Args:
            url: URL to download from
            local_path: Local file path to save to
            on_progress: Callback(loaded_bytes, total_bytes)
            chunk_size: Download chunk size
            
        Returns:
            True if download successful
        """
        try:
            req = urllib.request.Request(url, headers=self.default_headers)
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                with open(local_path, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                            
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if on_progress:
                            on_progress(downloaded, total_size)
                            
                        if self.on_download_progress:
                            self.on_download_progress(downloaded, total_size)
                            
            return True
            
        except Exception as e:
            if self.on_request_error:
                self.on_request_error(None, str(e))
            return False
            
    def upload_file(self, url: str, file_path: str,
                   field_name: str = "file",
                   additional_fields: Dict[str, str] = None) -> HttpResponse:
        """
        Upload file via multipart/form-data
        
        Args:
            url: Upload URL
            file_path: Path to file to upload
            field_name: Form field name for file
            additional_fields: Additional form fields
            
        Returns:
            HttpResponse
        """
        import mimetypes
        
        boundary = '----RAD_TUI_Boundary'
        
        # Build multipart body
        body_parts = []
        
        # Add additional fields
        if additional_fields:
            for key, value in additional_fields.items():
                body_parts.append(f'--{boundary}\\r\\n')
                body_parts.append(f'Content-Disposition: form-data; name="{key}"\\r\\n\\r\\n')
                body_parts.append(f'{value}\\r\\n')
                
        # Add file
        filename = file_path.split('/')[-1].split('\\\\')[-1]
        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        body_parts.append(f'--{boundary}\\r\\n')
        body_parts.append(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\\r\\n')
        body_parts.append(f'Content-Type: {content_type}\\r\\n\\r\\n')
        
        # Read file
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        # Build body
        body = ''.join(body_parts).encode('utf-8') + file_content + f'\\r\\n--{boundary}--\\r\\n'.encode('utf-8')
        
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body))
        }
        
        req = HttpRequest("POST", url, headers, body.decode('utf-8'))
        return self.request(req)
        
    def set_default_header(self, key: str, value: str):
        """Set default header for all requests"""
        self.default_headers[key] = value
        
    def clear_default_headers(self):
        """Clear all default headers"""
        self.default_headers = {}


# Convenience functions

def http_get(url: str, headers: Dict[str, str] = None) -> HttpResponse:
    """Simple GET request"""
    nm = NetworkManager()
    return nm.get(url, headers)


def http_post(url: str, data: Any, headers: Dict[str, str] = None) -> HttpResponse:
    """Simple POST request"""
    nm = NetworkManager()
    return nm.post(url, data, headers)


def fetch_json(url: str) -> Any:
    """
    Fetch and parse JSON from URL
    
    Args:
        url: URL to fetch
        
    Returns:
        Parsed JSON data or None
    """
    response = http_get(url)
    return response.json() if response.is_success() else None


def download_with_progress(url: str, local_path: str, 
                          progress_callback: Callable[[int, int], None]):
    """
    Download file with progress
    
    Args:
        url: URL to download
        local_path: Local file path
        progress_callback: Function(loaded, total)
    """
    nm = NetworkManager()
    return nm.download_file(url, local_path, progress_callback)


# URL utilities

def encode_url_params(params: Dict[str, str]) -> str:
    """Encode dictionary as URL query string"""
    return urllib.parse.urlencode(params)


def build_url(base: str, params: Dict[str, str] = None) -> str:
    """
    Build URL with query parameters
    
    Args:
        base: Base URL
        params: Query parameters
        
    Returns:
        Complete URL
    """
    if params:
        separator = '&' if '?' in base else '?'
        return f"{base}{separator}{encode_url_params(params)}"
    return base


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
