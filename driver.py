import requests
import sqlite3
import hashlib
import random
from time import sleep
from bs4 import BeautifulSoup as Bs 
from config import Config
from datetime import datetime
from validation import Validator
from language_models import process

def md5hash(data):
	hash_object = hashlib.md5(data.encode())
	digest = hash_object.hexdigest()
	return digest

def search_image(keywords):
	try:
		response = requests.get(f'https://unsplash.com/s/photos/{keywords}?license=free')
		soup = Bs(response.text, 'html.parser')
		figs = soup.find_all('figure', attrs={'itemprop': 'image'})

		figs = figs[random.randint(0, max(len(figs) // Config.UNSPLASH_SEARCH_LIMITER, 1))].find_all('img')
		idx = len(figs) - 1
		ret = ''
		
		while idx != -1:
			try:
				srcs = figs[-1]['srcset']
				links = srcs.split()
				return links[links.index(f'{Config.IMAGE_SCALE}w,') - 1]
			except:
				idx -= 1
		return Config.DUMMY_IMAGE
	except:
		return Config.DUMMY_IMAGE

def get_articles(links=None, headings=None, file_path=None):
	if file_path != None:
		links, headings = [], []
		with open(file_path) as file:
			for line in file:
				link, heading = line.strip().split('$#@')
				links.append(link)
				headings.append(heading)
	
	ret = []
	prev = ''

	validator = Validator()
	for link, heading in zip(links, headings):
		if validator.check(link, heading):
			if heading != prev:
				ret.append(link)
				prev = heading
	
	return ret

def fetch_links(domain, entry_point=None):
	if entry_point == None:
		entry_point = domain

	response = requests.get(entry_point)
	soup = Bs(response.text, 'html.parser')

	data = soup.find_all('a', attrs={'href': True})

	links, headings = [], []
	for item in data:
		try:
			heading = max(item['href'].split('/'), key=lambda item: len(item)).split('#')[0].split('.')[0]
			if item['href'].startswith('/') and not item['href'].startswith('//'):
				links.append(domain + item['href'])
				headings.append(heading)
			elif item['href'].startswith(domain):
				links.append(item['href'])
				headings.append(heading)
		except:
			pass
	
	return links, headings

def save_links_headings(links, headings, file_path):
	if file_path != None:
		with open(file_path, 'w') as file:
			for link, heading in zip(links, headings):
				file.write(f'{link}$#@{heading}\n')
	
	return links, headings

def save_links(links, file_path):
	if file_path != None:
		with open(file_path, 'w') as file:
			for link in links:
				file.write(f'{link}\n')

def fetch_content(link, ai_processed=True, timeout=300):
	domain = link.split('://')[1].split('/')[0]
	print(f'Fetching from {domain}: ', link)
	hashed = md5hash(link)

	conn = sqlite3.connect(Config.DB_FILE)
	cur = conn.cursor()

	cur.execute(f"SELECT * FROM headings WHERE hashed = '{hashed}'")
	rows = cur.fetchall()
	conn.close()
	
	if len(rows) == 0:
		print('Checked not uploaded')

		response = requests.get(link)
		soup = Bs(response.text, 'html.parser')

		content = soup.text.replace('\n', '. ').replace('  ', '.')
		content = filter(lambda item: len(item) > 110, content.split('.'))
		content = '. '.join(list(content))[:1000]

		if ai_processed == True:
			data = process(content, domain)
			return data
		else:
			# do not disable ai_processed
			return content
	else:
		print('Already uploaded')
		return -1
