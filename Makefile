setup:
	@pip install -Ue.\[tests\]

test:
	@coverage run --branch `which nosetests` -v --with-yanc -s tests/
