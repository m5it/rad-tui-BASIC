"""
TreeView Control Module for RAD-TUI v2.2.0
Provides hierarchical tree display with expandable nodes
"""

class TreeNode:
    """Represents a node in the TreeView"""
    
    def __init__(self, text="", icon="", parent=None):
        self.text = text
        self.icon = icon  # Single character icon
        self.parent = parent
        self.children = []
        self.expanded = False
        self.selected = False
        self.tag = None  # User data
        self.visible = True
        
    def add_child(self, text, icon=""):
        """Add a child node"""
        child = TreeNode(text, icon, self)
        self.children.append(child)
        return child
        
    def remove_child(self, child):
        """Remove a child node"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            
    def expand(self):
        """Expand this node to show children"""
        self.expanded = True
        
    def collapse(self):
        """Collapse this node to hide children"""
        self.expanded = False
        
    def toggle(self):
        """Toggle expanded/collapsed state"""
        self.expanded = not self.expanded
        
    def has_children(self):
        """Check if node has children"""
        return len(self.children) > 0
        
    def get_level(self):
        """Get nesting level (0 = root)"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level


class TreeView:
    """TreeView control for hierarchical data display"""
    
    TOOL_TYPE = 17
    
    def __init__(self, name_id="treeView1", x=0, y=0, width=30, height=10):
        self.name_id = name_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.caption = ""
        
        # Tree data
        self.root_nodes = []
        self.selected_node = None
        
        # Appearance
        self.indent_size = 2
        self.show_icons = True
        self.show_lines = True  # Show tree lines
        self.expand_char = "+"  # Collapsed indicator
        self.collapse_char = "-"  # Expanded indicator
        self.leaf_char = " "   # No children indicator
        
        # Events
        self.on_node_click = None
        self.on_node_expand = None
        self.on_node_collapse = None
        self.on_node_select = None
        
        # State
        self.scroll_offset = 0
        self.visible_nodes = []  # Flattened visible nodes
        
    def add_root_node(self, text, icon=""):
        """Add a root-level node"""
        node = TreeNode(text, icon)
        self.root_nodes.append(node)
        self._update_visible_nodes()
        return node
        
    def remove_node(self, node):
        """Remove a node and all its children"""
        if node in self.root_nodes:
            self.root_nodes.remove(node)
        elif node.parent:
            node.parent.remove_child(node)
            
        if self.selected_node == node:
            self.selected_node = None
            
        self._update_visible_nodes()
        
    def clear(self):
        """Remove all nodes"""
        self.root_nodes = []
        self.selected_node = None
        self.visible_nodes = []
        
    def expand_node(self, node):
        """Expand a node"""
        if node.has_children():
            node.expand()
            self._update_visible_nodes()
            if self.on_node_expand:
                self.on_node_expand(node)
                
    def collapse_node(self, node):
        """Collapse a node"""
        if node.has_children():
            node.collapse()
            self._update_visible_nodes()
            if self.on_node_collapse:
                self.on_node_collapse(node)
                
    def toggle_node(self, node):
        """Toggle node expanded/collapsed state"""
        if node.has_children():
            if node.expanded:
                self.collapse_node(node)
            else:
                self.expand_node(node)
                
    def select_node(self, node):
        """Select a node"""
        if self.selected_node:
            self.selected_node.selected = False
            
        self.selected_node = node
        if node:
            node.selected = True
            if self.on_node_select:
                self.on_node_select(node)
                
    def get_selected(self):
        """Get currently selected node"""
        return self.selected_node
        
    def _update_visible_nodes(self):
        """Update flattened list of visible nodes"""
        self.visible_nodes = []
        
        def add_visible(node, level):
            node.visible_level = level
            self.visible_nodes.append(node)
            if node.expanded:
                for child in node.children:
                    add_visible(child, level + 1)
                    
        for root in self.root_nodes:
            add_visible(root, 0)
            
    def get_node_at_index(self, index):
        """Get node at visible index"""
        if 0 <= index < len(self.visible_nodes):
            return self.visible_nodes[index]
        return None
        
    def get_node_index(self, node):
        """Get visible index of node"""
        try:
            return self.visible_nodes.index(node)
        except ValueError:
            return -1
            
    def handle_click(self, x, y):
        """Handle mouse click at position"""
        # Calculate which node was clicked
        row = y - self.y
        if row < 0 or row >= len(self.visible_nodes):
            return False
            
        node = self.visible_nodes[row + self.scroll_offset]
        if not node:
            return False
            
        # Check if click was on expand/collapse indicator
        level = node.visible_level
        indent = level * self.indent_size
        
        if x == self.x + indent and node.has_children():
            self.toggle_node(node)
            return True
            
        # Select the node
        self.select_node(node)
        
        if self.on_node_click:
            self.on_node_click(node)
            
        return True
        
    def scroll_up(self):
        """Scroll view up"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            
    def scroll_down(self):
        """Scroll view down"""
        if self.scroll_offset < len(self.visible_nodes) - self.height:
            self.scroll_offset += 1
            
    def render(self, screen):
        """Render the TreeView to screen"""
        if not self.visible_nodes:
            self._update_visible_nodes()
            
        for row in range(self.height):
            node_index = row + self.scroll_offset
            
            if node_index < len(self.visible_nodes):
                node = self.visible_nodes[node_index]
                self._render_node(screen, node, row)
            else:
                # Clear remaining rows
                self._clear_row(screen, row)
                
    def _render_node(self, screen, node, row):
        """Render a single node"""
        y = self.y + row
        level = node.visible_level
        indent = level * self.indent_size
        
        # Build line content
        line = ""
        
        # Expand/collapse indicator or space
        if node.has_children():
            line += self.collapse_char if node.expanded else self.expand_char
        else:
            line += self.leaf_char
            
        line += " "
        
        # Icon
        if self.show_icons and node.icon:
            line += node.icon + " "
            
        # Text
        line += node.text
        
        # Truncate if too long
        max_width = self.width - indent - 2
        if len(line) > max_width:
            line = line[:max_width-3] + "..."
            
        # Output with indentation
        x_pos = self.x + indent
        
        # Highlight if selected
        if node.selected:
            # In real implementation, would use reverse video or color
            pass
            
        # Place on screen (implementation depends on screen buffer)
        # This is a placeholder - actual implementation uses curses
        pass
        
    def _clear_row(self, screen, row):
        """Clear a row in the tree view area"""
        y = self.y + row
        # Clear line (implementation depends on screen)
        pass


# Utility functions for common tree operations

def find_node_by_text(treeview, text, recursive=True):
    """Find first node matching text"""
    def search_nodes(nodes):
        for node in nodes:
            if node.text == text:
                return node
            if recursive and node.children:
                found = search_nodes(node.children)
                if found:
                    return found
        return None
        
    return search_nodes(treeview.root_nodes)


def expand_all_nodes(treeview):
    """Expand all nodes in tree"""
    def expand_recursive(node):
        if node.has_children():
            node.expand()
            for child in node.children:
                expand_recursive(child)
                
    for root in treeview.root_nodes:
        expand_recursive(root)
        
    treeview._update_visible_nodes()


def collapse_all_nodes(treeview):
    """Collapse all nodes in tree"""
    def collapse_recursive(node):
        if node.has_children():
            node.collapse()
            for child in node.children:
                collapse_recursive(child)
                
    for root in treeview.root_nodes:
        collapse_recursive(root)
        
    treeview._update_visible_nodes()
