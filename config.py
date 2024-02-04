class Config:
	DOMAINS_FILE = 'domains.txt'
	OPENAI_TOKEN = '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'
	PROMPT_META = '''Напиши название для статьи. Напиши к какой одной категории относится текст (Мировые новости, Республиканские новости, Регионы, Город, Село, Экономика, Политика, ЖКХ, Дороги, Экология, Происшествия, Правопорядок, Культура и искусство, Здравоохранение, Образование, Наука и технологии, Спорт, Животные, Общество, ЖЗЛ (Жизнь замечательных людей), Погода, Обзоры и аналитика, Развлечение). После напиши три ключевых слова из статьи переведенных на английский. Используй слова 'Название', 'Категория', 'Ключевые слова'\n'''
	PROMPT_CONTENT = '''Перефразируй текст и напиши в 80 словах\n'''
	POST_REFERENCE = ', передает Kostanay News со ссылкой на '
	DB_FILE = './storage/headings.db'
	POOL_SERVER = 'https://tvoykostanay.kz/validate'
	POOL_SERVER_USER_ID = 47
	POOL_SERVER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOiIyMDI0LTAxLTI0VDE0OjI1OjI0Ljc2NjA2NDQ2NloiLCJpYXQiOjE3MDYxMDI3MjQsImlzcyI6ImRvbWFpbiJ9.7IsgrGSoIU5dFWNsdTABdfZnMXAwt1G172T0_wWR6XA'
	INIT = False
	IMAGE_SCALE = 700
	DUMMY_IMAGE = ''
