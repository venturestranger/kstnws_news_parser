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

	conn = sqlite3.connect(Config.DB_FILE)
	cur = conn.cursor()

	payload = {
		'id_author': Config.POOL_SERVER_USER_ID,
		'title': data['title'],
		'lead': '',
		'picture_url': data['pic_url'],
		'content': data['content'],
		'date_publication': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
		'date_edit': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
		'category': data['category'],
		'hashtags': data['hashtags'],
		'comment': ''
	}
	print('Pushing:', link)
	print(payload)
	
	while True:
		headers = {
			'Authorization': 'Bearer ' + Config.POOL_SERVER_TOKEN
		}
		response = requests.post(Config.POOL_SERVER, json=payload, headers=headers)

		if response.status_code == 200:
			response = requests.get(Config.POOL_SERVER + f'?id_author={Config.POOL_SERVER_USER_ID}', headers=headers)
			post_id = sorted(response.json(), key=lambda x: int(x['id']), reverse=True)[0]['id']
			requests.put(Config.POOL_SERVER + f'/push?id={post_id}&pass=true', headers=headers)
			break
		else:
			print("Fetching Authorization token")
			response = requests.get(Config.POOL_SERVER + '/auth?key=domain')
			Config.POOL_SERVER_TOKEN = response.text

	cur.execute(f'INSERT INTO headings(id) VALUES({hashed})')
	conn.commit()
	conn.close()

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

		sleep(timeout)


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

# links = get_articles(file_path='links_headings.data')
# push_content(fetch_content(links[0], gpt_processed=True))
# save_links(links=get_articles(*save_links_headings(links, headings, 'links_headings.data')), file_path='links.data')
