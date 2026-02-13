import os
import sys
import tempfile
import unittest
from unittest.mock import patch
import logging

from ingestipy.ingestipy import main

class TestAppIntegration(unittest.TestCase):

    def setUp(self):
        self.test_dir        = os.path.dirname(os.path.abspath(__file__))
        self.sample_project  = os.path.join(self.test_dir, "sample_project")
        self.expected_output = os.path.join(self.test_dir, "expected_output.txt")
        self.output_file     = os.path.join(self.test_dir, "test_output.txt")

        # Ensure any old output file is removed before running the test
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_sample_project_output(self):
        """Test the app against a sample project and compare output."""
        test_args = [
            "prog",
            "-in", self.sample_project,
            "-out", self.output_file,
            "-ignore", os.path.join(self.sample_project, "ignore.txt"),
        ]

        with patch.object(sys, 'argv', test_args):
            main()

        # Read both output and expected files
        with open(self.output_file, "r", encoding="utf-8") as f:
            actual_output = f.read().strip()

        with open(self.expected_output, "r", encoding="utf-8") as f:
            expected_output = f.read().strip()

        self.assertEqual(actual_output, expected_output, "Output does not match expected output!")

    def test_app_integration_with_all_args(self):
        """
        Test the app by providing all arguments (input directory, output file, and ignore file).
        Verifies that only files that are not ignored are written to the output.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create an input file that should be processed.
            file1_path = os.path.join(temp_dir, "file1.txt")
            with open(file1_path, "w", encoding="utf-8") as f:
                f.write("Hello, World!")

            # Create an ignored directory and file inside it.
            ignore_dir = os.path.join(temp_dir, "ignore")
            os.mkdir(ignore_dir)
            file2_path = os.path.join(ignore_dir, "file2.txt")
            with open(file2_path, "w", encoding="utf-8") as f:
                f.write("This should be ignored.")

            # Create a .git directory and file (should be automatically ignored).
            git_dir = os.path.join(temp_dir, ".git")
            os.mkdir(git_dir)
            git_file_path = os.path.join(git_dir, "config")
            with open(git_file_path, "w", encoding="utf-8") as f:
                f.write("Git config data")

            # Specify an output file path (will be overwritten by the app).
            output_file_path = os.path.join(temp_dir, "output.txt")

            # Create an ignore file that instructs to ignore the "ignore" directory.
            ignore_file_path = os.path.join(temp_dir, "ignore.txt")
            with open(ignore_file_path, "w", encoding="utf-8") as f:
                f.write("ignore/*\n")

            test_args = [
                "prog",
                "-in", temp_dir,
                "-out", output_file_path,
                "-ignore", ignore_file_path,
                "-v"
            ]

            with patch.object(sys, 'argv', test_args):
                main()

            # Read the output file and verify its contents.
            with open(output_file_path, "r", encoding="utf-8") as f:
                output = f.read()

            # Check that file1.txt's content is present.
            self.assertIn("Hello, World!", output)
            # Verify that files in the ignored directory are not present.
            self.assertNotIn("This should be ignored.", output)
            # Verify that files inside .git are not included.
            self.assertNotIn("Git config data", output)
            # Confirm that the file header for file1.txt is included.
            self.assertIn("// file: file1.txt:", output)

    def test_app_integration_default_args(self):
        """
        Test the app when no command-line arguments are provided.
        The app should use the current working directory as input and create a default output file.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change the current working directory to our temp_dir.
            old_cwd = os.getcwd()
            os.chdir(temp_dir)
            try:
                # Create an input file.
                file1_path = os.path.join(temp_dir, "file1.txt")
                with open(file1_path, "w", encoding="utf-8") as f:
                    f.write("Default input test")

                # Do not create an ignore file so that defaults are exercised.

                test_args = ["prog"]
                with patch.object(sys, 'argv', test_args):
                    main()

                # Determine the default output file name.
                folder_name = os.path.basename(os.path.normpath(temp_dir))
                default_output = os.path.join(temp_dir, f"{folder_name}_ingestipy_output.txt")
                with open(default_output, "r", encoding="utf-8") as f:
                    output = f.read()

                self.assertIn("Default input test", output)
            finally:
                os.chdir(old_cwd)

    def test_app_exception_handling(self):
        """
        Test that the app properly handles exceptions during file writing.
        By setting the output path to a directory, opening it as a file should fail,
        and the app should exit with a status code of 1.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create an input file.
            file1_path = os.path.join(temp_dir, "file1.txt")
            with open(file1_path, "w", encoding="utf-8") as f:
                f.write("Content that triggers exception")

            # Use a directory path as the output file path to force an exception.
            output_file_path = os.path.join(temp_dir, "output_dir")
            os.mkdir(output_file_path)

            test_args = [
                "prog",
                "-in", temp_dir,
                "-out", output_file_path,
                "-v"
            ]

            with patch.object(sys, 'argv', test_args):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()
