class PanelState:
    def __init__(self, name="", visible=True):
        self.name = name
        self.visible = visible

    def to_dict(self):
        return {"name": self.name, "visible": self.visible}
