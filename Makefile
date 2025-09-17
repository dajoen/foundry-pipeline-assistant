# Foundry Pipeline Assistant - Development Makefile

.PHONY: help install run test lint format clean dev-setup check-config azurelogin

# Default target
help:
	@echo "📋 Foundry Pipeline Assistant - Available Commands"
	@echo "=================================================="
	@echo "🚀 Setup & Run:"
	@echo "  make install     Install package with dev dependencies"
	@echo "  make azurelogin  Setup Azure AI Foundry authentication"
	@echo "  make run         Run pipeline analysis with example question"
	@echo "  make run-custom  Run with custom question (interactive prompt)"
	@echo "  make dev-setup   Complete development environment setup"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test        Run test suite"
	@echo "  make lint        Check code quality with ruff"
	@echo "  make format      Format code with ruff"
	@echo "  make check-config Validate Azure AI configuration"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean       Remove cache files and artifacts"
	@echo ""
	@echo "💡 First time setup:"
	@echo "  1. make install"
	@echo "  2. make azurelogin  # Automatically configure Azure AI credentials"
	@echo "  3. make check-config  # Verify configuration"
	@echo "  4. make run"

install:
	@echo "📦 Installing foundry-pipeline-assistant..."
	poetry install --with dev
	@echo "✅ Installation complete!"

check-config:
	@echo "🔧 Validating Azure AI configuration..."
	poetry run python check_config.py

azurelogin:
	@echo "🔐 Setting up Azure AI Foundry authentication..."
	@echo "This will help configure your .env file with Azure AI Foundry credentials"
	@echo ""
	@# Check if Azure CLI is installed
	@command -v az >/dev/null 2>&1 || { echo "❌ Azure CLI not found. Please install: brew install azure-cli"; exit 1; }
	@# Check if logged in
	@az account show >/dev/null 2>&1 || { echo "❌ Please login to Azure first: az login"; exit 1; }
	@# Create .env from .env.example if it doesn't exist
	@if [ ! -f .env ]; then cp .env.example .env; echo "📄 Created .env from .env.example"; fi
	@echo "🔍 Finding Azure AI Foundry resources..."
	@# Get AI services resources with better error handling
	@RESOURCE_INFO=$$(az cognitiveservices account list --query "[?kind=='AIServices' || kind=='OpenAI'].{name:name,resourceGroup:resourceGroupName,location:location,endpoint:properties.endpoint}" -o json 2>/dev/null || echo "[]"); \
	if [ "$${RESOURCE_INFO}" = "[]" ]; then \
		echo "❌ No Azure AI Foundry/OpenAI resources found in your subscription."; \
		echo "Please create an Azure AI Foundry resource first:"; \
		echo "https://portal.azure.com/#create/Microsoft.CognitiveServicesAIServices"; \
		exit 1; \
	fi; \
	echo "📋 Available Azure AI resources:"; \
	echo "$${RESOURCE_INFO}" | jq -r '.[] | "\(.name) (\(.resourceGroup)) - \(.location)"'; \
	echo ""; \
	RESOURCE_NAME=$$(echo "$${RESOURCE_INFO}" | jq -r '.[0].name'); \
	RESOURCE_GROUP=$$(echo "$${RESOURCE_INFO}" | jq -r '.[0].resourceGroup'); \
	ENDPOINT=$$(echo "$${RESOURCE_INFO}" | jq -r '.[0].endpoint'); \
	echo "🎯 Using resource: $${RESOURCE_NAME}"; \
	echo ""; \
	echo "🔑 Attempting to get API key via Azure CLI..."; \
	API_KEY=$$(az cognitiveservices account keys list --name "$${RESOURCE_NAME}" --resource-group "$${RESOURCE_GROUP}" --query "key1" -o tsv 2>/dev/null || echo "ACCESS_DENIED"); \
	if [ "$${API_KEY}" = "ACCESS_DENIED" ]; then \
		echo "⚠️ Cannot retrieve API key automatically (insufficient permissions)"; \
		echo ""; \
		echo "📋 Manual setup required:"; \
		echo "1. Go to Azure Portal: https://portal.azure.com"; \
		echo "2. Navigate to your AI resource: $${RESOURCE_NAME}"; \
		echo "3. Go to 'Keys and Endpoint' section"; \
		echo "4. Copy Key 1 and the endpoint URL"; \
		echo "5. Update your .env file manually:"; \
		echo "   AZURE_OPENAI_ENDPOINT=<your-endpoint-from-portal>"; \
		echo "   AZURE_OPENAI_API_KEY=<your-key-from-portal>"; \
		echo "   AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>"; \
		echo ""; \
		echo "💡 Your current .env has been initialized with template values."; \
		echo "   Edit .env and run 'make check-config' when ready."; \
		exit 1; \
	fi; \
	echo "📋 Getting deployments..."; \
	DEPLOYMENTS=$$(az cognitiveservices account deployment list --name "$${RESOURCE_NAME}" --resource-group "$${RESOURCE_GROUP}" --query "[].{name:name,model:properties.model.name}" -o json 2>/dev/null || echo "[]"); \
	if [ "$${DEPLOYMENTS}" = "[]" ]; then \
		echo "⚠️ No model deployments found. You'll need to create a deployment."; \
		echo "1. Go to Azure AI Foundry Studio: https://ai.azure.com"; \
		echo "2. Select your resource: $${RESOURCE_NAME}"; \
		echo "3. Create a GPT-4 deployment"; \
		DEPLOYMENT_NAME="gpt-4o"; \
	else \
		echo "📋 Available deployments:"; \
		echo "$${DEPLOYMENTS}" | jq -r '.[] | "\(.name) (\(.model))"'; \
		DEPLOYMENT_NAME=$$(echo "$${DEPLOYMENTS}" | jq -r '.[0].name'); \
		echo "🎯 Using deployment: $${DEPLOYMENT_NAME}"; \
	fi; \
	echo ""; \
	echo "✏️ Updating .env file..."; \
	if [[ "$${ENDPOINT}" == *"cognitiveservices.azure.com"* ]]; then \
		FOUNDRY_ENDPOINT=$${ENDPOINT}; \
		echo "ℹ️ Using standard Azure OpenAI endpoint format"; \
	else \
		FOUNDRY_ENDPOINT="$${ENDPOINT}"; \
		echo "ℹ️ Using Azure AI Foundry endpoint format"; \
	fi; \
	sed -i.backup "s|AZURE_OPENAI_ENDPOINT=.*|AZURE_OPENAI_ENDPOINT=$${FOUNDRY_ENDPOINT}|" .env; \
	sed -i.backup "s|AZURE_OPENAI_API_KEY=.*|AZURE_OPENAI_API_KEY=$${API_KEY}|" .env; \
	sed -i.backup "s|AZURE_OPENAI_DEPLOYMENT_NAME=.*|AZURE_OPENAI_DEPLOYMENT_NAME=$${DEPLOYMENT_NAME}|" .env; \
	rm -f .env.backup; \
	echo "✅ Azure AI Foundry configuration complete!"; \
	echo ""; \
	echo "📋 Configuration summary:"; \
	echo "   Resource: $${RESOURCE_NAME}"; \
	echo "   Endpoint: $${FOUNDRY_ENDPOINT}"; \
	echo "   Deployment: $${DEPLOYMENT_NAME}"; \
	echo "   API Key: $${API_KEY:0:8}..."; \
	echo ""; \
	echo "🔧 Run 'make check-config' to verify the configuration"

run:
	@echo "🚀 Running pipeline analysis with example question..."
	poetry run foundry-pipeline-assistant -q "Analyze the current CI/CD pipeline health and identify any potential issues or improvements" --output markdown

run-custom:
	@echo "🎯 Running pipeline analysis with custom question..."
	@read -p "Enter your question: " question; \
	poetry run foundry-pipeline-assistant -q "$$question" --output markdown

run-json:
	@echo "🚀 Running pipeline analysis (JSON output)..."
	poetry run foundry-pipeline-assistant -q "Analyze the current CI/CD pipeline health and identify any potential issues or improvements" --output json

run-quiet:
	@echo "🤫 Running pipeline analysis (quiet mode)..."
	poetry run foundry-pipeline-assistant -q "Analyze the current CI/CD pipeline health and identify any potential issues or improvements" --quiet --output markdown

run-verbose:
	@echo "📊 Running pipeline analysis (verbose mode)..."
	poetry run foundry-pipeline-assistant -q "Analyze the current CI/CD pipeline health and identify any potential issues or improvements" --verbose --output markdown

test:
	@echo "🧪 Running test suite..."
	poetry run python run_tests.py
	@echo "✅ Tests complete!"

test-smoke:
	@echo "🔥 Running smoke test..."
	poetry run python run_tests.py smoke

test-pytest: 
	@echo "🧪 Running tests with pytest..."
	pytest

lint:
	@echo "🔍 Checking code quality..."
	ruff check .

lint-fix:
	@echo "🔧 Fixing code quality issues..."
	ruff check --fix .

format:
	@echo "🎨 Formatting code..."
	ruff format .

clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -f report.json 2>/dev/null || true
	@echo "✅ Cleanup complete!"

dev-setup:
	@echo "🛠️  Setting up development environment..."
	@echo "1️⃣  Checking for .env file..."
	@if [ ! -f .env ]; then \
		echo "⚠️  .env file not found. Copying from .env.example..."; \
		cp .env.example .env; \
		echo "✅ Created .env file. Please edit it with your Azure AI credentials."; \
	else \
		echo "✅ .env file exists."; \
	fi
	@echo "2️⃣  Installing dependencies..."
	$(MAKE) install
	@echo "3️⃣  Running smoke test..."
	$(MAKE) test-smoke
	@echo "🎉 Development environment ready!"
	@echo ""
	@echo "📝 Next steps:"
	@echo "  1. Edit .env with your Azure AI Foundry credentials"
	@echo "  2. Run 'make run' to test the pipeline"

# Health check
health:
	@echo "🩺 System health check..."
	foundry-pipeline-assistant --help > /dev/null && echo "✅ CLI working"
	poetry run python -c "from services import run; print('✅ Services importable')"
	poetry run python -c "from common import llm_text; print('✅ Azure AI client available')"

# Production-like run
prod-run:
	@echo "🏭 Production-style run..."
	poetry run foundry-pipeline-assistant --question "Production health check" --output prod-report.json
	@echo "📄 Report saved to prod-report.json"

# Development workflow
dev: clean dev-setup test lint
	@echo "🎯 Development workflow complete!"

# Show project structure
tree:
	@echo "📁 Project structure:"
	@if command -v tree >/dev/null 2>&1; then \
		tree -I '__pycache__|*.pyc|*.egg-info|.pytest_cache' .; \
	else \
		find . -type f -name "*.py" | head -20; \
		echo "... (install 'tree' command for full view)"; \
	fi

# Check environment
check-env:
	@echo "🔍 Environment check:"
	@echo "Python: $(shell python --version)"
	@echo "Pip: $(shell pip --version)"
	@if [ -f .env ]; then \
		echo "✅ .env file exists"; \
		if grep -q "your-api-key-here" .env; then \
			echo "⚠️  .env contains placeholder values - please update with real credentials"; \
		else \
			echo "✅ .env appears configured"; \
		fi \
	else \
		echo "❌ .env file missing - run 'make dev-setup'"; \
	fi