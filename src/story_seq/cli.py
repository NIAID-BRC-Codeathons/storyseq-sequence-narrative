"""CLI interface for story-seq."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from story_seq import __version__
from story_seq.config import load_config, get_config_path

app = typer.Typer(
    name="story-seq",
    help="A CLI tool for sequence narrative analysis using AI",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Display version information."""
    if value:
        console.print(f"[bold blue]story-seq[/bold blue] version: [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """
    Story-Seq: A CLI tool for sequence narrative analysis.

    Use --help with any command to see detailed help information.
    """
    pass


@app.command()
def blast(
    query: Annotated[
        Path,
        typer.Argument(
            help="Query FASTA file path",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    database: Annotated[
        str,
        typer.Option(
            "--database",
            "-d",
            help="Database to search against",
        ),
    ] = "",
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output file path",
        ),
    ] = "",
    llm_api_url: Annotated[
        Optional[str],
        typer.Option(
            "--llm-api-url",
            help="LLM API endpoint URL (overrides config file)",
        ),
    ] = None,
    llm_model: Annotated[
        Optional[str],
        typer.Option(
            "--llm-model",
            help="LLM model to use (overrides config file)",
        ),
    ] = None,
    llm_api_key: Annotated[
        Optional[str],
        typer.Option(
            "--llm-api-key",
            help="API key for LLM service (overrides config file)",
        ),
    ] = None,
    question: Annotated[
        str,
        typer.Option(
            "--question",
            help="Question to ask the LLM about the BLAST results",
        ),
    ] = "",
) -> None:
    """
    Run BLAST analysis on sequences.

    This command will perform BLAST searches and integrate results
    with AI-powered narrative analysis.
    
    Configuration is loaded from ~/.storyseq/config.json by default,
    or from the path specified in STORY_SEQ_CONFIG environment variable.
    Command-line parameters override configuration file values.
    """
    # Load config from file
    config = load_config()
    
    # Override with command-line parameters if provided
    final_llm_api_url = llm_api_url or config.llm_api_url
    final_llm_model = llm_model or config.llm_model
    final_llm_api_key = llm_api_key or config.llm_api_key
    
    # Display current configuration
    console.print("[yellow]BLAST command is not yet implemented.[/yellow]")
    console.print()
    
    # Create a table for better display
    table = Table(title="Configuration")
    table.add_column("Parameter", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    table.add_row("Config File", str(get_config_path()))
    table.add_row("Query", str(query))
    table.add_row("Database", database if database else "[dim]Not specified[/dim]")
    table.add_row("Output", output if output else "[dim]Not specified[/dim]")
    table.add_row("Question", question if question else "[dim]Not specified[/dim]")
    table.add_row("LLM API URL", final_llm_api_url if final_llm_api_url else "[dim]Not specified[/dim]")
    table.add_row("LLM Model", final_llm_model)
    table.add_row("LLM API Key", "[dim]***[/dim]" if final_llm_api_key else "[dim]Not specified[/dim]")
    
    console.print(table)


if __name__ == "__main__":
    app()
