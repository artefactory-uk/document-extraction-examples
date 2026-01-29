# document-extraction-examples

Practical, end-to-end examples that implement the interfaces and orchestrators from the
`document-extraction-tools` [repository](https://github.com/artefactory-uk/document-extraction-tools). 

This repository is for data scientists/engineers who want to
see real, working pipelines and use them as a starting point for their own document
extraction systems.

## Table of Contents

- [document-extraction-examples](#document-extraction-examples)
  - [What this repo is](#what-this-repo-is)
  - [How it uses document-extraction-tools](#how-it-uses-document-extraction-tools)
  - [Project layout](#project-layout)
  - [Examples](#examples)
    - [Simple lease extraction](#simple-lease-extraction)
  - [Install](#install)
  - [Configure](#configure)
  - [Run](#run)
    - [Extraction](#extraction)
    - [Evaluation](#evaluation)
    - [MLflow server](#mlflow-server)
  - [How to build on this](#how-to-build-on-this)
  - [Development](#development)

## What this repo is

- A set of concrete implementations for the interfaces defined in
  `document-extraction-tools`.
- A reference for how to wire components with the provided orchestrators.
- Runnable baseline for extraction + evaluation workflows.

## How it uses document-extraction-tools

The `document-extraction-tools` library is intentionally implementation-light. It
defines the interfaces and orchestration logic, and you implement the pieces.

This repo provides those pieces:

- **Interfaces implemented here**
  - `BaseFileLister`
  - `BaseReader`
  - `BaseConverter`
  - `BaseExtractor`
  - `BaseExtractionExporter`
  - `BaseTestDataLoader`
  - `BaseEvaluator`
  - `BaseEvaluationExporter`
- **Orchestrators used from the library**
  - `ExtractionOrchestrator`
  - `EvaluationOrchestrator`
- **Config system used from the library**
  - `load_config` / `load_evaluation_config`
  - Base config classes (subclassed in this repo)

The orchestrators handle concurrency (thread pool for CPU-bound steps and async
concurrency for I/O-bound steps); this repo focuses on the actual logic for each
pipeline stage.

## Project layout

```bash
.
├── src
│   └── document_extraction_examples
│       └── simple_lease_extraction
│           ├── components               # Implementations of the base interfaces
│           ├── config                   # Pydantic config classes + YAML
│           ├── data                     # Example inputs/outputs/eval data
│           ├── prompts                  # Prompt references (see MLflow prompt usage)
│           ├── schemas                  # Extraction schema (Pydantic)
│           ├── utils                    # MLflow + LLM-as-a-judge utilities
│           ├── extraction_main.py       # Extraction entrypoint
│           └── evaluation_main.py       # Evaluation entrypoint
├── tests
├── Makefile
├── docker-compose.yaml                  # MLflow server
├── pyproject.toml
└── README.md
```

## Examples

### Simple lease extraction

Location: `src/document_extraction_examples/simple_lease_extraction`

This example extracts structured lease details from PDFs using Gemini with image
inputs, and evaluates results against a small labeled dataset.

The example is instrumented with MLflow: traces and evaluation metrics are logged
so you can inspect runs and results in the MLflow UI.

**Schema**

`SimpleLeaseDetails` is a Pydantic model that defines the target output fields:

- landlord/tenant names and addresses
- property address + postcode
- lease start/end dates
- rent and deposit amounts

**Extraction pipeline components**

- **File lister**: `LocalFileLister`  
  Lists PDFs under `data/input`.
- **Reader**: `LocalFileReader`  
  Reads PDF bytes from disk.
- **Converter**: `PDFToImageConverter`  
  Uses `pdf2image` to convert each PDF into image pages.
- **Extractor**: `GeminiImageExtractor`  
  Calls the Gemini API with the prompt + image pages and parses a structured
  response against the schema.
- **Exporter**: `LocalFileExtractionExporter`  
  Writes JSON results to `data/output`.

**Evaluation pipeline components**

- **Test data loader**: `LocalJSONTestDataLoader`  
  Loads labeled examples from `data/evaluation/test_data.json`.
- **Evaluators**: `AccuracyEvaluator`, `F1Evaluator`  
  Field-level accuracy and F1; can optionally use an LLM-as-a-judge for fuzzy
  equality.
- **Exporter**: `LocalFileEvaluationExporter`  
  Writes per-metric JSON files and logs average metrics to MLflow.

**Config files**

Configuration lives under:

```
src/document_extraction_examples/simple_lease_extraction/config/yaml
```

Each file maps to a component’s config model in `config/` and is loaded by
`load_config` / `load_evaluation_config`.

## Install

This project uses `uv` and a pinned Python version (see `pyproject.toml`).

First-time setup checklist:

- Ensure Homebrew is installed (macOS):
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
- Ensure `make` is installed.
  - macOS: `brew install make`
- To run the MLflow server, install Docker:
  - macOS: `brew install docker docker-buildx colima`
  - Link Docker BuildX plugin:
    ```bash
    mkdir -p ~/.docker/cli-plugins  
    ln -sfn $(brew --prefix)/opt/docker-buildx/bin/docker-buildx ~/.docker/cli-plugins/docker-buildx
    ```

Then install dependencies:

```bash
make install
```

Notes:

- `document-extraction-tools` is installed from Git over SSH, so you’ll need
  GitHub access via SSH.
- `pdf2image` typically requires Poppler installed on your system.
  - macOS: `brew install poppler`

## Configure

Create a `.env` file (or export variables) for API keys and MLflow:

```bash
cp .env.example .env
```

Required:

- `GEMINI_API_KEY` for the extractor and optional LLM-as-a-judge.

For MLflow server via Docker Compose:

- `PG_USER`
- `PG_PASSWORD`

The default example configuration is under:

`src/document_extraction_examples/simple_lease_extraction/config/yaml`

Key settings to pay attention to:

- `extractor.yaml`  
  `mlflow_prompt_name` + `mlflow_prompt_version` must exist in your MLflow
  prompt registry.
- `file_lister.yaml`  
  Input directory and file extensions.
- `test_data_loader.yaml`  
  Evaluation dataset location.
- `extraction_exporter.yaml` / `evaluation_exporter.yaml`  
  Output directories for results.
- `evaluator.yaml`  
  Enables LLM-as-a-judge comparisons if desired.

## Run

### Extraction

```bash
make run
```

Outputs are written to:

`src/document_extraction_examples/simple_lease_extraction/data/output`

### Evaluation

```bash
make evaluate
```

Outputs are written to:

`src/document_extraction_examples/simple_lease_extraction/data/evaluation`

### MLflow server

This example is instrumented with MLflow tracing. You can run a local MLflow
server via Docker Compose:

```bash
make start-mlflow
```

The extraction/evaluation entrypoints default to:

- Tracking URI: `http://localhost:8080`
- Experiments: `simple_lease_extraction` / `simple_lease_evaluation`

## How to build on this

If you want to create your own pipeline:

1. **Define a schema**  
   Add a Pydantic model under `schemas/`.
2. **Implement components**  
   Subclass the base interfaces from `document-extraction-tools`.
3. **Add config models + YAML**  
   Create config classes in `config/` and YAML in `config/yaml/`.
4. **Wire an entrypoint**  
   Follow the pattern in `extraction_main.py` / `evaluation_main.py`.
5. **Update the Makefile (optional)**  
   Point `APP_ENTRYPOINT` / `EVAL_ENTRYPOINT` to your new module.

You can also extend the example:

- Swap the extractor to another model/provider.
- Add post-processing or validation inside the extractor or exporter.
- Add more evaluators or a different evaluation dataset.

## Development

```bash
make lint
make test
```

These run `pre-commit` and `pytest` using the locked `uv` environment.
