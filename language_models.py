from config import Config
from deep_translator import GoogleTranslator
from pymystem3 import Mystem
from nltk import sent_tokenize, word_tokenize, regexp_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.pipeline import Pipeline
import pickle
import numpy as np
import requests
import random
import re

class LLM:
	def __init__(self):
		pass

	def query(self, content, is_title=False, is_category=False):
		try:
			params = {
				'model': Config.LLM_MODEL,
				'prompt': content + (Config.PROMPT_TITLE if is_title else Config.PROMPT_CATEGORY if is_category else Config.PROMPT_CONTENT),
				'stream': False
			}
			resp = requests.post(Config.LLM_BASE_URL, json=params)

			content = resp.json()['response']
			return content
		except Exception as e:
			print('LLM: ', e)
			return -1

class Translator:
	def __init__(self):
		pass
	
	def query(self, text, source='en', target='ru'):
		translated = GoogleTranslator(source=source, target=target).translate(text)
		return translated

class Normalizer:
	def __init__(self, path='./models/', stopwords_loc='stopwords-ru.txt'):
		try:
			self.stopwords = []

			with open(path + stopwords_loc, 'r') as file:
				for line in file:
					self.stopwords.append(line.strip())
		except:
			self.stopwords = []
	
	def query(self, text, stopwords=None, normalize=True, min_length=4, as_str=False):
		if not stopwords:
			stopwords = self.stopwords

		if normalize:
			stem = Mystem()
			words = [lemma['analysis'][0]['lex'] for lemma in stem.analyze(text) if lemma.get('analysis', None) != None and len(lemma.get('analysis', [])) != 0 and not lemma['text'][0].isupper()]
		else:
			regexp=r'(?u)\b\w{4,}\b'
			words = [w for sent in sent_tokenize(text)
				for w in regexp_tokenize(sent, regexp)]

		if stopwords:
			stopwords = set(stopwords)
			words = [tok for tok in words if tok not in stopwords]

		words = [word for word in words if len(word) >= min_length]
		if as_str:
			words = ' '.join(words)

		return words

class TopicRecognizer:
	def __init__(self, path='./models/', docs='', stopwords_loc='stopwords-ru.txt'):
		try:
			with open(path + 'tfidf.pkl', 'rb') as file:
				vectorizer = pickle.load(file)
			with open(path + 'lda.pkl', 'rb') as file:
				lda = pickle.load(file)
			self.normalizer = Normalizer(stopwords_loc=stopwords_loc, path=path)
			self.kernel = Pipeline([
				('vectorizer', vectorizer),
				('latent_dirichlet_allocation', lda),
			])
		except Exception as e:
			print('TopicRecognizer: not initialized ', e)
	
	def fit(self, text, n_topics=100, path='./models/', stopwords_loc='stopwords-ru.txt', tokens=None):
		self.normalizer = Normalizer(stopwords_loc=stopwords_loc, path=path)

		if tokens == None:
			for idx in range(len(text)):
				text[idx] = ' '.join(normalizer.query(text[idx]))
				print(f'Fit on: {idx} / {len(text)}')
		else:
			with open(path + tokens) as file:
				text = pickle.load(file)

		vectorizer = TfidfVectorizer(max_features=10000)
		tfidf_matrix = vectorizer.fit_transform(text)
		
		lda = LatentDirichletAllocation(n_components=n_topics, max_iter=5, random_state=0)
		lda.fit(tfidf_matrix)

		with open(path + 'tfidf.pkl', 'wb') as file:
			pickle.dump(vectorizer, file)
		with open(path + 'lda.pkl', 'wb') as file:
			pickle.dump(lda, file)

		self.__init__(path=path, stopwords_loc=stopwords_loc)

	def query(self, text, n_returns=1):
		try:
			data = self.kernel.transform([self.normalizer.query(text, as_str=True)])
			return self.kernel['vectorizer'].get_feature_names_out()[self.kernel['latent_dirichlet_allocation'].components_[np.argmax(data[0])].argsort()[-n_returns:]]
		except:
			print('TopicRecognizer: ', e)
			return -1

def process(text, domain):
	print('Started processing text')
	llm = LLM()
	topic = TopicRecognizer()
	trans = Translator()

	print('[o]> ', text)
	for i in range(Config.PARAPHRASE_TURNS):
		text = llm.query(text)
		text = text.replace('\n', '. ')
		print('[~]> ', text)
	
	data = {}
	data['title'] = trans.query(llm.query(text, is_title=True))

	data['title'] = data['title'].split('\n')[0]
	if data['title'].startswith('Название:'):
		data['title'] = data['title'][:9].strip()
	if data['title'][-1].isalpha() == False and data['title'][0].isalpha() == False:
		data['title'] = data['title'][1:-1]

	data['content'] = trans.query(text)
	splitted = data['content'].split('. ')
	data['content'] = '. '.join([splitted[0] + Config.POST_REFERENCE + domain] + splitted[1:])

	data['keywords'] = [trans.query(item, source='ru', target='en') for item in list(topic.query(text, n_returns=3))]
	random.shuffle(data['keywords'])

	"""
	data['category'] = llm.query(text, is_category=True)
	print(data['category'])
	if data['category'].startswith('Topic'):
		data['category'] = ''.join([a for a in data['category'].split()[0] if a.isalpha()])
	else:
		data['category'] = ''.join([a for a in data['category'].split()[1] if a.isalpha()])
	"""

	print('[v]> ', data['content'], data['keywords'])
	return data
		

if __name__=='__main__':
	"""
	model = TopicRecognizer()
	text = ''
	with open('./models/news_sample.txt', 'r') as file:
		text = file.read()
	#model.fit(text.split('@#$')[:100])
	print(text.split('@#$')[-4])
	print(model.query(text.split('@#$')[-4], n_returns=3))
	"""
	text = """У казахстанцев скоро появится возможность легально трудоустроиться в Южной Корее. Как это можно будет сделать, рассказала министр труда и социальной защиты населения Светлана Жакупова, передает корреспондент Tengrinews.kz.11 По словам Светланы Жакуповой, в Минтруда был разработан проект, который согласовали с госорганами и направили через Министерство иностранных дел корейской стороне для согласования. "Какие подготовительные работы были проведены? Министерством совместно с акиматами Алматы, Алматинской области подготовлены производственная база в городе Кунаеве и Центр сертификации на базе университета имени Аль-Фараби. Эти работы проведены для того, чтобы выезжающие казахстанцы могли получить основы корейского языка, основы по тем профессиям, по которым будут даны разрешения [на работу], чтобы они приобретали квалификацию, чтобы мы их готовили", - сказала министр. """[:1500]

	print(process(text, 'x'))
	"""

	topic = TopicRecognizer()
	while True:
		inp = input()
		print(topic.query(inp, n_returns=3))
	"""
