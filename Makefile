dev:
	FLASK_APP=sixchan FLASK_ENV=development flask run

lint:
	flake8 --exclude .venv --max-line-length 88

format:
	black .

.PHONY: dev lint format