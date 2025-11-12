# StorySeq: Automated Sequence Narrative Generation

Automating sequence identification and contextualization using BLAST, database queries, and LLM narrative synthesis to accelerate pathogen and AMR gene discovery

## About This Project

This is a project from the **NIAID BRC AI Codeathon 2025**, taking place November 12-14, 2025 at Argonne National Laboratory.

**Event Website:** https://niaid-brc-codeathons.github.io/

## Features

- **BLAST Integration**: Run BLAST searches with ease
- **AI-Powered Narratives**: Generate narratives from sequence data using Pydantic AI
- **Graph-based Analysis**: Leverage Pydantic Graph for complex data relationships
- **Rich CLI**: Beautiful command-line interface powered by Typer and Rich

## Installation

### From source

```bash
# Clone the repository
git clone <repository-url>
cd storyseq-sequence-narrative

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Usage

### Basic Commands

```bash
# Show help
story-seq --help

# Show version
story-seq --version

# BLAST command (not yet implemented)
story-seq blast --query sequence.fasta --database mydb
```

### BLAST Command

The `blast` command will perform BLAST searches and integrate results with AI-powered narrative analysis.

```bash
story-seq blast --query <query-file> --database <database-name> --output <output-file>
```

Options:
- `--query, -q`: Query sequence or file path
- `--database, -d`: Database to search against
- `--output, -o`: Output file path
- `--llm-api-url`: LLM API endpoint URL (overrides config file)
- `--llm-model`: LLM model to use (overrides config file)
- `--llm-api-key`: API key for LLM service (overrides config file)

### Configuration

Story-seq uses a configuration file to store default settings. By default, the configuration is stored at `~/.storyseq/config.json`.

You can specify a custom configuration file location by setting the `STORY_SEQ_CONFIG` environment variable:

```bash
export STORY_SEQ_CONFIG=/path/to/custom/config.json
```

Example configuration file (`~/.storyseq/config.json`):

```json
{
  "llm_api_url": "https://api.openai.com/v1",
  "llm_model": "gpt-4",
  "llm_api_key": "your-api-key-here",
  "blast_db_path": "/path/to/blast/db",
  "blast_evalue": 0.001,
  "max_tokens": 2000
}
```

Command-line parameters always override configuration file values.

## Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=story_seq --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
storyseq-sequence-narrative/
├── src/
│   └── story_seq/
│       ├── __init__.py
│       ├── cli.py          # CLI interface
│       ├── config.py       # Configuration management
│       └── models.py       # Pydantic models
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_models.py
├── pyproject.toml          # Project configuration
├── README.md
└── .gitignore
```

## Dependencies

- **Typer**: Modern CLI framework
- **Pydantic**: Data validation and settings management
- **Pydantic AI**: AI integration for narrative generation
- **Rich**: Beautiful terminal output

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

**Project Details:** https://niaid-brc-codeathons.github.io/projects/storyseq-sequence-narrative/

## Codeathon Goals

The NIAID Bioinformatics Resource Centers (BRCs) invite researchers, data scientists, and developers to a three-day AI Codeathon focused on improving Findability, Accessibility, Interoperability, and Reusability (FAIR-ness) of BRC data and tools using artificial intelligence (AI) and large language models (LLMs).

## Getting Started

*Team members: Add your project setup instructions here.*

## Team

*Team members: Add your team information here.*

## License

*To be determined by the team.*
