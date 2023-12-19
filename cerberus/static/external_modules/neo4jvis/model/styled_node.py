class StyledNode():
    def __init__(self, param_id, label=None):
        self._id = param_id
        self._label = label
        self._edges = set()
        self._attr = dict()

    def __getitem__(self, key):
        return self._attr[key]

    def __setitem__(self, key, value):
        self._attr[key] = value

    @property
    def id(self):
        return self._id

    @property
    def label(self):
        return self._label

    @property
    def edges(self):
        return self._edges

    @id.setter
    def id(self, value):
        self._id = value

    @label.setter
    def label(self, value):
        self._label = value

    @edges.setter
    def edges(self, value):
        self._edges = value

    def _repr_html_(self):
        return """
        <table>
            <tr>
                <td><strong>Id</strong></td>
                <td>{id}</td>
            </tr><tr>
                <td><strong>Label</strong></td>
                <td>{label}</td>
            </tr><tr>
                <td><strong>Edges</strong></td>
                <td>{edges}</td>
            </tr>
        </table>
        """.format(
            id=self._id,
            label=self._label,
            edges=len(self._edges),
        )

    def to_dict(self):
        res = {
            'id': self._id,
            'label': str(self._label),
        }
        if "id" in self._attr:
            # Having properties with key "id" will conflict
            # with the drawing process, conseq. it is replaced with "ID"
            self._attr["ID"] = self._attr.pop("id")
        res = {**res, **self._attr}  # we join both dictionaries
        return res
