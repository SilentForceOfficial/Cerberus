from cerberus.static.external_modules.neo4jvis.utils.validation import validate_hex_color


class Color:
    def __init__(self, background=None, border=None):
        self._background = background
        self.border = border

    @property
    def background(self):
        return self._background

    @property
    def border(self):
        return self._border

    @background.setter
    def background(self, value):
        if value is not None:
            validate_hex_color(value)
        self._background = value

    @border.setter
    def border(self, value):
        if value is not None:
            validate_hex_color(value)
        self._border = value

    def to_dict(self):
        res = {}
        if self._background is not None:
            res["background"] = self._background
        if self._border is not None:
            res["border"] = self._border
        return res