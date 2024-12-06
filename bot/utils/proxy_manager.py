import json
import os
from typing import Dict, Optional

class ProxyManager:
    def __init__(self):
        self.proxy_file = "bot/config/proxy_bindings.json"
        self.proxy_bindings: Dict[str, str] = {}
        self.load_bindings()

    def load_bindings(self) -> None:
        """Load proxy bindings from file if it exists"""
        if os.path.exists(self.proxy_file):
            try:
                with open(self.proxy_file, 'r') as f:
                    self.proxy_bindings = json.load(f)
            except json.JSONDecodeError:
                self.proxy_bindings = {}
        else:
            self.proxy_bindings = {}

    def save_bindings(self) -> None:
        """Save proxy bindings to file"""
        os.makedirs(os.path.dirname(self.proxy_file), exist_ok=True)
        with open(self.proxy_file, 'w') as f:
            json.dump(self.proxy_bindings, f, indent=4)

    def get_proxy(self, session_name: str) -> Optional[str]:
        """Get proxy for session"""
        return self.proxy_bindings.get(session_name)

    def set_proxy(self, session_name: str, proxy: str) -> None:
        """Set proxy for session"""
        self.proxy_bindings[session_name] = proxy
        self.save_bindings()

    def remove_proxy(self, session_name: str) -> None:
        """Remove proxy binding for session"""
        if session_name in self.proxy_bindings:
            del self.proxy_bindings[session_name]
            self.save_bindings() 