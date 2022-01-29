dev:
	FLASK_APP=sixchan FLASK_ENV=development flask run

up:
	docker compose up -d

down:
	docker compose down

lint:
	flake8 --exclude .venv --max-line-length 88

format:
	black .

.PHONY: dev up down lint format