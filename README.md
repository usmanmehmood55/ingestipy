# Ingestipy

**Ingestipy** is a Python derivative of Ingestify, a command-line tool that merges an entire project’s source files into
a single text file. This can be particularly useful when feeding small-sized codebases to AI chat bots like ChatGPT.

## Table of Contents

- [Ingestipy](#ingestipy)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Basic Example](#basic-example)
    - [Verbose Mode](#verbose-mode)
  - [Ignore File](#ignore-file)
  - [Examples](#examples)

## Features

- Recursively collects files from a specified directory.
- Automatically skips:
  - The output file itself to prevent self-ingestion.
  - `.git` directories.
  - User-defined ignore patterns (glob-based) from an optional ignore file.
- Logs processing info and errors to help identify problematic files.

## Installation

You can install **ingestipy** directly from [PyPI](https://pypi.org/) using `pip`:

```bash
pip install ingestipy
```

After installation, you should have an `ingestipy` command available in your terminal.

## Usage

Run `ingestipy --help` to see the available arguments:

```bash
ingestipy --help
```

Output:
```
usage: ingestipy [-h] [-in INPUT_DIR] [-out OUTPUT_PATH] [-ignore IGNORE_FILE_PATH] [-v]

Extract code with ignore functionality.

optional arguments:
  -h, --help            show this help message and exit
  -in INPUT_DIR, --input_dir INPUT_DIR
                        Input directory path
  -out OUTPUT_PATH, --output_path OUTPUT_PATH
                        Output file path
  -ignore IGNORE_FILE_PATH, --ignore_file_path IGNORE_FILE_PATH
                        Path to ignore file
  -v, --verbose         Enable verbose logging
```

### Basic Example

```bash
ingestipy --input_dir . --output_path my_project_ingest.txt
```

### Verbose Mode

```bash
ingestipy -in . -out my_project_ingest.txt --verbose
```
This will provide extra debug output in your terminal (e.g., which files are being processed or skipped).

## Ignore File

If you have a file containing glob patterns (e.g., `ingestipy_ignore.txt`), you can specify it with `-ignore`:

```bash
ingestipy -in /path/to/project -out /path/to/output.txt -ignore /path/to/ingestipy_ignore.txt
```

Each line in the ignore file is treated as a [glob pattern](https://docs.python.org/3/library/fnmatch.html). For example:

```
*.log
*.pyc
node_modules
dist
build
```

When a file or directory matches any of these patterns, **ingestipy** skips it.

## Examples

1. **Default Behavior (No Arguments)**  
   ```bash
   ingestipy
   ```
   - Uses the script’s directory as input.
   - Creates an output file named `<current_folder>_ingestipy_output.txt`.

2. **Specifying Everything Manually**  
   ```bash
   ingestipy -in /home/user/my_project -out /home/user/output/merged.txt -ignore /home/user/my_project/my_ignore_list.txt
   ```
   - Gathers all files from `my_project` (excluding anything matching `my_ignore_list.txt`) and writes them to `merged.txt`.
