#!/usr/bin/env python3
"""
Configuration validator for foundry-pipeline-assistant.

Helps users validate their Azure AI setup and environment configuration.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and has proper structure."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    print("🔍 Checking environment configuration...")
    print("=" * 50)
    
    # Check if .env exists
    if not env_file.exists():
        print("❌ .env file not found")
        if env_example.exists():
            print("💡 Solution: Copy .env.example to .env")
            print("   cp .env.example .env")
        else:
            print("❌ .env.example also missing - check project setup")
        return False
    
    print("✅ .env file exists")
    
    # Load environment variables
    load_dotenv()
    
    # Check required variables
    required_vars = {
        'AZURE_OPENAI_ENDPOINT': 'Azure OpenAI endpoint URL',
        'AZURE_OPENAI_API_KEY': 'Azure OpenAI API key', 
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'GPT model deployment name'
    }
    
    all_configured = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"❌ {var} not set")
            all_configured = False
        elif value in ['your-api-key-here', 'your-foundry-resource.services.ai.azure.com/api/projects/your-project', 'your-gpt-deployment-name']:
            print(f"⚠️  {var} contains placeholder value")
            print(f"   Please update with your actual {description}")
            all_configured = False
        else:
            print(f"✅ {var} configured")
    
    # Check optional variables
    api_version = os.getenv('AZURE_API_VERSION', '2024-02-01')
    print(f"ℹ️  AZURE_API_VERSION: {api_version} (using default)")
    
    return all_configured


def test_azure_connection():
    """Test basic Azure AI connection without making actual calls."""
    print("\n🔗 Testing Azure AI configuration...")
    print("=" * 50)
    
    try:
        # Import after dotenv loading
        from common.azure_ai import AzureAIClient
        
        # Try to create client (will validate configuration)
        client = AzureAIClient()
        print("✅ Azure AI client initialized successfully")
        print(f"   Endpoint: {client.endpoint}")
        print(f"   Deployment: {client.deployment}")
        print(f"   API Version: {client.api_version}")
        return True
        
    except Exception as e:
        print(f"❌ Azure AI client initialization failed:")
        print(f"   {str(e)}")
        return False


def test_service_imports():
    """Test that all service modules can be imported."""
    print("\n📦 Testing service imports...")
    print("=" * 50)
    
    services_to_test = [
        ('services.bamboo_mock', 'Bamboo mock service'),
        ('services.logs_mock', 'Logs mock service'),
        ('services.analyzer_agent', 'Analyzer agent'),
        ('services.reporting_agent', 'Reporting agent'),
        ('services.orchestrator', 'Orchestrator'),
    ]
    
    all_imported = True
    
    for module_name, description in services_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            all_imported = False
    
    return all_imported


def main():
    """Run complete configuration validation."""
    print("🛠️  Foundry Pipeline Assistant - Configuration Validator")
    print("=" * 60)
    
    # Check environment file
    env_ok = check_env_file()
    
    if not env_ok:
        print("\n❌ Environment configuration incomplete")
        print("\n📋 Next steps:")
        print("1. Copy .env.example to .env:")
        print("   cp .env.example .env")
        print("2. Edit .env with your Azure AI Foundry credentials")
        print("3. Run this validator again: python check_config.py")
        sys.exit(1)
    
    # Test service imports
    imports_ok = test_service_imports()
    
    if not imports_ok:
        print("\n❌ Service imports failed - check package installation")
        print("   Run: pip install -e '.[dev]'")
        sys.exit(1)
    
    # Test Azure connection
    azure_ok = test_azure_connection()
    
    # Final status
    print("\n" + "=" * 60)
    print("🎯 CONFIGURATION SUMMARY")
    print("=" * 60)
    
    if env_ok and imports_ok and azure_ok:
        print("🎉 All systems ready!")
        print("✅ Environment configured")
        print("✅ Services available")
        print("✅ Azure AI client ready")
        print("\n🚀 You can now run: foundry-pipeline-assistant")
        
    else:
        print("⚠️  Configuration issues detected:")
        if not env_ok:
            print("   - Environment variables need setup")
        if not imports_ok:
            print("   - Package dependencies missing")
        if not azure_ok:
            print("   - Azure AI configuration invalid")
        
        print("\n📚 Troubleshooting:")
        print("   - Check README.md for setup instructions")
        print("   - Verify Azure AI credentials in Azure Portal")
        print("   - Ensure all dependencies installed: pip install -e '.[dev]'")
        
        sys.exit(1)


if __name__ == '__main__':
    main()