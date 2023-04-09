

class MainSection:

    def __init__(self, code, description):
        self.code = code
        self.description = description

        self.sub_sections = []

    def __repr__(self):
        return '.'.join(self.code)


class SubSection:

    def __init__(self, code, description, category=None):
        self.code = code
        self.description = description
        self.category = category

        self.items = []

    def __repr__(self):
        return '.'.join(self.code)


class Item:

    def __init__(self, code, suffix, description, category=None):
        self.code = code
        self.suffix = suffix
        self.description = description
        self.category = category

    def __repr__(self):
        return '.'.join(self.code) + ' ' + self.suffix
