"""
Regular Expression Module for RAD-TUI v2.2.0
Provides pattern matching and text manipulation
"""

import re
from typing import List, Dict, Any, Optional, Iterator


class Match:
    """Represents a regex match result"""
    
    def __init__(self, match_obj=None, text: str = ""):
        self._match = match_obj
        self._text = text
        
        if match_obj:
            self.value = match_obj.group(0)
            self.position = match_obj.start()
            self.end_position = match_obj.end()
            self.length = len(self.value)
        else:
            self.value = ""
            self.position = -1
            self.end_position = -1
            self.length = 0
            
    def group(self, index: int = 0) -> str:
        """Get capture group by index"""
        if self._match:
            return self._match.group(index)
        return ""
        
    def groups(self) -> tuple:
        """Get all capture groups"""
        if self._match:
            return self._match.groups()
        return ()
        
    def group_dict(self) -> Dict[str, str]:
        """Get named capture groups as dictionary"""
        if self._match:
            return self._match.groupdict()
        return {}
        
    def is_valid(self) -> bool:
        """Check if match is valid"""
        return self._match is not None and self.position >= 0


class Regex:
    """Regular expression pattern"""
    
    # Flags
    CASE_INSENSITIVE = re.IGNORECASE
    MULTILINE = re.MULTILINE
    DOTALL = re.DOTALL
    VERBOSE = re.VERBOSE
    
    def __init__(self, pattern: str, flags: int = 0):
        self.pattern = pattern
        self.flags = flags
        self._compiled = None
        
        try:
            self._compiled = re.compile(pattern, flags)
        except re.error as e:
            self._error = str(e)
        else:
            self._error = None
            
    def is_valid(self) -> bool:
        """Check if pattern is valid"""
        return self._compiled is not None and self._error is None
        
    def get_error(self) -> Optional[str]:
        """Get compilation error message"""
        return self._error
        
    def search(self, text: str) -> Optional[Match]:
        """
        Search for first match in text
        
        Args:
            text: Text to search in
            
        Returns:
            Match object or None
        """
        if not self._compiled:
            return None
            
        match = self._compiled.search(text)
        if match:
            return Match(match, text)
        return None
        
    def match(self, text: str) -> Optional[Match]:
        """
        Match pattern at beginning of text
        
        Args:
            text: Text to match against
            
        Returns:
            Match object or None
        """
        if not self._compiled:
            return None
            
        match = self._compiled.match(text)
        if match:
            return Match(match, text)
        return None
        
    def fullmatch(self, text: str) -> Optional[Match]:
        """
        Match entire text against pattern
        
        Args:
            text: Text to match
            
        Returns:
            Match object or None
        """
        if not self._compiled:
            return None
            
        match = self._compiled.fullmatch(text)
        if match:
            return Match(match, text)
        return None
        
    def find_all(self, text: str) -> List[Match]:
        """
        Find all matches in text
        
        Args:
            text: Text to search in
            
        Returns:
            List of Match objects
        """
        if not self._compiled:
            return []
            
        matches = []
        for match_obj in self._compiled.finditer(text):
            matches.append(Match(match_obj, text))
            
        return matches
        
    def find_all_strings(self, text: str) -> List[str]:
        """
        Find all matches and return as strings
        
        Args:
            text: Text to search in
            
        Returns:
            List of matched strings
        """
        if not self._compiled:
            return []
            
        return self._compiled.findall(text)
        
    def replace(self, text: str, replacement: str, count: int = 0) -> str:
        """
        Replace matches with replacement string
        
        Args:
            text: Original text
            replacement: Replacement string (can use \\1, \\2 for groups)
            count: Maximum replacements (0 = all)
            
        Returns:
            Modified text
        """
        if not self._compiled:
            return text
            
        return self._compiled.sub(replacement, text, count)
        
    def replace_func(self, text: str, func: callable, count: int = 0) -> str:
        """
        Replace matches using function
        
        Args:
            text: Original text
            func: Function receiving Match, returning replacement string
            count: Maximum replacements (0 = all)
            
        Returns:
            Modified text
        """
        if not self._compiled:
            return text
            
        def wrapper(match_obj):
            match = Match(match_obj, text)
            return func(match)
            
        return self._compiled.sub(wrapper, text, count)
        
    def split(self, text: str, maxsplit: int = 0) -> List[str]:
        """
        Split text by pattern
        
        Args:
            text: Text to split
            maxsplit: Maximum splits (0 = all)
            
        Returns:
            List of parts
        """
        if not self._compiled:
            return [text]
            
        return self._compiled.split(text, maxsplit)
        
    def count(self, text: str) -> int:
        """
        Count matches in text
        
        Args:
            text: Text to count in
            
        Returns:
            Number of matches
        """
        if not self._compiled:
            return 0
            
        return len(self._compiled.findall(text))


# Utility functions

def regex_search(pattern: str, text: str, flags: int = 0) -> Optional[Match]:
    """
    Simple regex search function
    
    Args:
        pattern: Regex pattern
        text: Text to search
        flags: Optional flags
        
    Returns:
        Match or None
    """
    r = Regex(pattern, flags)
    return r.search(text)


def regex_match(pattern: str, text: str, flags: int = 0) -> Optional[Match]:
    """
    Simple regex match function
    
    Args:
        pattern: Regex pattern
        text: Text to match
        flags: Optional flags
        
    Returns:
        Match or None
    """
    r = Regex(pattern, flags)
    return r.match(text)


def regex_replace(pattern: str, text: str, replacement: str, 
                  flags: int = 0, count: int = 0) -> str:
    """
    Simple regex replace function
    
    Args:
        pattern: Regex pattern
        text: Original text
        replacement: Replacement string
        flags: Optional flags
        count: Maximum replacements
        
    Returns:
        Modified text
    """
    r = Regex(pattern, flags)
    return r.replace(text, replacement, count)


def regex_split(pattern: str, text: str, flags: int = 0, 
                maxsplit: int = 0) -> List[str]:
    """
    Simple regex split function
    
    Args:
        pattern: Regex pattern
        text: Text to split
        flags: Optional flags
        maxsplit: Maximum splits
        
    Returns:
        List of parts
    """
    r = Regex(pattern, flags)
    return r.split(text, maxsplit)


def is_valid_pattern(pattern: str) -> bool:
    """
    Check if regex pattern is valid
    
    Args:
        pattern: Pattern to validate
        
    Returns:
        True if valid
    """
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def escape_regex(text: str) -> str:
    """
    Escape special regex characters in text
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for use in pattern
    """
    return re.escape(text)


# Common patterns

PATTERNS = {
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}',
    'url': r'https?://[^\\s<>\"{}|\\\\^`\\[\\]]+',
    'ip': r'\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b',
    'phone': r'\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b',
    'date_iso': r'\\d{4}-\\d{2}-\\d{2}',
    'date_us': r'\\d{2}/\\d{2}/\\d{4}',
    'time': r'\\d{2}:\\d{2}:\\d{2}',
    'word': r'\\b\\w+\\b',
    'number': r'-?\\d+(?:\\.\\d+)?',
    'integer': r'-?\\d+',
    'whitespace': r'\\s+',
}


def match_pattern(pattern_name: str, text: str) -> Optional[Match]:
    """
    Match using predefined pattern
    
    Args:
        pattern_name: Name from PATTERNS dict
        text: Text to match
        
    Returns:
        Match or None
    """
    if pattern_name in PATTERNS:
        return regex_search(PATTERNS[pattern_name], text)
    return None


# String manipulation helpers

def extract_emails(text: str) -> List[str]:
    """Extract all email addresses from text"""
    r = Regex(PATTERNS['email'])
    return r.find_all_strings(text)


def extract_urls(text: str) -> List[str]:
    """Extract all URLs from text"""
    r = Regex(PATTERNS['url'])
    return r.find_all_strings(text)


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text"""
    r = Regex(PATTERNS['number'])
    matches = r.find_all_strings(text)
    return [float(m) for m in matches if m]


def remove_extra_whitespace(text: str) -> str:
    """Remove extra whitespace from text"""
    return regex_replace(r'\\s+', text, ' ').strip()


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text"""
    return regex_replace(r'<[^>]+>', text, '')
