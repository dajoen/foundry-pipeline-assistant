#!/usr/bin/env python3
"""
CLI entrypoint for the foundry-pipeline-assistant.

Provides command-line interface for pipeline analysis with configurable
questions and multiple output formats.
"""

import json
import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

from services.orchestrator import run


def validate_azure_config() -> None:
    """Validate Azure AI configuration before running analysis."""
    required_vars = ['AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_DEPLOYMENT_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        missing_list = ", ".join(missing_vars)
        click.echo("❌ Azure AI Configuration Error", err=True)
        click.echo("=" * 40, err=True)
        click.echo(f"Missing required environment variables: {missing_list}", err=True)
        click.echo("", err=True)
        click.echo("🔧 Setup Instructions:", err=True)
        click.echo("1. Copy .env.example to .env:", err=True)
        click.echo("   cp .env.example .env", err=True)
        click.echo("", err=True)
        click.echo("2. Edit .env with your Azure AI Foundry credentials:", err=True)
        click.echo("   AZURE_OPENAI_ENDPOINT=https://your-foundry-resource.services.ai.azure.com/api/projects/your-project", err=True)
        click.echo("   AZURE_OPENAI_API_KEY=your-api-key-here", err=True)
        click.echo("   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o", err=True)
        click.echo("", err=True)
        click.echo("📍 Get credentials from: Azure AI Foundry -> Projects -> Your Project -> Settings", err=True)
        sys.exit(1)


@click.command()
@click.option('--question', '-q', 
              help='The question to analyze about CI/CD pipelines',
              required=True)
@click.option('--output', '-o', 
              type=click.Choice(['json', 'yaml', 'markdown']), 
              default='json',
              help='Output format (default: json)')
@click.option('--quiet', is_flag=True, help='Suppress progress messages')
@click.option('--verbose', is_flag=True, help='Show detailed processing steps')
def main(question, output, quiet, verbose):
    """Foundry Pipeline Assistant - AI-powered CI/CD pipeline analysis."""
    
    # Validate Azure configuration early
    validate_azure_config()
    
    if not quiet:
        click.echo("🚀 Starting pipeline analysis...")
        if verbose:
            click.echo(f"Question: {question}")
            click.echo(f"Output format: {output}")
    
    try:
        # Run the orchestrator
        result = run(question)
        
        if verbose:
            click.echo(f"✅ Analysis completed in {result['workflow_info']['execution_time_seconds']:.2f} seconds")
            click.echo(f"📊 Analyzed {result['outputs']['report']['stats']['pipelines_total']} pipelines")
            click.echo(f"🔍 Found {result['outputs']['report']['stats']['errors_total']} total errors")
        
        # Output results based on format
        if output == 'json':
            click.echo(json.dumps(result, indent=2))
        elif output == 'yaml':
            try:
                import yaml
                click.echo(yaml.dump(result, default_flow_style=False))
            except ImportError:
                click.echo("❌ YAML output requires PyYAML. Install with: pip install PyYAML", err=True)
                click.echo("Falling back to JSON output:", err=True)
                click.echo(json.dumps(result, indent=2))
        elif output == 'markdown':
            # Output the markdown report
            click.echo(result['outputs']['report']['markdown'])
            
            if verbose:
                click.echo("\n" + "="*60)
                click.echo("📋 EXECUTION SUMMARY")
                click.echo("="*60)
                
                # Show key metrics
                stats = result['outputs']['report']['stats']
                click.echo(f"Total Pipelines: {stats['pipelines_total']}")
                click.echo(f"Total Runs: {stats['runs_total']}")
                click.echo(f"Errors Found: {stats['errors_total']}")
                click.echo(f"Average Duration: {stats['avg_duration_seconds']}s")
                
                # Show failing pipelines specifically
                if result['outputs']['analyses']:
                    failing_pipelines = []
                    for analysis in result['outputs']['analyses']:
                        if analysis['top_errors']:
                            failing_pipelines.append(analysis['pipeline_key'])
                    
                    if failing_pipelines:
                        click.echo(f"\n🔴 Failing Pipelines: {', '.join(failing_pipelines)}")
                    else:
                        click.echo(f"\n✅ No actively failing pipelines detected")
                        
    except Exception as e:
        click.echo(f"❌ Error during analysis: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()