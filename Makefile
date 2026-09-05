.PHONY: help up down logs health test test-telemetry deploy-prod clean

help:
	@echo "AISensorEdgeComp Platform — common commands"
	@echo ""
	@echo "  make up              Start full stack via docker compose"
	@echo "  make down            Stop the stack"
	@echo "  make logs            Tail all logs"
	@echo "  make health          Check service health"
	@echo "  make test-telemetry  Send a test telemetry message"
	@echo "  make test            Run pytest suite"
	@echo "  make deploy-prod     Deploy to k8s (NAMESPACE=production)"
	@echo "  make clean           Remove all containers, volumes, and caches"

up:
	docker compose up -d
	@echo "Stack starting. Run 'make health' to verify."

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

health:
	@echo "Checking service health..."
	@curl -sf http://localhost:8000/health > /dev/null && echo "  ✓ API: ok" || echo "  ✗ API: down"
	@curl -sf http://localhost:8081/subjects > /dev/null && echo "  ✓ Schema Registry: ok" || echo "  ✗ Schema Registry: down"
	@docker compose ps --format "table {{.Name}}\t{{.Status}}" | grep -v NAME

test-telemetry:
	@echo "Sending test telemetry message..."
	python scripts/send_test_telemetry.py

test:
	pytest tests/ -v --cov=services --cov-report=term-missing

deploy-prod:
	@test -n "$(NAMESPACE)" || (echo "Usage: make deploy-prod NAMESPACE=production" && exit 1)
	helm upgrade --install aisensoredgecomp ./helm/aisensoredgecomp \
	  --values ./helm/values-production.yaml \
	  --namespace $(NAMESPACE) \
	  --create-namespace \
	  --wait

clean:
	docker compose down -v --rmi local
	rm -rf .pytest_cache .coverage htmlcov
