docker_flask = docker-compose exec auth flask


init_db:
	@echo "Database initialization is started"
	@${docker_flask} db init
	@${docker_flask} db migrate -m "Initial migration"
	@${docker_flask} db upgrade
	@echo "Database initialization is finished"

db_upgrade:
	@echo "Database initialization is started"
	@${docker_flask} db upgrade
	@echo "Database initialization is finished"

.PHONY = create_superuser check-env
create_superuser: check-env
	@echo "Start superuser creation"
	@${docker_flask} create_superuser '$(EMAIL)' '$(PASSWORD)'
	@echo "Superuser was created"

check-env:
ifndef EMAIL
	@echo "EMAIL is not defined"
	@exit 1
endif
ifndef PASSWORD
	@echo "PASSWORD is not defined"
	@exit 1
endif

run_tests:
	@echo "Running tests"
	@docker-compose -f docker-compose.test.yml --env-file .env.test up -d --build
	@echo "Tests finished"

run_app:
	@echo "Starting applications"
	@docker-compose up -d --build
	@echo "Applications are up"

run_sample_app:
	@echo "Starting applications"
	@docker-compose --env-file .env.sample up -d --build
	@echo "Applications are up"

down:
	@docker-compose down --remove-orphans
	@echo "Applications are down"

compile_proto:
	@echo "Compilation started"
	@docker-compose exec grpc python -m grpc_tools.protoc --proto_path=. ./auth_grpc.proto --python_out=. --grpc_python_out=.
	@echo "Compilation finished"