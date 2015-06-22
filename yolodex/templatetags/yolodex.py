from django import template

register = template.Library()


@register.simple_tag
def verbify(edge, subject):
    return edge.render_with_subject(subject, link_object=True)


@register.assignment_tag
def dictKeyLookup(the_dict, key):
    return the_dict.get(key, '')
