protocols = {
	'tengrinews.kz': lambda heading, heading_extract, link_extract: len(heading) > 20 and len(heading_extract) >= 6,
	'zakon.kz': lambda heading, heading_extract, link_extract: len(heading) > 20 and len(heading_extract) >= 7,
	'nur.kz': lambda heading, heading_extract, link_extract: len(heading) > 20 and len(heading_extract) >= 7,
	'vlast.kz': lambda heading, heading_extract, link_extract: len(heading) > 20 and len(heading_extract) >= 5,
	'caravan.kz': lambda heading, heading_extract, link_extract: len(heading) > 20 and len(heading_extract) >= 6,
	'ktk.kz': lambda heading, heading_extract, link_extract: len(link_extract) >= 6,
	'khabar.kz': lambda heading, heading_extract, link_extract: len(heading) > 20 and len(heading_extract) >= 6,
	'lada.kz': lambda heading, heading_extract, link_extract: len(heading) > 20 and len(heading_extract) >= 6,
	'uralskweek.kz': lambda heading, heading_extract, link_extract: len(heading) > 20,
	'sinegor.kz': lambda heading, heading_extract, link_extract: len(heading) > 20,
}

class Validator:
	def __init__(self):
		pass
	
	def check(self, link, heading):
		dec_heading = heading.split('-')
		heading_extract = max(filter(lambda x: x.isdigit(), dec_heading + ['0']), key=lambda x: len(x))

		link += '/0'
		link_extract = max(filter(lambda x: x.isdigit(), link.replace('-', '/').split('/')), key=lambda x: len(x))

		domain = link.split('//')[1].split('/')[0]
		if domain.startswith('www.'):
			domain = domain[4:]

		if protocols[domain](heading, heading_extract, link_extract):
			return True
		else:
			return False
