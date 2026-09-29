class WindowState:
    def __init__(self, geometry=None, active_tab=0, project_path=""):
        self.geometry = geometry or {}
        self.active_tab = active_tab
        self.project_path = project_path

    def to_dict(self):
        return {
            "geometry": self.geometry,
            "active_tab": self.active_tab,
            "project_path": self.project_path,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            geometry=d.get("geometry", {}),
            active_tab=d.get("active_tab", 0),
            project_path=d.get("project_path", ""),
        )
