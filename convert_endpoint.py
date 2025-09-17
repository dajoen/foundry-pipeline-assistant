#!/usr/bin/env python3
"""
Azure AI Foundry endpoint converter.

Helps convert between Azure OpenAI and Azure AI Foundry endpoint formats.
"""

import os
import sys
from pathlib import Path

def convert_endpoint_format():
    """Convert Azure OpenAI endpoint to Azure AI Foundry format."""
    
    # Load current endpoint from .env
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    current_endpoint = None
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip().startswith('AZURE_OPENAI_ENDPOINT='):
                current_endpoint = line.split('=', 1)[1].strip()
                break
    
    if not current_endpoint:
        print("❌ AZURE_OPENAI_ENDPOINT not found in .env")
        return False
    
    print(f"📋 Current endpoint: {current_endpoint}")
    
    # Check if it's already in the right format
    if '/api/projects/' in current_endpoint:
        print("✅ Endpoint already in Azure AI Foundry format")
        return True
    
    # Try to convert from standard Azure OpenAI to Foundry format
    if '.cognitiveservices.azure.com' in current_endpoint:
        print("🔄 Converting from Azure OpenAI to Azure AI Foundry format...")
        
        # Extract resource name
        resource_name = current_endpoint.split('//')[1].split('.')[0]
        print(f"📍 Detected resource: {resource_name}")
        
        # Prompt user for project name
        project_name = input("🔧 Enter your Azure AI Foundry project name: ").strip()
        if not project_name:
            print("❌ Project name required for conversion")
            return False
        
        # Build new endpoint
        new_endpoint = f"https://{resource_name}.services.ai.azure.com/api/projects/{project_name}"
        
        print(f"🎯 New endpoint: {new_endpoint}")
        
        # Update .env file
        env_content = env_file.read_text()
        updated_content = env_content.replace(
            f"AZURE_OPENAI_ENDPOINT={current_endpoint}",
            f"AZURE_OPENAI_ENDPOINT={new_endpoint}"
        )
        
        env_file.write_text(updated_content)
        print("✅ Updated .env with Azure AI Foundry endpoint format")
        
        return True
    
    print("⚠️ Unrecognized endpoint format")
    return False


def main():
    """Main conversion function."""
    print("🔄 Azure AI Foundry Endpoint Converter")
    print("=" * 50)
    
    if convert_endpoint_format():
        print("\n🎉 Endpoint conversion complete!")
        print("🔧 Run 'make check-config' to verify the new configuration")
    else:
        print("\n❌ Conversion failed")
        print("💡 Please check your .env file and endpoint format")
        sys.exit(1)


if __name__ == '__main__':
    main()