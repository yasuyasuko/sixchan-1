dev:
	FLASK_APP=sixchan FLASK_ENV=development flask run

up:
	docker compose up -d

down:
	docker compose down

postgres:
	docker compose exec postgres bash

createtables:
	FLASK_APP=sixchan FLASK_ENV=development flask database create_tables

droptables:
	FLASK_APP=sixchan FLASK_ENV=development flask database drop_tables

insertmocks:
	FLASK_APP=sixchan FLASK_ENV=development flask dev insert_mockdata

resetdb: droptables createtables insertmocks

lint:
	flake8 --exclude .venv --max-line-length 88

format:
	black .

isort:
	isort --force-single-line-imports .

.PHONY: dev up down postgres
.PHONY: createtables droptables insertmocks resetdb
.PHONY: lint format isort