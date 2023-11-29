class MenuItem:
    def __init__(self, name,
                 action=None,
                 submenu=None,
                 dynamic_text=None):
        """
        :param name: Name of the menu item
        :param action: Function to execute when the item is selected
        :param submenu: Menu to display when a sub menu item is selected
        """
        self.name = name
        self.action = action
        self.submenu = submenu
        self.dynamic_text = dynamic_text

    def execute(self):
        if self.submenu:
            return self.submenu
        if self.action:
            result = self.action()
            if result is not None:
                return result
        return None

    def get_display_text(self):
        if self.dynamic_text:
            return self.dynamic_text()
        return self.name

class Menu:
    def __init__(self, items, title="Menu", parent=None):
        """
        Menu initializer function

        :param items: List of menu items
        :param display_handler: DisplayHandler object
        :param title: Menu title
        :param parent: Parent menu
        """
        self.items = [
                MenuItem("Back", self._back)
                ] + items if parent else items
        self.selected = 0
        self.parent = parent
        self.title = title
        self.top_index = 0  # Index of the top item displayed

    def _back(self):
        return self.parent

    def move_up(self):
        """
        Move the selection up one item
        """
        if self.selected > 0:
            self.selected -= 1
            if self.selected < self.top_index:
                self.top_index = self.selected
                print(f"{self.title}: {self.top_index}")

    def move_down(self):
        """
        Move the selection down one item
        """
        if self.selected < len(self.items) - 1:
            self.selected += 1
            if self.selected >= self.top_index + 4:
                self.top_index = self.selected - 3
                print(f"{self.title}: {self.top_index}")

    def select(self, index):
        """
        Set the selection
        """
        if 0 > index >= len(self.items):
            return
        self.selected = index

    def selection(self):
        """
        Select the current item
        """
        item = self.items[self.selected]
        return item.execute()
