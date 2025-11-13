"""CLI interface for story-seq."""

import asyncio
from pathlib import Path
from typing import Optional, Any
import typer
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from typing_extensions import Annotated

from story_seq import __version__
from story_seq.config import load_config, get_config_path, save_config, StorySeqConfig


def paths_to_strings(obj: Any) -> Any:
    """Recursively convert Path objects to strings for JSON serialization."""
    if isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: paths_to_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [paths_to_strings(item) for item in obj]
    else:
        return obj

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
def init(
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite existing configuration file",
        ),
    ] = False,
) -> None:
    """
    Initialize story-seq configuration.
    
    Creates a default configuration file at ~/.storyseq/config.json
    (or at the path specified by STORY_SEQ_CONFIG environment variable).
    """
    config_path = get_config_path()
    
    # Check if config already exists
    if config_path.exists() and not force:
        console.print(f"[yellow]Configuration file already exists at:[/yellow] {config_path}")
        console.print("[dim]Use --force to overwrite[/dim]")
        raise typer.Exit(0)
    
    # Create default configuration
    default_config = StorySeqConfig(
        llm_api_url="http://lambda5.cels.anl.gov:44497/v1",
        llm_model="gpt5",
        llm_api_key=".",
    )
    
    # Save configuration
    try:
        save_config(default_config)
        console.print(f"[green]✓[/green] Configuration file created at: [cyan]{config_path}[/cyan]")
        console.print()
        
        # Display the configuration
        table = Table(title="Default Configuration")
        table.add_column("Parameter", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        table.add_row("LLM API URL", default_config.llm_api_url or "[dim]Not set[/dim]")
        table.add_row("LLM Model", default_config.llm_model)
        table.add_row("LLM API Key", default_config.llm_api_key or "[dim]Not set[/dim]")
        table.add_row("BLAST E-value", str(default_config.blast_evalue))
        table.add_row("Max Tokens", str(default_config.max_tokens))
        
        console.print(table)
        console.print()
        console.print("[dim]You can edit this file directly or override values using command-line options.[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to create configuration file: {e}")
        raise typer.Exit(1)


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


@app.command()
def run_agent(
    agent_name: Annotated[
        str,
        typer.Argument(
            help="Name of the agent to run (configuration, blast, data_decoration, reporter, validation)",
        ),
    ],
    query: Annotated[
        Optional[Path],
        typer.Option(
            "--query",
            "-q",
            help="Query FASTA file path",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
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
    ] = "output.txt",
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
    ] = ""
) -> None:
    """
    Run a specific agent with custom parameters.
    
    This command allows you to run individual agents from the story-seq pipeline
    with custom prompts and parameters.
    
    Available agents:
    - configuration: Manage and validate configuration settings
    - blast: Execute BLAST searches and parse results
    - data_decoration: Enrich sequence data with annotations
    - reporter: Generate narrative reports from results
    - validation: Validate inputs and results for quality control
    
    Configuration is loaded from ~/.storyseq/config.json by default,
    or from the path specified in STORY_SEQ_CONFIG environment variable.
    Command-line parameters override configuration file values.
    """
    # Load config from file
    config = load_config()
    
    # Override with command-line parameters if provided (check for None explicitly)
    final_llm_api_url = llm_api_url if llm_api_url is not None else config.llm_api_url
    final_llm_model = llm_model if llm_model is not None else config.llm_model
    final_llm_api_key = llm_api_key if llm_api_key is not None else config.llm_api_key
    
    # Validate agent name
    valid_agents = ["configuration", "blast", "data_decoration", "reporter", "validation"]
    if agent_name not in valid_agents:
        console.print(f"[red]Error:[/red] Invalid agent name '{agent_name}'")
        console.print(f"Valid agents: {', '.join(valid_agents)}")
        raise typer.Exit(1)
    
    # Display current configuration
    console.print(f"[bold cyan]Running Agent:[/bold cyan] {agent_name}")
    console.print()
    
    # Create a table for better display
    table = Table(title="Agent Configuration")
    table.add_column("Parameter", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    table.add_row("Agent", agent_name)
    table.add_row("Config File", str(get_config_path()))
    if query:
        table.add_row("Query", str(query))
    table.add_row("Database", database if database else "[dim]Not specified[/dim]")
    table.add_row("Output", output if output else "[dim]Not specified[/dim]")
    table.add_row("Question", question if question else "[dim]Not specified[/dim]")
    table.add_row("LLM API URL", final_llm_api_url if final_llm_api_url else "[dim]Not specified[/dim]")
    table.add_row("LLM Model", final_llm_model)
    table.add_row("LLM API Key", "[dim]***[/dim]" if final_llm_api_key else "[dim]Not specified[/dim]")
    
    console.print(table)
    console.print()
    
    # Run the async implementation
    results = asyncio.run(_run_agent_async(
        agent_name=agent_name,
        query=query,
        database=database,
        output=output,
        llm_api_url=final_llm_api_url,
        llm_model=final_llm_model,
        llm_api_key=final_llm_api_key,
        question=question
    ))
    
    # Print results
    console.print("[bold green]Results:[/bold green]")
    console.print(results.output)


async def _run_agent_async(
    agent_name: str,
    query: Optional[Path],
    database: str,
    output: str,
    llm_api_url: Optional[str],
    llm_model: str,
    llm_api_key: Optional[str],
    question: str,
):
    """Async implementation of run_agent command - just runs and returns results."""
    # Import agents
    try:
        from story_seq.agent import (
            get_configuration_agent,
            get_blast_agent,
            get_data_decoration_agent,
            get_reporter_agent,
            get_validation_agent,
        )
        from story_seq.agent.configuration_agent import ConfigurationAgentDeps
        from story_seq.agent.blast_agent import BlastAgentDeps
        from story_seq.agent.data_decoration_agent import DataDecorationAgentDeps
        from story_seq.agent.reporter_agent import ReporterAgentDeps
        from story_seq.agent.validation_agent import ValidationAgentDeps
        from story_seq.util import process_multiple_files
    except ImportError as e:
        console.print(f"[red]Error:[/red] Failed to import agents: {e}")
        console.print("[yellow]Make sure pydantic-ai is installed: pip install pydantic-ai[/yellow]")
        raise typer.Exit(1)
    
    # Get the appropriate agent based on agent_name
    agent = None
    deps = None
    try:
        if agent_name == "configuration":
            agent = await get_configuration_agent(
                llm_api_url=llm_api_url,
                llm_api_key=llm_api_key,
                model_name=llm_model,
            )
            # Process FASTA file(s) if provided
            fasta_sketch = None
            if query:
                try:
                    raw_fasta_sketch = process_multiple_files([query])
                    fasta_sketch = paths_to_strings(raw_fasta_sketch)
                except Exception as e:
                    console.print(f"[yellow]Warning:[/yellow] Error processing FASTA file: {e}")
            
            # Create dependencies for the configuration agent
            deps = ConfigurationAgentDeps(
                question=question,
                query=query,
                sequence_type="",  # Could be determined from the file
                fasta_sketch=fasta_sketch,
            )
        elif agent_name == "blast":
            agent = await get_blast_agent(
                llm_api_url=llm_api_url,
                llm_api_key=llm_api_key,
                model_name=llm_model,
            )
            # Create dependencies for the blast agent
            if query:
                deps = BlastAgentDeps(
                    query_file=query,
                    database=database if database else "nr",
                    evalue=0.001,
                )
        elif agent_name == "data_decoration":
            agent = await get_data_decoration_agent(
                llm_api_url=llm_api_url,
                llm_api_key=llm_api_key,
                model_name=llm_model,
            )
            # Create dependencies for the data decoration agent
            # Convert any Path objects in blast_results to strings
            deps = DataDecorationAgentDeps(
                blast_results=paths_to_strings([]),  # Would normally come from previous step
                include_taxonomy=True,
                include_functional=True,
            )
        elif agent_name == "reporter":
            agent = await get_reporter_agent(
                llm_api_url=llm_api_url,
                llm_api_key=llm_api_key,
                model_name=llm_model,
            )
            # Create dependencies for the reporter agent
            # Convert any Path objects to strings
            deps = ReporterAgentDeps(
                blast_results=paths_to_strings([]),  # Would normally come from previous step
                enriched_data=paths_to_strings(None),
                question=question if question else None,
            )
        elif agent_name == "validation":
            agent = await get_validation_agent(
                llm_api_url=llm_api_url,
                llm_api_key=llm_api_key,
                model_name=llm_model,
            )
            # Create dependencies for the validation agent
            deps = ValidationAgentDeps(
                fasta_file=query,
                blast_results=None,
                narrative=None,
                strict_mode=False,
            )
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to create agent: {e}")
        raise typer.Exit(1)
    
    # Run the agent and return results
    # Pass deps if the agent uses them, otherwise just the question
    if deps:
        results = await agent.run(question, deps=deps)
    else:
        results = await agent.run(question)
        
    return results


if __name__ == "__main__":
    app()
