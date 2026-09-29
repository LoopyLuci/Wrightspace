class StateManager:
    def __init__(self):
        self._panels = {}
        self._window_state = None
        self._recovery_points = []

    def save_state(self, window, project_name=""):
        try:
            self._window_state = {
                "geometry": {
                    "x": window.x(),
                    "y": window.y(),
                    "width": window.width(),
                    "height": window.height(),
                },
                "project_path": project_name,
            }
            window.saveState()
            return True
        except Exception:
            return False

    def restore_state(self, window):
        if self._window_state:
            g = self._window_state["geometry"]
            window.setGeometry(g.get("x", 0), g.get("y", 0), g.get("width", 800), g.get("height", 600))
            return True
        return False

    def set_panel_state(self, name, visible=True):
        self._panels[name] = {"name": name, "visible": visible}

    def get_panel_state(self, name):
        return self._panels.get(name)

    def get_recovery_points(self):
        return self._recovery_points
