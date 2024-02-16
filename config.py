class Config:
	DOMAINS_FILE = 'domains.txt'
	OPENAI_TOKEN = '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'
	PROMPT_CONTENT = '''paraphrase in 80 words, change sentence order, remove source mentions: '''
	PROMPT_TITLE = '''Write the title for this text: '''
	POST_REFERENCE = ', передает Kostanay News со ссылкой на '
	PARAPHRASE_TURNS = 2
	DB_FILE = './storage/headings.db'
	INIT = True
	LLM_BASE_URL = 'http://localhost:11434/api/generate'
	LLM_MODEL = 'mistral:7b-instruct'
	DUMMY_IMAGE = ''
	IMAGE_SCALE = 600
	UNSPLASH_SEARCH_LIMITER = 3
	POOL_SERVER_USER_ID = 47
