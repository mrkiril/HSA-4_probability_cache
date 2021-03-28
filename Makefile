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
	docker-compose exec $(MAIN_SERVICE) bash -c "pidstat -p 1 -r 60 100"

psql:
	docker-compose exec db-reface-auth-new psql -U postgres -d reface-auth

format:
	isort .
	python3 -m black -l 100 .
	python3 -m flake8 -v

pytest: up
	docker-compose exec $(MAIN_SERVICE) pytest
	make down

pytest_report: up
	docker-compose exec $(MAIN_SERVICE) python3 -m pytest --cov-report term-missing --cov=. tests/

drop-db:
	make down
	docker volume rm reface-authentication-service_db-data

migrate: up
	docker-compose exec $(MAIN_SERVICE) python3 -m reface_service_base -c migrate


