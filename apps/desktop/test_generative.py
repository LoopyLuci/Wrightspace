#!/usr/bin/env python3
"""Test generative UI integration."""
import sys
sys.path.insert(0, '.')

from webbuilder.generative_ui import AgentCommandParser, UINode
from webbuilder.generative_ui.widget_factory import create_widget, WidgetFactory

# Test command parsing
parser = AgentCommandParser(None)
mutations = parser.parse('add button Submit')
print(f'Parsed: {len(mutations)} mutations')
m = mutations[0]
print(f'Type: {m.type}, Payload: {m.payload}')

# Test UINode creation
node_data = m.payload.get('node', {})
node = UINode.from_dict(node_data)
print(f'Node: id={node.id}, type={node.type}, props={node.props}')

# Test widget factory
widget = create_widget(node)
print(f'Widget: {type(widget).__name__}')
print(f'Widget text: {widget.text() if hasattr(widget, "text") else "N/A"}')

# Test more commands
for cmd in ['add label "Hello"', 'add input with placeholder "Enter..."']:
    mutations = parser.parse(cmd)
    if mutations:
        node = UINode.from_dict(mutations[0].payload.get('node', {}))
        widget = create_widget(node)
        print(f'{cmd} -> {type(widget).__name__}')

print('OK Generative UI integration working')
