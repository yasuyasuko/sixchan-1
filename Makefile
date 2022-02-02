dev:
	FLASK_APP=sixchan FLASK_ENV=development flask run

up:
	docker compose up -d

down:
	docker compose down

createtables:
	python3 -c "from sixchan import app, db; db.create_all(app=app)"

droptables:
	python3 -c "from sixchan import app, db; db.drop_all(app=app)"

insertmocks:
	python3 -c "from sixchan import app; from sixchan.models import insert_mockdata; app.app_context().push(); insert_mockdata();"

resetdb: droptables createtables insertmocks

lint:
	flake8 --exclude .venv --max-line-length 88

format:
	black .

.PHONY: dev up down createtables droptables insertmocks resetdb lint format