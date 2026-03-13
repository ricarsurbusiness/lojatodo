.PHONY: help up down build build-all test test-auth test-product test-cart test-order test-inventory test-payment test-notification test-analytics test-admin lint lint-auth lint-product lint-cart lint-order lint-inventory lint-payment lint-notification lint-analytics lint-admin migrate migrate-auth migrate-product clean logs

help:
	@echo "LojaTodo - Available commands:"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make build           - Build all service images"
	@echo "  make build-auth      - Build auth-service image"
	@echo "  make build-product   - Build product-service image"
	@echo "  make build-cart      - Build cart-service image"
	@echo "  make build-order     - Build order-service image"
	@echo "  make build-inventory - Build inventory-service image"
	@echo "  make build-payment   - Build payment-service image"
	@echo "  make build-notification - Build notification-service image"
	@echo "  make build-analytics - Build analytics-service image"
	@echo "  make build-admin     - Build admin-service image"
	@echo "  make test            - Run all tests"
	@echo "  make test-auth       - Run auth-service tests"
	@echo "  make test-product   - Run product-service tests"
	@echo "  make test-cart       - Run cart-service tests"
	@echo "  make test-order      - Run order-service tests"
	@echo "  make test-inventory  - Run inventory-service tests"
	@echo "  make test-payment    - Run payment-service tests"
	@echo "  make test-notification - Run notification-service tests"
	@echo "  make test-analytics  - Run analytics-service tests"
	@echo "  make test-admin      - Run admin-service tests"
	@echo "  make lint            - Run all linters"
	@echo "  make lint-auth       - Run auth-service linter"
	@echo "  make lint-product   - Run product-service linter"
	@echo "  make lint-cart       - Run cart-service linter"
	@echo "  make lint-order      - Run order-service linter"
	@echo "  make lint-inventory  - Run inventory-service linter"
	@echo "  make lint-payment    - Run payment-service linter"
	@echo "  make lint-notification - Run notification-service linter"
	@echo "  make lint-analytics  - Run analytics-service linter"
	@echo "  make lint-admin      - Run admin-service linter"
	@echo "  make migrate         - Run all migrations"
	@echo "  make migrate-auth    - Run auth-service migrations"
	@echo "  make migrate-product - Run product-service migrations"
	@echo "  make clean           - Remove containers and volumes"
	@echo "  make logs            - View logs"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

build-auth:
	docker-compose build auth-service

build-product:
	docker-compose build product-service

build-cart:
	docker-compose build cart-service

build-order:
	docker-compose build order-service

build-inventory:
	docker-compose build inventory-service

build-payment:
	docker-compose build payment-service

build-notification:
	docker-compose build notification-service

build-analytics:
	docker-compose build analytics-service

build-admin:
	docker-compose build admin-service

test:
	@echo "Running all tests..."
	cd services/auth-service && pytest || true
	cd services/product-service && pytest || true
	cd services/cart-service && pytest || true
	cd services/order-service && pytest || true
	cd services/inventory-service && pytest || true
	cd services/payment-service && pytest || true
	cd services/notification-service && pytest || true
	cd services/analytics-service && pytest || true
	cd services/admin-service && pytest || true

test-auth:
	cd services/auth-service && pytest -v

test-product:
	cd services/product-service && pytest -v

test-cart:
	cd services/cart-service && pytest -v

test-order:
	cd services/order-service && pytest -v

test-inventory:
	cd services/inventory-service && pytest -v

test-payment:
	cd services/payment-service && pytest -v

test-notification:
	cd services/notification-service && pytest -v

test-analytics:
	cd services/analytics-service && pytest -v

test-admin:
	cd services/admin-service && pytest -v

lint:
	@echo "Running all linters..."
	cd services/auth-service && ruff check app/ || true
	cd services/product-service && ruff check app/ || true
	cd services/cart-service && ruff check app/ || true
	cd services/order-service && ruff check app/ || true
	cd services/inventory-service && ruff check app/ || true
	cd services/payment-service && ruff check app/ || true
	cd services/notification-service && ruff check app/ || true
	cd services/analytics-service && ruff check app/ || true
	cd services/admin-service && ruff check app/ || true

lint-auth:
	cd services/auth-service && ruff check app/

lint-product:
	cd services/product-service && ruff check app/

lint-cart:
	cd services/cart-service && ruff check app/

lint-order:
	cd services/order-service && ruff check app/

lint-inventory:
	cd services/inventory-service && ruff check app/

lint-payment:
	cd services/payment-service && ruff check app/

lint-notification:
	cd services/notification-service && ruff check app/

lint-analytics:
	cd services/analytics-service && ruff check app/

lint-admin:
	cd services/admin-service && ruff check app/

migrate:
	@echo "Running all migrations..."
	cd services/auth-service && python -m alembic upgrade head || true
	cd services/product-service && python -m alembic upgrade head || true

migrate-auth:
	cd services/auth-service && python -m alembic upgrade head

migrate-product:
	cd services/product-service && python -m alembic upgrade head

clean:
	docker-compose down -v

logs:
	docker-compose logs -f
