import os
from typing import Optional
import json


class FileSystemTool:
    """Tool for file system operations"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
    
    def write(self, path: str, content: str) -> dict:
        """Write content to file"""
        full_path = os.path.join(self.base_path, path)
        
        # Create directory if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                "action": "write",
                "path": path,
                "status": "success",
                "size": len(content)
            }
        except Exception as e:
            return {
                "action": "write",
                "path": path,
                "status": "error",
                "error": str(e)
            }
    
    def read(self, path: str) -> dict:
        """Read content from file"""
        full_path = os.path.join(self.base_path, path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "action": "read",
                "path": path,
                "status": "success",
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {
                "action": "read",
                "path": path,
                "status": "error",
                "error": str(e)
            }
    
    def exists(self, path: str) -> bool:
        """Check if file exists"""
        full_path = os.path.join(self.base_path, path)
        return os.path.exists(full_path)
    
    def delete(self, path: str) -> dict:
        """Delete a file"""
        full_path = os.path.join(self.base_path, path)
        
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
                return {
                    "action": "delete",
                    "path": path,
                    "status": "success"
                }
            else:
                return {
                    "action": "delete",
                    "path": path,
                    "status": "error",
                    "error": "File not found"
                }
        except Exception as e:
            return {
                "action": "delete",
                "path": path,
                "status": "error",
                "error": str(e)
            }
    
    def list_dir(self, path: str = ".") -> dict:
        """List directory contents"""
        full_path = os.path.join(self.base_path, path)
        
        try:
            entries = os.listdir(full_path)
            return {
                "action": "list_dir",
                "path": path,
                "status": "success",
                "entries": entries
            }
        except Exception as e:
            return {
                "action": "list_dir",
                "path": path,
                "status": "error",
                "error": str(e)
            }
    
    def write_json(self, path: str, data: dict) -> dict:
        """Write JSON data to file"""
        try:
            content = json.dumps(data, indent=2, ensure_ascii=False)
            return self.write(path, content)
        except Exception as e:
            return {
                "action": "write_json",
                "path": path,
                "status": "error",
                "error": str(e)
            }
    
    def read_json(self, path: str) -> dict:
        """Read JSON data from file"""
        result = self.read(path)
        if result['status'] == 'success':
            try:
                data = json.loads(result['content'])
                result['data'] = data
            except Exception as e:
                result['status'] = 'error'
                result['error'] = f"JSON parse error: {str(e)}"
        return result
