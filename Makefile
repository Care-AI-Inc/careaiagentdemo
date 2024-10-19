format:
	autoflake --remove-all-unused-imports --in-place --recursive .
	isort .
	black .

lint:
	flake8 .