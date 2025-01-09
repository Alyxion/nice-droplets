import re

from nicegui import ui
import nice_droplets.dui as dui

# Text Constants
USERNAME_REQUIREMENTS_TITLE = 'Username requirements:'
USERNAME_REQUIREMENTS = {
    'start_letter': 'Must start with a letter',
    'allowed_chars': 'Only letters, numbers, and underscores',
    'length': 'Length between 3-20 characters'
}
USERNAME_VALID_MESSAGE = '✅ Username is valid'
USERNAME_INVALID_MESSAGE = '❌ Username does not meet requirements'

PASSWORD_REQUIREMENTS_TITLE = 'Password requirements:'
PASSWORD_REQUIREMENTS = {
    'length': 'At least 8 characters',
    'uppercase': 'At least one uppercase letter',
    'lowercase': 'At least one lowercase letter',
    'number': 'At least one number',
    'special': 'At least one special character'
}

VALIDATION_ICONS = {
    'success': '✅',
    'error': '❌'
}

STYLE_TITLE = 'font-weight: bold; margin-bottom: 0.5rem;'

def check_password_requirements(password: str) -> dict:
    requirements = {
        'length': len(password) >= 8,
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'lowercase': bool(re.search(r'[a-z]', password)),
        'number': bool(re.search(r'\d', password)),
        'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    }
    return requirements

def check_username_requirements(username: str) -> dict:
    requirements = {
        'start_letter': bool(re.match(r'^[a-zA-Z]', username)),
        'allowed_chars': bool(re.match(r'^[a-zA-Z0-9_]+$', username)),
        'length': 3 <= len(username) <= 20
    }
    return requirements

@ui.page('/')
async def index():
    def update_username_validation(username: str):
        if not username:
            for label in username_requirement_labels.values():
                label.text = label.text.replace(VALIDATION_ICONS['success'], VALIDATION_ICONS['error'])
            return

        requirements = check_username_requirements(username)
        for req, is_met in requirements.items():
            icon = VALIDATION_ICONS['success'] if is_met else VALIDATION_ICONS['error']
            username_requirement_labels[req].text = f'{icon} {USERNAME_REQUIREMENTS[req]}'

    def update_password_validation(password: str):
        if not password:
            for label in requirement_labels.values():
                label.text = label.text.replace(VALIDATION_ICONS['success'], VALIDATION_ICONS['error'])
            return

        requirements = check_password_requirements(password)
        for req, is_met in requirements.items():
            icon = VALIDATION_ICONS['success'] if is_met else VALIDATION_ICONS['error']
            requirement_labels[req].text = f'{icon} {PASSWORD_REQUIREMENTS[req]}'

    # Username input with popover
    with ui.input(label='Username', on_change=lambda e: update_username_validation(e.value)):
        with dui.popover() as popover:
            ui.label(USERNAME_REQUIREMENTS_TITLE).style(STYLE_TITLE)
            username_requirement_labels = {
                key: ui.label(f'{VALIDATION_ICONS["error"]} {text}')
                for key, text in USERNAME_REQUIREMENTS.items()
            }

    # Password input with requirements checklist
    with ui.input(label='Password', password=True, on_change=lambda e: update_password_validation(e.value)):
        with dui.popover() as popover:
            ui.label(PASSWORD_REQUIREMENTS_TITLE).style(STYLE_TITLE)
            requirement_labels = {
                key: ui.label(f'{VALIDATION_ICONS["error"]} {text}')
                for key, text in PASSWORD_REQUIREMENTS.items()
            }

ui.run()
