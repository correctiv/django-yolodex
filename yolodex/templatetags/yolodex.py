from django import template

register = template.Library()


def verbify(edge, subject):
    return edge.render_with_subject(subject)

register.simple_tag(verbify)
