.PHONY: run setup_database create_superuser load_data test shutdown

run: ## Starts the server
	$(eval include .env)
	$(eval export $(sh sed 's/=.*//' .env))

	docker compose up -d

shutdown: ## Shutdown the server
	$(eval include .env)
	$(eval export $(sh sed 's/=.*//' .env))

	docker compose down

setup_database:
	$(eval include .env)
	$(eval export $(sh sed 's/=.*//' .env))
	docker compose exec db psql -U $(DB_USER) -c "CREATE DATABASE $(DB_NAME) WITH OWNER $(DB_USER) ENCODING 'utf8'"

create_superuser: ## Create a superuser for the app
	docker exec -it pure_app-app-1 python manage.py createsuperuser

load_data: ## Load chats data
	@if [ -z "$(n)" ]; then echo "Please specify the amount of data to load (e.g., make load_data n=1000)"; exit 1; fi
	docker exec -it pure_app-app-1 python manage.py generate_chats $(n)

test: ## Run the test suite
	docker exec -it pure_app-app-1 pytest
