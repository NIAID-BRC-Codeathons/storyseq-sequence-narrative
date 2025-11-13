#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
fasta_sketch.py

A script to analyze one or more FASTA files and generate a single, 
machine-readable JSON "sketch" for the entire batch.

The script categorizes all input sequences into either a Nucleotide (NT) or
an Amino Acid (AA) partition. It calculates aggregated statistics for each partition
(total records, total length, average length) and also provides per-file stats.
If an input file contains a mix of sequence types, it is automatically split into
separate NT and AA files, which are then categorized accordingly.

The final JSON output provides an agent with two clean, statistically-described
batches of files to process with appropriate downstream tools.

Usage:
    python fasta_sketch.py <file1.fasta> [file2.fasta ...]
"""

import sys
import os
import json
from Bio import SeqIO

def guess_alphabet(sequence_str):
    """
    A simple heuristic to guess the alphabet of a sequence.
    """
    exclusive_protein_chars = set("EFILPQZ")
    for char in sequence_str.upper():
        if char in exclusive_protein_chars:
            return "AA"
    return "NT"

def longest_orf_length(seq: str) -> int:
    """
    Return the length (in nt) of the longest ORF across all 6 reading frames.
    ORF = region between in-frame stop codons (TAA/TAG/TGA); start codon not required.
    """
    seq = seq.upper().replace("\n", "").replace(" ", "")
    stops = {"TAA", "TAG", "TGA"}

    def revcomp(s: str) -> str:
        comp = str.maketrans("ACGTN", "TGCAN")
        return s.translate(comp)[::-1]

    def max_orf_in_frame(s: str, frame: int) -> int:
        max_len = 0
        current_len = 0
        # walk codon by codon starting at given frame
        for i in range(frame, len(s) - 2, 3):
            codon = s[i:i+3]
            if codon in stops:
                # stop codon ends current ORF
                if current_len > max_len:
                    max_len = current_len
                current_len = 0
            else:
                current_len += 3
        # tail ORF without trailing stop
        if current_len > max_len:
            max_len = current_len
        return max_len

    seq_rc = revcomp(seq)

    best = 0
    for frame in range(3):
        best = max(best, max_orf_in_frame(seq, frame))
        best = max(best, max_orf_in_frame(seq_rc, frame))

    return best

def analyze_single_fasta(file_path):
    """
    Analyzes a single FASTA file, splits it if mixed, and returns a 
    structured dictionary of its raw characteristics (counts and lengths).
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
            "analysis": { "total_records": 0, "total_length": 0, "file_alphabet_type": "empty" }
        }

    total_records = len(records)
    total_length = sum(len(rec.seq) for rec in records)
    
    nt_has_orfs = False;
    nt_partition = []
    aa_partition = []
    for record in records:
        if guess_alphabet(str(record.seq)) == "NT":
            nt_partition.append(record)
            max_orf_length = longest_orf_length(str(record.seq))
            if max_orf_length > len(str(record.seq))/2 or max_orf_length >= 300:
                nt_has_orfs = True  
        else:
            aa_partition.append(record)

    is_nt = bool(nt_partition)
    is_aa = bool(aa_partition)
    has_orfs = True
    if is_nt and not is_aa:
        file_alphabet_type = "NT"
        has_orfs = nt_has_orfs
    elif not is_nt and is_aa:
        file_alphabet_type = "AA"
    else:
        file_alphabet_type = "mixed"

    output = {
        "file_path": file_path,
        "analysis": {
            "total_records": total_records,
            "total_length": total_length,
            "file_alphabet_type": file_alphabet_type,
            "has_orfs": has_orfs
        }
    }
    
    if file_alphabet_type == "mixed":
        base_name, _ = os.path.splitext(file_path)
        nt_filename = f"{base_name}_NT.fasta"
        aa_filename = f"{base_name}_AA.fasta"
        
        SeqIO.write(nt_partition, nt_filename, "fasta")
        SeqIO.write(aa_partition, aa_filename, "fasta")
        
        nt_total_length = sum(len(rec.seq) for rec in nt_partition)
        aa_total_length = sum(len(rec.seq) for rec in aa_partition)
        
        output["analysis"]["partitions"] = {
            "NT": {"count": len(nt_partition), "total_length": nt_total_length, "output_file": nt_filename, "has_orfs": nt_has_orfs},
            "AA": {"count": len(aa_partition), "total_length": aa_total_length, "output_file": aa_filename, "has_orfs": True}
        }
        
    return output

def process_multiple_files(file_paths):
    """
    Orchestrates the analysis of multiple FASTA files and aggregates the
    results into a single JSON object with NT and AA partitions.
    """
    nt_agg = {"total_records": 0, "total_length": 0, "has_orfs":False, "files": []}
    aa_agg = {"total_records": 0, "total_length": 0, "has_orfs":False, "files": []}
    errors = []

    for path in file_paths:
        result = analyze_single_fasta(path)
        
        if "error" in result:
            errors.append(result)
            continue
        
        analysis = result["analysis"]
        alphabet_type = analysis["file_alphabet_type"]
        
        if alphabet_type == "NT":
            nt_agg["total_records"] += analysis["total_records"]
            nt_agg["total_length"] += analysis["total_length"]
            nt_agg["has_orfs"] = analysis["has_orfs"]
            nt_agg["files"].append({
                "source_file": result["file_path"],
                "record_count": analysis["total_records"],
                "total_length": analysis["total_length"]
            })

        elif alphabet_type == "AA":
            aa_agg["total_records"] += analysis["total_records"]
            aa_agg["total_length"] += analysis["total_length"]
            aa_agg["has_orfs"] = analysis["has_orfs"]
            aa_agg["files"].append({
                "source_file": result["file_path"],
                "record_count": analysis["total_records"],
                "total_length": analysis["total_length"]
            })
            
        elif alphabet_type == "mixed":
            nt_info = analysis["partitions"]["NT"]
            aa_info = analysis["partitions"]["AA"]
            
            nt_agg["total_records"] += nt_info["count"]
            nt_agg["total_length"] += nt_info["total_length"]
            nt_agg["has_orfs"] += nt_info["has_orfs"]
            nt_agg["files"].append({
                "source_file": nt_info["output_file"],
                "original_source": result["file_path"],
                "record_count": nt_info["count"],
                "total_length": nt_info["total_length"]
            })
            
            aa_agg["total_records"] += aa_info["count"]
            aa_agg["total_length"] += aa_info["total_length"]
            aa_agg["has_orfs"] = aa_info["has_orfs"]
            aa_agg["files"].append({
                "source_file": aa_info["output_file"],
                "original_source": result["file_path"],
                "record_count": aa_info["count"],
                "total_length": aa_info["total_length"]
            })
    
    if nt_agg["total_records"] > 0:
        nt_agg["average_length"] = round(nt_agg["total_length"] / nt_agg["total_records"], 2)
    else:
        nt_agg["average_length"] = 0
        
    if aa_agg["total_records"] > 0:
        aa_agg["average_length"] = round(aa_agg["total_length"] / aa_agg["total_records"], 2)
    else:
        aa_agg["average_length"] = 0

    final_dispatch_plan = {
        "run_summary": {
            "total_input_files": len(file_paths),
            "input_files_list": file_paths,
            "errors": errors
        },
        "partitions": {
            "NT": nt_agg,
            "AA": aa_agg
        }
    }

    return final_dispatch_plan

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fasta_sketch.py <file1.fasta> [file2.fasta ...]")
        sys.exit(1)

    input_files = sys.argv[1:]
    dispatch_plan = process_multiple_files(input_files)
    
    print(json.dumps(dispatch_plan, indent=4))
