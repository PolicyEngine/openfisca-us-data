format:
	autopep8 . -r -i
	black . -l 79
test:
	pytest tests/test_imports.py -vv
install:
	pip install -e .[dev]
