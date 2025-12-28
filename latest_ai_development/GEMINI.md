# Project Context: LatestAiDevelopment (CrewAI)

## Project Overview

**LatestAiDevelopment** is a Python-based AI automation project built using the [crewAI](https://crewai.com) framework. It is designed to deploy a crew of AI agents to perform complex tasks.

Currently, the project is configured as an **E-commerce Scraper**. It features a specialized agent capable of scraping product information (names, prices, descriptions, images, ratings) from e-commerce websites and saving the data in a structured JSON format.

### Key Components

*   **Framework:** `crewAI` (v1.7.2)
*   **Dependency Manager:** `uv`
*   **Main Logic:** `src/latest_ai_development/crew.py` (Crew definition)
*   **Entry Points:** `src/latest_ai_development/main.py` (CLI commands)
*   **Configuration:**
    *   `src/latest_ai_development/config/agents.yaml`: Agent definitions (roles, goals, backstories).
    *   `src/latest_ai_development/config/tasks.yaml`: Task definitions (descriptions, expected outputs).
*   **Custom Tools:** `src/latest_ai_development/tools/custom_tool.py` (Contains `EcommerceScraper`).

## Architecture

The project follows the standard crewAI structure:

1.  **Crew Definition (`crew.py`):** Decorators (`@crew`, `@agent`, `@task`) are used to assemble the crew. It binds the YAML configurations to the Python class methods.
2.  **Agents:** Defined in `agents.yaml` and instantiated in `crew.py`. The current agent is `ecommerce_scraper`.
3.  **Tasks:** Defined in `tasks.yaml` and instantiated in `crew.py`. The current task is `scraping_task`, which outputs to `outputs/scraped_products.json`.
4.  **Tools:** The `ecommerce_scraper` agent is equipped with the `EcommerceScraper` tool, which uses `requests` and `BeautifulSoup` to parse HTML.

## Setup and Usage

### Prerequisites
*   Python >=3.10, <3.14
*   `uv` (Universal Python Packaging)

### Installation
```bash
pip install uv
crewai install
```

### Running the Crew
To execute the default scraping task (currently targeting `https://cellphones.com.vn/laptop.html`):

```bash
crewai run
```

This command invokes the `run()` function in `src/latest_ai_development/main.py`.

### Other Commands
*   **Train:** `crewai train <n_iterations> <filename>` (Train agents on specific data)
*   **Replay:** `crewai replay <task_id>` (Replay a specific task)
*   **Test:** `crewai test <n_iterations> <model>` (Test agent performance)

## Development Conventions

*   **Configuration First:** Modify behavior primarily through `config/agents.yaml` and `config/tasks.yaml` before touching Python code.
*   **Custom Logic:** Add new tools in `src/latest_ai_development/tools/` and register them in `crew.py`.
*   **Environment Variables:** Store sensitive keys (like `OPENAI_API_KEY`) in `.env`.
*   **Outputs:** Artifacts are generated in the `outputs/` directory.

## Important Files

*   `pyproject.toml`: Project metadata and dependencies.
*   `src/latest_ai_development/main.py`: The entry point script. **Note:** The target URL is currently hardcoded here in the `inputs` dictionary.
*   `src/latest_ai_development/tools/custom_tool.py`: The scraping logic. It has a default CSS selector strategy but attempts fallback heuristics if specific selectors fail.
