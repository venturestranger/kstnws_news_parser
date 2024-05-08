class Config:
	DOMAINS_FILE = 'domains.txt'
	OPENAI_TOKEN = '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'
	PROMPT_CONTENT = '''. Paraphrase in 80 words, change sentences, remove source and correspondent mentions'''
	PROMPT_CATEGORY = '''. Write only one corresponding topic: Регионы, Экономика, Политика, ЖКХ, Происшествия, Здравоохранение, Образование, Спорт, Общество, Погода'''
	PROMPT_TITLE = '''. Write only title in 10 words'''
	POST_REFERENCE = ', передает Kostanay News со ссылкой на '
	PARAPHRASE_TURNS = 2
	DB_FILE = './storage/headings.db'
	INIT = True
	LLM_BASE_URL = 'http://localhost:11434/api/generate'
	LLM_MODEL = 'mistral:7b-instruct'
	DUMMY_IMAGE = ''
	IMAGE_SCALE = 600
	UNSPLASH_SEARCH_LIMITER = 3
	POOL_SERVER = 'https://tvoykostanay.kz/validate'
	POOL_SERVER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOiIyMDI0LTA0LTE4VDEyOjM3OjE1Ljg1NDU2MTczNFoiLCJpYXQiOjE3MTM0NDAyMzUsImlzcyI6IjQ5NGMwNmY4NmYwODZmNWJiMTM1ZjI0MWJhZGEyZDViYTBjZDdhMGQ5OWRkY2Q5MDIzYjNlMWVlYTk5NWZhNTQifQ.ST7iU8PBlyoU1wqQXY5iMduklmU2cLJUtrZwTk8ntRY'
	POOL_SERVER_USER_ID = 47
