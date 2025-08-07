"""
Command Line Interface for log-whisperer
"""
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .config import Config, list_supported_providers, get_provider_info
from .llm_factory import llm_factory
from .chat import LogAnalyzer

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Log Whisperer - An AI log analyzer with chat interface"""
    pass


@main.command()
def configure():
    """Configure LLM provider settings"""
    console.print(Panel.fit(
        "[bold blue]Log Whisperer Configuration[/bold blue]",
        border_style="blue"
    ))
    
    config = Config()
    
    # Show supported providers
    providers = list_supported_providers()
    console.print("\n[bold]Supported LLM Providers:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan")
    table.add_column("Description", style="white")
    
    provider_descriptions = {
        "openai": "OpenAI GPT models (GPT-3.5, GPT-4, etc.)",
        "anthropic": "Anthropic Claude models",
        "google": "Google Gemini models",
        "cohere": "Cohere Command models", 
        "huggingface": "Hugging Face Hub models",
        "ollama": "Local Ollama models"
    }
    
    for provider in providers:
        description = provider_descriptions.get(provider, "")
        table.add_row(provider, description)
    
    console.print(table)
    
    # Get provider choice
    provider = click.prompt(
        "\nSelect LLM provider", 
        type=click.Choice(providers, case_sensitive=False),
        show_choices=False
    ).lower()
    
    provider_info = get_provider_info(provider)
    
    # Get model name
    console.print(f"\n[bold]Configuring {provider.title()} provider[/bold]")
    
    # Suggest common models based on provider
    model_suggestions = {
        "openai": "gpt-3.5-turbo, gpt-4, gpt-4-turbo",
        "anthropic": "claude-3-sonnet-20240229, claude-3-haiku-20240307",
        "google": "gemini-pro, gemini-pro-vision",
        "cohere": "command, command-nightly",
        "huggingface": "microsoft/DialoGPT-medium, meta-llama/Llama-2-7b-chat-hf",
        "ollama": "llama2, mistral, codellama"
    }
    
    if provider in model_suggestions:
        console.print(f"[dim]Popular models: {model_suggestions[provider]}[/dim]")
    
    model = click.prompt("Model name")
    
    # Collect configuration
    provider_config = {
        "provider": provider,
        "model": model
    }
    
    # Get required parameters
    for param in provider_info["required_params"]:
        if param.endswith("_key") or param.endswith("_token"):
            value = click.prompt(f"{param.replace('_', ' ').title()}", hide_input=True)
        else:
            value = click.prompt(f"{param.replace('_', ' ').title()}")
        provider_config[param] = value
    
    # Get optional parameters
    console.print("\n[bold]Optional Parameters (press Enter to skip):[/bold]")
    for param in provider_info["optional_params"]:
        if param in ["temperature"]:
            value = click.prompt(
                f"{param.replace('_', ' ').title()} (0.0-1.0)",
                type=float,
                default=None,
                show_default=False
            )
        elif param in ["max_tokens", "max_output_tokens", "max_new_tokens", "num_predict"]:
            value = click.prompt(
                f"{param.replace('_', ' ').title()}",
                type=int,
                default=None,
                show_default=False
            )
        elif param in ["top_p", "p"]:
            value = click.prompt(
                f"{param.replace('_', ' ').title()} (0.0-1.0)",
                type=float,
                default=None,
                show_default=False
            )
        else:
            value = click.prompt(
                f"{param.replace('_', ' ').title()}",
                default=None,
                show_default=False
            )
        
        if value is not None:
            provider_config[param] = value
    
    # Special handling for Ollama base URL
    if provider == "ollama":
        base_url = click.prompt(
            "Base URL (e.g., http://localhost:11434)",
            default="http://localhost:11434",
            show_default=True
        )
        if base_url:
            provider_config["base_url"] = base_url
    
    # Test the configuration
    console.print("\n[yellow]Testing configuration...[/yellow]")
    try:
        success = llm_factory.test_provider_connection(provider, model, provider_config)
        if success:
            # Save configuration
            config.set_provider_config(provider_config)
            console.print("\n[green]✓ Configuration saved successfully![/green]")
            console.print(f"[dim]Configuration saved to: {config.config_file}[/dim]")
        else:
            console.print("\n[red]✗ Configuration test failed. Please check your settings and try again.[/red]")
            return
    except Exception as e:
        console.print(f"\n[red]✗ Configuration test failed: {e}[/red]")
        console.print("[yellow]Configuration saved anyway. You can test it manually later.[/yellow]")
        config.set_provider_config(provider_config)


@main.command()
@click.option(
    "--log-file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the log file to analyze"
)
@click.option(
    "--save",
    type=click.Path(path_type=Path),
    help="Path to save the conversation (optional)"
)
def chat(log_file: Path, save: Path):
    """Start interactive chat session for log analysis"""
    try:
        # Check if configuration exists
        config = Config()
        provider_config = config.get_provider_config()
        if not provider_config:
            console.print("[red]✗ No LLM provider configured.[/red]")
            console.print("Please run '[cyan]log-whisperer configure[/cyan]' first.")
            return
        
        # Initialize and start chat
        analyzer = LogAnalyzer(str(log_file), str(save) if save else None)
        analyzer.start_chat()
        
    except Exception as e:
        console.print(f"[red]✗ Error starting chat: {e}[/red]")


@main.command()
def status():
    """Show current configuration status"""
    config = Config()
    provider_config = config.get_provider_config()
    
    if not provider_config:
        console.print("[yellow]No LLM provider configured.[/yellow]")
        console.print("Run '[cyan]log-whisperer configure[/cyan]' to set up a provider.")
        return
    
    # Display current configuration
    table = Table(title="Current Configuration", show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Provider", provider_config.get("provider", "Not set"))
    table.add_row("Model", provider_config.get("model", "Not set"))
    
    # Show optional parameters if set
    for key, value in provider_config.items():
        if key not in ["provider", "model"] and not key.endswith("_key") and not key.endswith("_token"):
            table.add_row(key.replace("_", " ").title(), str(value))
    
    # Hide sensitive information
    for key in provider_config:
        if key.endswith("_key") or key.endswith("_token"):
            table.add_row(key.replace("_", " ").title(), "***configured***")
    
    console.print(table)
    console.print(f"\n[dim]Configuration file: {config.config_file}[/dim]")


@main.command()
def reset():
    """Reset configuration"""
    config = Config()
    if click.confirm("Are you sure you want to reset all configuration?"):
        try:
            config.config_file.unlink(missing_ok=True)
            console.print("[green]✓ Configuration reset successfully.[/green]")
        except Exception as e:
            console.print(f"[red]✗ Error resetting configuration: {e}[/red]")


if __name__ == "__main__":
    main()