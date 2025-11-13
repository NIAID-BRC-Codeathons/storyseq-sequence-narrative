#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
fasta_sketch_and_split.py

A script to analyze a FASTA file and generate a machine-readable JSON summary.
This summary is intended for an agentic pipeline to make decisions about
downstream processing (e.g., choosing blastn vs. blastp).

If the input file contains a mix of Nucleotide (NT) and Amino Acid (AA)
sequences, this script will also write two new FASTA files, one for each
alphabet type, and include the paths to these new files in the JSON output.

Usage:
    python fasta_sketch.py <path_to_fasta_file>
"""

import sys
import os
import json
from Bio import SeqIO

def guess_alphabet(sequence_str):
    """
    A simple heuristic to guess the alphabet of a sequence.
    If any character is exclusive to the protein alphabet, it's 'AA'.
    Otherwise, it's assumed to be 'NT'.
    """
    exclusive_protein_chars = set("EFILPQZ")
    for char in sequence_str.upper():
        if char in exclusive_protein_chars:
            return "AA"
    return "NT"

def analyze_fasta(file_path):
    """
    Analyzes a FASTA file and returns a dictionary of its characteristics.
    If the file is of a mixed alphabet type, it splits the file into
    separate NT and AA files.
    """
    records = []
    try:
        with open(file_path, "r") as handle:
            for record in SeqIO.parse(handle, "fasta"):
                records.append(record)
    except FileNotFoundError:
        return {"error": f"File not found: {file_path}"}
    except Exception as e:
        return {"error": f"An error occurred while parsing the file: {e}"}

    if not records:
        return {
            "file_path": file_path,
            "analysis": {
                "total_records": 0,
                "average_length": 0,
                "file_alphabet_type": "empty",
            }
        }

    total_records = len(records)
    total_length = sum(len(rec.seq) for rec in records)
    average_length = round(total_length / total_records, 2)

    # Partition records by guessed alphabet
    nt_partition = []
    aa_partition = []
    for record in records:
        alphabet = guess_alphabet(str(record.seq))
        if alphabet == "NT":
            nt_partition.append(record)
        else:
            aa_partition.append(record)

    # Determine overall file alphabet type
    is_nt = bool(nt_partition)
    is_aa = bool(aa_partition)

    if is_nt and not is_aa:
        file_alphabet_type = "NT"
    elif not is_nt and is_aa:
        file_alphabet_type = "AA"
    else:
        file_alphabet_type = "mixed"

    # Build the final JSON structure
    output = {
        "file_path": file_path,
        "analysis": {
            "total_records": total_records,
            "average_length": average_length,
            "file_alphabet_type": file_alphabet_type,
        }
    }
    
    # If mixed, perform the file split and update the JSON
    if file_alphabet_type == "mixed":
        base_name, ext = os.path.splitext(file_path)
        nt_filename = f"{base_name}_NT.fasta"
        aa_filename = f"{base_name}_AA.fasta"
        
        # Write the new FASTA files
        SeqIO.write(nt_partition, nt_filename, "fasta")
        SeqIO.write(aa_partition, aa_filename, "fasta")
        
        output["analysis"]["partitions"] = {
            "NT": {
                "count": len(nt_partition),
                "record_ids": [rec.id for rec in nt_partition],
                "output_file": nt_filename  # Inform the agent of the new file
            },
            "AA": {
                "count": len(aa_partition),
                "record_ids": [rec.id for rec in aa_partition],
                "output_file": aa_filename  # Inform the agent of the new file
            }
        }
        
    return output

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fasta_sketch.py <path_to_fasta_file>")
        sys.exit(1)

    fasta_file = sys.argv[1]
    result = analyze_fasta(fasta_file)
    
    # Print the JSON output to stdout
    print(json.dumps(result, indent=4))
