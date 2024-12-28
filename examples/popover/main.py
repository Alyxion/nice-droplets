from nicegui import ui
from nice_droplets import dui
import re

def check_password_requirements(password: str) -> dict:
    requirements = {
        'length': len(password) >= 8,
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'lowercase': bool(re.search(r'[a-z]', password)),
        'number': bool(re.search(r'\d', password)),
        'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    }
    return requirements

@ui.page('/')
async def index():
    # Username input with popover
    with ui.input(label='Username', on_change=lambda e: update_username_validation(e.value)) as username_input:
        with dui.Popover(docking_side='bottom left') as username_popover:
            with ui.element().style('background-color: #f5f5f5; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: 1px solid black;'):
                ui.label('Username requirements:').style('font-weight: bold; margin-bottom: 0.5rem;')
                ui.label('• Only letters, numbers, and underscores')
                ui.label('• Must start with a letter')
                ui.label('• Length between 3-20 characters')
                username_validation_label = ui.label('')
    
    # Password input with requirements checklist
    with ui.input(label='Password', password=True, on_change=lambda e: update_password_validation(e.value)) as password_input:
        with dui.Popover(docking_side='bottom left') as password_popover:
            with ui.element().style('background-color: #f5f5f5; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: 1px solid black;'):
                ui.label('Password requirements:').style('font-weight: bold; margin-bottom: 0.5rem;')
                requirement_labels = {
                    'length': ui.label('❌ At least 8 characters'),
                    'uppercase': ui.label('❌ At least one uppercase letter'),
                    'lowercase': ui.label('❌ At least one lowercase letter'),
                    'number': ui.label('❌ At least one number'),
                    'special': ui.label('❌ At least one special character')
                }

    def update_username_validation(username: str):
        if not username:
            username_validation_label.text = ''
            return
        
        valid = bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,19}$', username))
        if valid:
            username_validation_label.text = '✅ Username is valid'
            username_validation_label.style('color: green')
        else:
            username_validation_label.text = '❌ Username does not meet requirements'
            username_validation_label.style('color: red')

    def update_password_validation(password: str):
        if not password:
            for label in requirement_labels.values():
                label.text = label.text.replace('✅', '❌')
            return

        requirements = check_password_requirements(password)
        requirement_texts = {
            'length': 'At least 8 characters',
            'uppercase': 'At least one uppercase letter',
            'lowercase': 'At least one lowercase letter',
            'number': 'At least one number',
            'special': 'At least one special character'
        }

        for req, is_met in requirements.items():
            icon = '✅' if is_met else '❌'
            requirement_labels[req].text = f'{icon} {requirement_texts[req]}'

ui.run()
