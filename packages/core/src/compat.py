# WebBuilder Backward Compatibility System
# Ensures old projects always load and work

import json
from typing import Dict, Any


class CompatibilityManager:
    """Manages backward compatibility for project formats"""
    
    CURRENT_VERSION = "2.0.0"
    
    def __init__(self):
        self.migrations = {
            '1.0.0': self._migrate_v1_to_v2,
        }
    
    def ensure_compatible(self, project: Dict) -> Dict:
        """Ensure project is compatible with current version"""
        version = project.get('version', '1.0.0')
        
        if version == self.CURRENT_VERSION:
            return project
        
        # Apply migrations sequentially
        while version in self.migrations:
            project = self.migrations[version](project)
            version = project.get('version', self.CURRENT_VERSION)
        
        return project
    
    def _migrate_v1_to_v2(self, project: Dict) -> Dict:
        """Migrate v1 to v2 format"""
        if 'colors' in project and 'fonts' in project:
            project['design'] = {
                'colors': project.pop('colors'),
                'fonts': project.pop('fonts')
            }
        project['version'] = '2.0.0'
        return project


__all__ = ['CompatibilityManager']
