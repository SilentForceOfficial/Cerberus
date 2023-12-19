class StyledEdge():
    def __init__(self, param_id, source, target, param_type=None):
        self._id = param_id
        self.source = source
        self.target = target
        self._type = param_type
        self._attr = dict()

    def __getitem__(self, key):
        return self._attr[key]

    def __setitem__(self, key, value):
        self._attr[key] = value

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def source(self):
        return self.source

    @property
    def target(self):
        return self.target

    @type.setter
    def type(self, value):
        self._type = value

    @source.setter
    def source(self, value):
        self._source = value

    @target.setter
    def target(self, value):
        self._target = value

    def _repr_html_(self):
        return """
        <table>
            <tr>
                <td><strong>Source</strong></td>
                <td>{source}</td>
            </tr><tr>
                <td><strong>Target</strong></td>
                <td>{target}</td>
            </tr><tr>
                <td><strong>Id</strong></td>
                <td>{id}</td>
            </tr>
        </table>
        """.format(
            source=self._source.id,
            target=self._target.id,
            id=self._id,
        )

    def to_dict(self):
        res = {
            'from': self._source.id,
            'to': self._target.id,
            'id': self._id,
            'type': str(self._type)
        }
        if "id" in self._attr:
            # Having properties with key "id" will conflict
            # with the drawing process, conseq. it is replaced with "ID"
            self._attr["ID"] = self._attr.pop("id")
        res = {**res, **self._attr}  # we join both dictionaries
        return res
