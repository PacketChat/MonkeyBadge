class MenuItem:
    def __init__(self, name, action=None, submenu=None):
        """
        :param name: Name of the menu item
        :param action: Function to execute when the item is selected
        :param submenu: Menu to display when a sub menu item is selected
        """
        self.name = name
        self.action = action
        self.submenu = submenu

    def execute(self):
        if self.submenu:
            return self.submenu
        if self.action:
            eval(self.action)
        return None

class Menu:
    def __init__(self, items, display_handler, title="Menu", parent=None):
        """
        Menu initializer function

        :param items: List of menu items
        :param display_handler: DisplayHandler object
        :param title: Menu title
        :param parent: Parent menu
        """
        self.items = items + [MenuItem("Back")] if parent else items
        self.selected = 0
        self.display_handler = display_handler
        self.parent = parent
        self.title = title
        self.top_index = 0  # Index of the top item displayed

    def move_up(self):
        """
        Move the selection up one item        
        """
        if self.selected > 0:
            self.selected -= 1
            if self.selected < self.top_index:
                self.top_index = self.selected
        self.update_display()

    def move_down(self):
        """
        Move the selection down one item
        """
        if self.selected < len(self.items) - 1:
            self.selected += 1
            if self.selected >= self.top_index + 5:
                self.top_index = self.selected - 4
        self.update_display()

    def select(self):
        """
        Select the current item
        """
        item = self.items[self.selected]
        if item.name == "Back":
            return self.parent
        return item.execute()

    def update_display(self):
        """
        Update the display with the current menu
        """
        lines = [self.title]
        display_range = self.items[self.top_index:self.top_index + 5]
        for i, item in enumerate(display_range):
            display_line = "* " + item.name if self.top_index + i == self.selected else "  " + item.name
            lines.append(display_line)
        self.display_handler.print_text(lines)

