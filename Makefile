install:
pip install -r requirements.txt

test:
pytest --maxfail=1 --disable-warnings -q

lint:
flake8 src tests

build:
docker build -t project-mvp .

clean:
rm -rf data/*.csv
