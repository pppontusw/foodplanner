test:
	python -m unittest discover tests/ -v

coverage:
	coverage run -m unittest discover tests/

format:
	black app

lint:
	flake8 app
