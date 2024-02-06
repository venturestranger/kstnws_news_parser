import requests
import openai
import sqlite3
import hashlib
import random
from time import sleep
from bs4 import BeautifulSoup as Bs 
from config import Config
from datetime import datetime
from validation import Validator

def md5hash(data):
	hash_object = hashlib.md5(data.encode())
	digest = hash_object.hexdigest()
	return digest

def search_image(keywords):
	try:
		response = requests.get(f'https://unsplash.com/s/photos/{keywords}?license=free')
		soup = Bs(response.text, 'html.parser')
		figs = soup.find('figure', attrs={'itemprop': 'image'}).find_all('img')

		idx = len(figs) - 1
		ret = ''

		while idx != -1:
			try:
				srcs = figs[-1]['srcset']
				links = srcs.split()
				return links[links.index(f'{Config.IMAGE_SCALE}w,') - 1]
			except:
				idx -= 1
	except:
		return Config.DUMMY_IMAGE
	else:
		return Config.DUMMY_IMAGE

def process_response(response, domain):
	response = response.split('\n')
	data = {}
	data['title'] = ''
	data['pic_url'] = ''
	data['content'] = ''
	data['category'] = ''
	data['hashtags'] = ''

	for line in response:
		line = line.split(': ')
		words = line[0].lower().split()

		if len(words) > 2:
			words = []
			line = ': '.join(line[0:]).strip()
		else:
			line = ': '.join(line[1:]).strip()

		if 'контент' in words:
			data['content'] = line
		elif 'название' in words:
			if line.startswith('"') and line.endswith('"'):
				line = line[1:-1]
			data['title'] = line
		elif 'категория' in words:
			data['category'] = line.strip()
		elif 'ключевые' in words or 'слова' in words:
			data['hashtags'] = line.strip()
	
	splitted = data['content'].split('. ')
	data['content'] = '. '.join([splitted[0] + Config.POST_REFERENCE + domain] + splitted[1:])
	
	hashtags = data['hashtags'].split(', ')
	random.shuffle(hashtags)
	data['hashtags'] = [item.strip().replace(' ', '-').lower() for item in hashtags]

	data['pic_url'] = search_image('-'.join(data['hashtags']) + '-' + data['category'].lower())
	data['hashtags'] = ' '.join(data['hashtags'])
	return data

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

def fetch_content(link, gpt_processed=True, timeout=300):
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

		content = soup.text.replace('\n', '.').replace('  ', '.')
		content = filter(lambda item: len(item) > 50, content.split('.'))
		content = '\n'.join(list(content))

		if gpt_processed == True:
			openai.api_key = Config.OPENAI_TOKEN
			data = ''
			
			while True:
				try:
					response = openai.ChatCompletion.create(    
						model="gpt-3.5-turbo-16k",
						messages=[{"role": "user", "content": Config.PROMPT_META + content}],
						temperature=0.2,
						max_tokens=4000,
						top_p=1,
						frequency_penalty=0.24,
						presence_penalty=0.18,
					)
				except Exception as e:
					print('OpenAI rate limit at PROMPT_META. Hope next request works', e)
					sleep(timeout)
				else:
					data += str(response['choices'][0]['message']['content']) + '\n'
					break

			while True:
				try:
					response = openai.ChatCompletion.create(    
						model="gpt-3.5-turbo-16k",
						messages=[{"role": "user", "content": Config.PROMPT_CONTENT + content}],
						temperature=0.2,
						max_tokens=4000,
						top_p=1,
						frequency_penalty=0.24,
						presence_penalty=0.18,
					)
				except Exception as e:
					print('OpenAI rate limit at PROMPT_META. Hope next request works', e)
					sleep(timeout)
				else:
					data += 'Контент: ' + str(response['choices'][0]['message']['content'])
					break

			processed_response = process_response(data, domain)
			return processed_response
		else:
			# do not disable gpt_processed
			return content
	else:
		print('Already uploaded')
		return -1

