from cerberus.static.external_modules.neo4jvis.utils.validation import validate_positive_integer
import cerberus.static.external_modules.neo4jvis.utils.draw_utils as draw_utils
import cerberus.static.external_modules.neo4jvis.utils.query_utils as query_utils
import cerberus.static.external_modules.neo4jvis.utils.neomodel_utils as neomodel_utils


class StyledGraph():
    def __init__(self, driver, directed=False):
        self._driver = driver
        self._nodes = dict()
        self._edges = set()
        self._value = None
        self._directed = directed
        self._attr = dict()
        self._options = self.default_options()

    def __getitem__(self, key):
        return self._attr[key]

    def __setitem__(self, key, value):
        self._attr[key] = value

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    @property
    def value(self):
        return self._value

    @property
    def driver(self):
        return self._driver

    @property
    def directed(self):
        return self._directed

    @property
    def options(self):
        return self._options

    @nodes.setter
    def nodes(self, value):
        self._nodes = value

    @driver.setter
    def driver(self, value):
        self._driver = value

    @edges.setter
    def edges(self, value):
        self._edges = value

    @value.setter
    def value(self, value):
        validate_positive_integer(value)
        self._value = value

    @directed.setter
    def directed(self, value):
        self._directed = value

    @options.setter
    def options(self, value):
        self._options = value

    def default_options(self):
        return {
            "nodes": {
                "color": {
                    "border": "#FFFFFF",
                    "background": "#F9A6C1"
                },
                "borderWidth": 2,
                "borderWidthSelected": 2,
                "shape": "dot"
            },
            "edges": {
                "arrows": {
                    "to": {
                        "enabled": "true" if self._directed else "false",
                        "scaleFactor": 0.5
                    }
                },
                "color": {
                    "inherit": "false"
                },
                "font": {
                    "size": 14,
                    "align": "middle"
                },
                "smooth": {
                    "enabled": "true",
                    "type": "dynamic"
                },
                "length": 200
            },
            "interaction": {
                "dragNodes": "true",
                "hideEdgesOnDrag": "false",
                "hideNodesOnDrag": "false"
            },
            "physics": {
                "enabled": "true",
                "stabilization": {
                    "enabled": "true",
                    "fit": "true",
                }
            }
        }

    def add_node(self, node):
        self._nodes[node.id] = node

    def html(self, output=None):
        return draw_utils.draw(self, output)

    def draw(self, output="vis.html"):
        return draw_utils.draw_iframe(self, output)

    def generate_whole_graph(self):
        query_utils.generate_whole_graph(self)

    def add_from_query(self, query):
        query_utils.add_from_relationship(self._driver, self, query)

    def add_from_neomodel_relationship(self, structured_rel):
        neomodel_utils.add_structured_relation(self, structured_rel)

    def add_from_neomodel_relationships(self, structured_rel_list):
        neomodel_utils.add_structured_relations(self, structured_rel_list)

    def _repr_html_(self):
        return """
        <table>
            <tr>
                <td><strong>Nodes</strong></td>
                <td>{nodes}</td>
            </tr><tr>
                <td><strong>Edges</strong></td>
                <td>{edges}</td>
            </tr><tr>
                <td><strong>Value</strong></td>
                <td>{value}</td>
            </tr>
        </table>
        """.format(
            nodes=len(self._nodes),
            edges=len(self._edges),
            value=self._value,
        )
