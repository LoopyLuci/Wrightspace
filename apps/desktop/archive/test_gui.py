"""GUI verification script"""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from desktop_app import WebBuilderApp
window = WebBuilderApp()
print('=== GUI VERIFICATION ===')
print(f'Title: {window.windowTitle()}')
print(f'Min size: {window.minimumSize().width()}x{window.minimumSize().height()}')
print(f'Current size: {window.size().width()}x{window.size().height()}')
print()
print(f'Tabs: {window.tabs.count()}')
for i in range(window.tabs.count()):
    tab = window.tabs.widget(i)
    print(f'  Tab {i} ({window.tabs.tabText(i)}): {type(tab).__name__}')
print()
print(f'Format tabs: {window.format_tabs.count()}')
print(f'Chat tabs: {window.chat_tabs.count()}')
for i in range(window.chat_tabs.count()):
    print(f'  Chat tab {i}: {window.chat_tabs.tabText(i)}')
print()
print(f'Menu bar: {window.menuBar().count()} menus')
for i in range(window.menuBar().count()):
    print(f'  Menu {i}: {window.menuBar().menuAction(i).text()}')
print()
print('✅ GUI verification complete')
