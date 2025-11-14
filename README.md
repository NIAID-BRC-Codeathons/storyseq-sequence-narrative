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

### Initialization

Before using story-seq, initialize the configuration file:

```bash
story-seq init
```

This creates a default configuration file at `~/.storyseq/config.json` with:
- LLM API URL: `http://lambda5.cels.anl.gov:44497/v1`
- LLM Model: `gpt5`
- LLM API Key: `.`

Options:
- `--force, -f`: Overwrite existing configuration file

### Basic Commands

```bash
# Show help
story-seq --help

# Show version
story-seq --version

# Initialize configuration
story-seq init

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

### Run Agent Command

The `run-agent` command allows you to run individual agents from the pipeline with custom prompts.

```bash
story-seq run-agent <agent-name> [options]
```

Available agents:
- `configuration`: Manage and validate configuration settings
- `blast`: Execute BLAST searches and parse results
- `data_decoration`: Enrich sequence data with annotations
- `reporter`: Generate narrative reports from results
- `validation`: Validate inputs and results for quality control

Example:
```bash
story-seq run-agent reporter \
  --query sequences.fasta \
  --prompt "Summarize the top 5 BLAST hits" \
  --llm-api-url https://api.openai.com/v1 \
  --llm-model gpt-4 \
  --llm-api-key your-key
```

Options (same as blast command):
- `--query, -q`: Query FASTA file path (optional for some agents)
- `--database, -d`: Database to search against
- `--output, -o`: Output file path
- `--question`: Question to ask the LLM
- `--prompt, -p`: Custom prompt or instructions for the agent
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

Of course. Here is the Markdown content to add to the end of your `README.md` file, including the team list and a formatted citation. This is designed to be directly copied and pasted.

---

## Team

-   Andrew Warren
-   Curtis Hendrickson
-   Dustin Machi
-   Jason Williams
-   Andrew Freiburger

## Citation

If you use StorySeq in your research, please cite it as follows:

Freiburger, A., Hendrickson, C., Machi, D., Willams, J., & Warren, A. (2025). *StorySeq: Automated Sequence Narrative Generation* (Version 0.1.0) [Computer software]. GitHub. Retrieved from https://github.com/NIAID-BRC-Codeathons/storyseq-sequence-narrative

### BibTeX

For users of LaTeX and reference managers, you can use the following BibTeX entry:

```bibtex
@software{StorySeq2025,
  author = {Freiburger, Andrew and Hendrickson, Curtis and Machi, Dustin and Williams, Jason and Warren, Andrew},
  title = {{StorySeq: Automated Sequence Narrative Generation}},
  year = {2025},
  version = {0.1.0},
  publisher = {GitHub},
  url = {https://github.com/NIAID-BRC-Codeathons/storyseq-sequence-narrative}
}
```

## License

*To be determined by the team.*
