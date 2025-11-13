"""
Utility modules for story-seq.

This file defines the public API for the utils package, making key
functions and data models directly importable.
"""

# Import the main function from the fasta_sketch module
from .fasta_sketch import process_multiple_files

__all__ = [
    # Functions
    "process_multiple_files"
]
