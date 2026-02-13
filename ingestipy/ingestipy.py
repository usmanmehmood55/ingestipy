import os
import sys
import logging
import argparse
import fnmatch
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='Extract code with ignore functionality.')
    parser.add_argument('-in',     '--input_dir',        help='Input directory path'                       )
    parser.add_argument('-out',    '--output_path',      help='Output file path'                           )
    parser.add_argument('-ignore', '--ignore_file_path', help='Path to ignore file'                        )
    parser.add_argument('-v',      '--verbose',          help='Enable verbose logging', action='store_true')
    return parser.parse_args()

def should_ignore(path: str, ignore_patterns: list, output_file_path: str, root_path: str) -> bool:
    """
    Determine if a given path should be ignored.

    Args:
        path (str): The file or directory path to check.
        ignore_patterns (list): A list of glob patterns to ignore.
        output_file_path (str): The absolute path to the output file.
        root_path (str): The root directory path.

    Returns:
        bool: True if the path should be ignored, False otherwise.
    """
    # Always ignore the output file
    if os.path.abspath(path) == os.path.abspath(output_file_path):
        return True
    # Always ignore .git directories
    relative_path = os.path.relpath(path, root_path)
    if '.git' in relative_path.split(os.sep):
        return True
    # Check ignore patterns
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(relative_path, pattern):
            return True
    return False

def write_files_recursively(root_path: str, output_file, ignore_patterns: list, output_file_path: str) -> None:
    """
    Recursively write files from the root_path to the output_file, respecting ignore patterns.

    Args:
        root_path (str): The root directory to start traversal.
        output_file (file object): The output file object to write to.
        ignore_patterns (list): A list of glob patterns to ignore.
        output_file_path (str): The path to the output file.
    """
    for root, dirs, files in os.walk(root_path):
        # Filter directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_patterns, output_file_path, root_path)]
        for file in files:
            file_path = os.path.join(root, file)
            if should_ignore(file_path, ignore_patterns, output_file_path, root_path):
                continue
            relative_path = os.path.relpath(file_path, root_path)
            output_file.write(f"// file: {relative_path}:\n")
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    output_file.write(f.read())
            except UnicodeDecodeError as e:
                logging.error(f"Error reading file '{file}': {e}")
            output_file.write('\n\n')

def main():
    args = parse_args()
    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logging_level)

    # Get script directory
    input_dir = os.getcwd()

    # Set default input_dir
    if args.input_dir:
        input_dir = args.input_dir
    else:
        logging.info(f"No input directory provided. Using script directory: {input_dir}")

    # Set default output_path
    if args.output_path:
        output_path = args.output_path
    else:
        folder_name = os.path.basename(os.path.normpath(input_dir))
        output_filename = f"{folder_name}_ingestipy_output.txt"
        output_path = os.path.join(input_dir, output_filename)
        logging.info(f"No output path provided. Using default: {output_path}")

    # Set default ignore_file_path
    default_ignore_path = os.path.join(input_dir, 'ingestipy_ignore.txt')
    if args.ignore_file_path:
        ignore_file_path = args.ignore_file_path
    elif os.path.isfile(default_ignore_path):
        ignore_file_path = default_ignore_path
        logging.info(f"Using ignore file from: {ignore_file_path}")
    else:
        ignore_file_path = None
        logging.warning("Ignore file was not given, and the default \"ingestipy_ignore.txt\" was also not found.")

    # Load ignore patterns
    ignore_patterns = []
    if ignore_file_path and os.path.isfile(ignore_file_path):
        with open(ignore_file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                ignore_patterns.append(line)
    else:
        logging.info("No ignore patterns loaded.")

    try:
        with open(output_path, 'w', encoding='utf-8', errors='replace') as output_file:
            write_files_recursively(input_dir, output_file, ignore_patterns, output_path)
        logging.info(f"Files written to {os.path.abspath(output_path)}")

    except Exception as ex:
        logging.critical(f"Exception thrown: {ex}")
        sys.exit(1)

if __name__ == "__main__":
    main()
