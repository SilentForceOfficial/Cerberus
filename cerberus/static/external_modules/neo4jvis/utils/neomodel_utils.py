from neomodel import StructuredRel, StructuredNode
from neomodel.relationship_manager import RelationshipManager

from cerberus.static.external_modules.neo4jvis.model.styled_node import StyledNode
from cerberus.static.external_modules.neo4jvis.model.styled_edge import StyledEdge


def structured_node_to_styled(node):
    if not isinstance(node, StructuredNode):
        raise TypeError(f"Parameter should be of type : 'StructuredNode'."
                        f"Found type is : '{type(node)}'")
    styled_node = StyledNode(node.id)
    # name of the class is assigned as node label
    styled_node.label = [type(node).__name__]
    for k, v in node.__dict__.items():
        # we don't include relations as node attributes
        if not isinstance(v, RelationshipManager):
            styled_node[k] = str(v)
    return styled_node


def add_structured_relation(styled_graph, relation):
    if not isinstance(relation, StructuredRel):
        raise TypeError(f"Parameter should be of type : 'StructuredRel'."
                        f"Found type is : '{type(relation)}'")
    # get nodes of the realtionship
    start_node_id = relation._start_node_id
    end_node_id = relation._end_node_id
    start_node = styled_graph.nodes[start_node_id] \
                if start_node_id in styled_graph.nodes \
                else structured_node_to_styled(relation.start_node())
    end_node = styled_graph.nodes[end_node_id] \
        if end_node_id in styled_graph.nodes \
        else structured_node_to_styled(relation.end_node())
    styled_graph.nodes[start_node_id] = start_node
    styled_graph.nodes[end_node_id] = end_node

    # get relationship attributes
    edge = StyledEdge(relation.id, start_node, end_node)
    for k, v in relation.__dict__.items():
        if k != '_start_node_id' and k != '_end_node_id':
            edge[k] = v
    start_node.edges.add(edge)
    end_node.edges.add(edge)
    styled_graph.edges.add(edge)


def add_structured_relations(styled_graph, relations):
    if not isinstance(relations, list):
        raise TypeError(f"Parameter should be of type : 'list'."
                        f"Found type is : '{type(relations)}'")
    for relation in relations:
        add_structured_relation(styled_graph, relation)



