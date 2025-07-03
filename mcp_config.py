import json
import yaml
from typing import Dict, Any

class MCPConfig:
    def __init__(self, config_path: str = "mcp_servers.yaml"):
        self.config_path = config_path
        self.servers = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load MCP server configurations"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self.create_default_config()
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create default MCP server configuration"""
        default_config = {
            "servers": {
                "filesystem": {
                    "url": "http://localhost:8001",
                    "description": "File system operations",
                    "enabled": True
                },
                "web_scraper": {
                    "url": "http://localhost:8002", 
                    "description": "Web scraping and content extraction",
                    "enabled": True
                },
                "database": {
                    "url": "http://localhost:8003",
                    "description": "Database operations",
                    "enabled": False
                }
            }
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        return default_config
    
    def add_server(self, name: str, url: str, description: str = ""):
        """Add new MCP server to configuration"""
        self.servers["servers"][name] = {
            "url": url,
            "description": description,
            "enabled": True
        }
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.servers, f, default_flow_style=False)
