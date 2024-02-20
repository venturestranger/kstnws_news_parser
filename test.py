from language_models import TopicRecognizer
model = TopicRecognizer()

while True:
	text = input("TEXT: ")
	print(model.query(text, n_returns=3))
