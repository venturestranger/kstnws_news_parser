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

	cur.execute('CREATE TABLE IF NOT EXISTS headings (id INTEGER PRIMARY KEY AUTOINCREMENT, hashed TEXT)')
	conn.commit()

def push_content(data, link):
	try:
		hashed = md5hash(link)

		payload = {
			'id_author': Config.POOL_SERVER_USER_ID,
			'title': data['title'],
			'lead': '',
			'picture_url': search_image((' '.join(data['keywords'])).replace(' ', '-')),
			'content': data['content'],
			'date_publication': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
			'date_edit': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
			'category': '',
			'hashtags': ' '.join(data['keywords']),
			'comment': ''
		}

		conn = sqlite3.connect(Config.DB_FILE)
		cur = conn.cursor()

		print('Pushing:', link)
		print(payload)
		
		cur.execute(f"INSERT INTO headings(hashed) VALUES('{hashed}')")
		conn.commit()
		conn.close()

		try:
			headers = {
				'Authorization': 'Bearer ' + Config.POOL_SERVER_TOKEN
			}
			requests.post(Config.POOL_SERVER, json=payload, headers=headers, timeout=3)
			response = requests.get(Config.POOL_SERVER + f'?id_author={Config.POOL_SERVER_USER_ID}', headers=headers, timeout=3)
			post_id = sorted(response.json(), key=lambda x: int(x['id']), reverse=True)[0]['id']
			requests.put(Config.POOL_SERVER + f'/push?id={post_id}&pass=true', headers=headers, timeout=3)
		except:
			print('Error', e)
	except:
		print('Error', e)

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
				try:
					data = fetch_content(link, ai_processed=True)
					if data != -1:
						push_content(data, link)
						sleep(timeout)
				except Exception as e:
					print('Error', e)
		else:
			save_links(links, path)


if __name__=='__main__':
	if Config.INIT == True:
		init()

	while True:
		try:
			parse(push=True, timeout=300)
		except Exception as e:
			print('Error', e)
