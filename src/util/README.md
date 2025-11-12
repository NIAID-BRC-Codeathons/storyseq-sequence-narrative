output examples


{
    "file_path": "nt.fasta",
    "analysis": {
        "total_records": 2,
        "average_length": 257.5,
        "file_alphabet_type": "NT"
    }
}


{
    "file_path": "mixed.fasta",
    "analysis": {
        "total_records": 4,
        "average_length": 300.5,
        "file_alphabet_type": "mixed",
        "partitions": {
            "NT": {
                "count": 2,
                "record_ids": [
                    "CY014845.1",
                    "NC_000913.3_gene_1"
                ],
                "output_file": "mixed_NT.fasta"
            },
            "AA": {
                "count": 2,
                "record_ids": [
                    "P01013.1",
                    "NP_414543.1"
                ],
                "output_file": "mixed_AA.fasta"
            }
        }
    }
}


