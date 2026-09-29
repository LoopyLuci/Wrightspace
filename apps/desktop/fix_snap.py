import sys

with open('webbuilder/gui/__init__.py', 'r') as f:
    content = f.read()

# Replace handle_chat_snap_request
old_chat = """    def handle_chat_snap_request(self, chat_window, snap: bool | None = None):
        \"\"\"Handle snap/unsnap request from Chat window.
        
        Args:
            chat_window: The ChatWindow requesting the snap
            snap: True to snap in, False to unsnap out, None to toggle
        \"\"\"
        try:
            from webbuilder.gui.chat_window import ChatDockWidget
            if snap is None:
                # Toggle based on current state
                snap = not chat_window._is_snapped
            
            if snap:
                # Snap chat into main window
                if not chat_window._chat_dock:
                    chat_window._chat_dock = ChatDockWidget(self)
                    chat_window._chat_dock.chat_window = chat_window
                    central = chat_window.centralWidget()
                    if central:
                        chat_window._chat_dock.setWidget(central)
                
                chat_window._chat_dock.setFeatures(
                    QDockWidget.DockWidgetMovable |
                    QDockWidget.DockWidgetFloatable |
                    QDockWidget.DockWidgetClosable
                )
                chat_window._chat_dock.setAllowedAreas(
                    Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea
                )
                self.addDockWidget(Qt.RightDockWidgetArea, chat_window._chat_dock)
                chat_window._main_window_ref = self
                chat_window._is_snapped = True
                chat_window._chat_dock.show()
                logger.debug("Chat snapped to main window")
            else:
                # Unsnap chat from main window
                if chat_window._chat_dock and chat_window._main_window_ref:
                    self.removeDockWidget(chat_window._chat_dock)
                    chat_window._chat_dock.setParent(None)
                    chat_window._chat_dock = None
                    chat_window._main_window_ref = None
                    chat_window._is_snapped = False
                    chat_window.show()
                    chat_window.raise_()
                    chat_window.activateWindow()
                    logger.debug("Chat unsnapped from main window")
        except Exception as e:
            logger.error(f"Chat snap request failed: {e}")"""

new_chat = """    def handle_chat_snap_request(self, chat_window, snap: bool | None = None):
        \"\"\"Handle snap/unsnap request from Chat window.
        
        Args:
            chat_window: The ChatWindow requesting the snap
            snap: True to snap in, False to unsnap out, None to toggle
        \"\"\"
        try:
            if snap is None:
                # Toggle based on current state
                snap = not chat_window._snap_state.is_snapped
            
            if snap:
                # Snap chat into main window
                chat_window._snap_state.set_main_window(self)
                success = chat_window._snap_state.snap_to(self)
                if success:
                    chat_window._is_snapped = True
                    logger.debug("Chat snapped to main window")
            else:
                # Unsnap chat from main window
                success = chat_window._snap_state.unsnap_from(self)
                if success:
                    chat_window._is_snapped = False
                    chat_window.show()
                    chat_window.raise_()
                    chat_window.activateWindow()
                    logger.debug("Chat unsnapped from main window")
        except Exception as e:
            logger.error(f"Chat snap request failed: {e}")"""

# Replace handle_properties_snap_request
old_props = """    def handle_properties_snap_request(self, props_window, snap: bool | None = None):
        \"\"\"Handle snap/unsnap request from Properties window.
        
        Args:
            props_window: The PropertiesWindow requesting the snap
            snap: True to snap in, False to unsnap out, None to toggle
        \"\"\"
        try:
            from webbuilder.gui.properties_window import PropertiesDockWidget
            if snap is None:
                snap = not props_window._is_snapped
            
            if snap:
                if not props_window._props_dock:
                    props_window._props_dock = PropertiesDockWidget(self)
                    props_window._props_dock.properties_widget = props_window.properties_widget
                
                props_window._props_dock.setFeatures(
                    QDockWidget.DockWidgetMovable |
                    QDockWidget.DockWidgetFloatable |
                    QDockWidget.DockWidgetClosable
                )
                props_window._props_dock.setAllowedAreas(
                    Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea
                )
                self.addDockWidget(Qt.RightDockWidgetArea, props_window._props_dock)
                props_window._main_window_ref = self
                props_window._is_snapped = True
                props_window._props_dock.show()
                logger.debug("Properties snapped to main window")
            else:
                if props_window._props_dock and props_window._main_window_ref:
                    self.removeDockWidget(props_window._props_dock)
                    props_window._props_dock.setParent(None)
                    props_window._props_dock = None
                    props_window._main_window_ref = None
                    props_window._is_snapped = False
                    props_window.show()
                    props_window.raise_()
                    props_window.activateWindow()
                    logger.debug("Properties unsnapped from main window")
        except Exception as e:
            logger.error(f"Properties snap request failed: {e}")"""

new_props = """    def handle_properties_snap_request(self, props_window, snap: bool | None = None):
        \"\"\"Handle snap/unsnap request from Properties window.
        
        Args:
            props_window: The PropertiesWindow requesting the snap
            snap: True to snap in, False to unsnap out, None to toggle
        \"\"\"
        try:
            if snap is None:
                snap = not props_window._snap_state.is_snapped
            
            if snap:
                # Snap properties into main window
                props_window._snap_state.set_main_window(self)
                success = props_window._snap_state.snap_to(self)
                if success:
                    props_window._is_snapped = True
                    logger.debug("Properties snapped to main window")
            else:
                # Unsnap properties from main window
                success = props_window._snap_state.unsnap_from(self)
                if success:
                    props_window._is_snapped = False
                    props_window.show()
                    props_window.raise_()
                    props_window.activateWindow()
                    logger.debug("Properties unsnapped from main window")
        except Exception as e:
            logger.error(f"Properties snap request failed: {e}")"""

# Replace _snap_window_to_main
old_snap = """    def _snap_window_to_main(self, window):
        \"\"\"Snap a window into the main window as a dock widget.
        
        Args:
            window: ChatWindow or PropertiesWindow to snap
        \"\"\"
        try:
            if isinstance(window, ChatWindow):
                self.handle_chat_snap_request(window, snap=True)
            elif isinstance(window, PropertiesWindow):
                self.handle_properties_snap_request(window, snap=True)
        except Exception as e:
            logger.error(f"Snap window failed: {e}")"""

new_snap = """    def _snap_window_to_main(self, window):
        \"\"\"Snap a window into the main window as a dock widget.
        
        Args:
            window: ChatWindow or PropertiesWindow to snap
        \"\"\"
        try:
            if isinstance(window, ChatWindow):
                window._snap_state.set_main_window(self)
                success = window._snap_state.snap_to(self)
                if success:
                    window._is_snapped = True
            elif isinstance(window, PropertiesWindow):
                window._snap_state.set_main_window(self)
                success = window._snap_state.snap_to(self)
                if success:
                    window._is_snapped = True
        except Exception as e:
            logger.error(f"Snap window failed: {e}")"""

if old_chat in content:
    content = content.replace(old_chat, new_chat)
    print("Replaced handle_chat_snap_request")
else:
    print("Pattern not found: handle_chat_snap_request")

if old_props in content:
    content = content.replace(old_props, new_props)
    print("Replaced handle_properties_snap_request")
else:
    print("Pattern not found: handle_properties_snap_request")

if old_snap in content:
    content = content.replace(old_snap, new_snap)
    print("Replaced _snap_window_to_main")
else:
    print("Pattern not found: _snap_window_to_main")

with open('webbuilder/gui/__init__.py', 'w') as f:
    f.write(content)
print("Done")
PYEOF