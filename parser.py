from driver import fetch_links
from driver import fetch_content
from driver import get_articles
from driver import save_links_headings
from driver import save_links
from driver import search_image
from driver import md5hash
from config import Config
from datetime import datetime
from time import sleep
import sqlite3
import random
import requests

def init():
	conn = sqlite3.connect(Config.DB_FILE)
	cur = conn.cursor()

	cur.execute('CREATE TABLE IF NOT EXISTS headings (id INTEGER PRIMARY KEY)')
	conn.commit()

def push_content(data, link):
	hashed = abs(md5hash(link))

	"""
	conn = sqlite3.connect(Config.DB_FILE)
	cur = conn.cursor()

	print('Pushing:', link)
	print(payload)
	
	# pushing 

	cur.execute(f'INSERT INTO headings(id) VALUES({hashed})')
	conn.commit()
	conn.close()
	"""

def parse(cycles=1, timeout=10, push=False, path='./links.txt'):
	for i in range(cycles):
		links = []
		headings = []
		domains = []

		with open(Config.DOMAINS_FILE) as file:
			for line in file:
				line = line.strip()
				if len(line) != 0:
					domains.append(line)

		count, overall = 0, len(domains)

		for domain in domains:
			count += 1
			print('Parsing: ', count, overall)

			domain, entry = '/'.join(domain.split('/')[:3]), domain

			ls, hs = fetch_links(domain, entry)
			links.extend(ls)
			headings.extend(hs)

		save_links_headings(links, headings, 'links_headings.txt')
		links = get_articles(links, headings)

		if push == True:
			random.shuffle(links)
			for link in links:
				data = fetch_content(link, gpt_processed=True)
				if data != -1:
					push_content(data, link)
					sleep(timeout)
		else:
			save_links(links, path)


if __name__=='__main__':
	if Config.INIT == True:
		init()

	parse(push=False)
	"""
	while True:
		try:
			parse()
		except Exception as e:
			print('Error', e)
	"""
