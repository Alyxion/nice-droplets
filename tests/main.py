"""Main file for NiceGUI test server."""
from nicegui import ui


def main():
    """Entry point for test server."""
    ui.run(reload=False, show=False)


if __name__ == '__main__':
    main()
