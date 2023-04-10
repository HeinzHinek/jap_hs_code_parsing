

class MainSection:

    def __init__(self, code, description):
        assert len(code) == 2
        assert all(len(part) == 2 for part in code)
        assert type(description) == str
        assert len(description) > 0

        self.code = code
        self.description = description

        self.sub_sections = []
        self.embedding = None

    def __repr__(self):
        return '.'.join(self.code)


class SubSection:

    def __init__(self, code, description):
        assert len(code) == 3
        assert all(len(part) == 2 for part in code)
        assert type(description) == str
        assert len(description) > 0

        self.code = code
        self.description = description

        self.items = []
        self.embedding = None

    def __repr__(self):
        return '.'.join(self.code)


class Item:

    def __init__(self, code, suffix, description):
        assert len(code) == 3
        assert all(len(part) == 2 for part in code)
        assert len(suffix) == 3
        assert type(description) == str
        assert len(description) > 0

        self.code = code
        self.suffix = suffix
        self.description = description

        self.embedding = None

    def __repr__(self):
        return '.'.join(self.code) + ' ' + self.suffix
