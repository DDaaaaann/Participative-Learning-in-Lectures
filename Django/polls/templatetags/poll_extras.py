from django import template

register = template.Library()

@register.filter
def voteFilter(value):
	"""
	Filters the values where openForVoting is False and immediately order
	the outcome randomly.
	"""
	answers = value.filter(openForVoting=True).order_by('?')
	return answers

@register.filter
def rankFilter(value):
        """
        Ranks the filtered results, at this point only the answers that are
        still open for voting are ranked.
        """
	answers = value.filter(openForVoting=True).order_by('-votes')
	return answers

