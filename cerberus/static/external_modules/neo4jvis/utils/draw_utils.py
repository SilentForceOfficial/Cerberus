from IPython.display import IFrame

from jinja2 import Template

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from cerberus.static.external_modules.neo4jvis import template


def draw(styled_graph, output=None):
    nodes = [n.to_dict() for n in styled_graph.nodes.values()]
    edges = [e.to_dict() for e in styled_graph.edges]
    options = str(styled_graph.options) \
        .replace("\'true\'", "true") \
        .replace("\'false'", "false")

    html_template = pkg_resources.read_text(template, "template.html")
    style_css = pkg_resources.read_text(template, "style.css")
    jinja_template = Template(html_template)
    html = jinja_template.render(
        style=style_css,
        options=options,
        nodes=nodes,
        edges=edges
    )

    if output is not None:
        file = open(output, "w")
        file.write(html)
        file.close()

    return html

def draw_iframe(styled_graph, output="vis.html"):
    draw(styled_graph, output=output)
    return IFrame(output, width="100%", height="500")
