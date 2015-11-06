setup:
	@pip install -Ue.\[tests\]

test:
	@coverage run --branch `which nosetests` -v --with-yanc -s tests/

coverage:
	@coverage report -m --fail-under=30

focus:
	@coverage run --branch `which nosetests` -vv --with-yanc --logging-level=WARNING --with-focus -i -s tests/
