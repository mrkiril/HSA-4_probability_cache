MAIN_SERVICE = king_size_service

ps:
	docker-compose ps

up:
	docker-compose up -d
	docker-compose ps

down:
	docker-compose down

run:
	docker-compose build --parallel --no-cache
	docker-compose up -d
	docker-compose ps

rebuild:
	docker-compose build --parallel
	docker-compose up -d
	docker-compose ps

restart:
	docker-compose restart $(MAIN_SERVICE)
	docker-compose ps

bash:
	docker-compose exec $(MAIN_SERVICE) bash

statm:
	docker-compose exec $(MAIN_SERVICE) bash -c "printf '%(%m-%d %H:%M:%S)T    ' && cat /proc/1/statm"

pidstat:
	docker-compose exec $(MAIN_SERVICE) bash -c "pidstat -p 1 -r 10 100"

psql:
	docker-compose exec db_postgres psql -U postgres -d projector_hw4

format:
	isort .
	python3 -m black -l 100 .
	python3 -m flake8 -v


siege:
	#siege -q -b -r 100000 --concurrent=50 --file=urls.txt
	siege -v --concurrent=50 --delay=0.55 --file=urls.txt
