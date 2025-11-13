output examples

simple
{
    "run_summary": {
        "total_input_files": 1,
        "input_files_list": [
            "../../test_data/gene/nuc/streptococcus_pneumoniae.PBP1a.fna"
        ],
        "errors": []
    },
    "partitions": {
        "NT": {
            "total_records": 1,
            "total_length": 2160,
            "files": [
                {
                    "source_file": "../../test_data/gene/nuc/streptococcus_pneumoniae.PBP1a.fna",
                    "record_count": 1,
                    "total_length": 2160
                }
            ],
            "average_length": 2160.0
        },
        "AA": {
            "total_records": 0,
            "total_length": 0,
            "files": [],
            "average_length": 0
        }
    }
}

complex
{
    "run_summary": {
        "total_input_files": 3,
        "input_files_list": [
            "genes.fasta",
            "proteins.fasta",
            "combined.fasta"
        ],
        "errors": []
    },
    "partitions": {
        "NT": {
            "total_records": 150,
            "total_length": 155000,
            "files": [
                {
                    "source_file": "genes.fasta",
                    "record_count": 100,
                    "total_length": 105000
                },
                {
                    "source_file": "combined_NT.fasta",
                    "original_source": "combined.fasta",
                    "record_count": 50,
                    "total_length": 50000
                }
            ],
            "average_length": 1033.33
        },
        "AA": {
            "total_records": 125,
            "total_length": 42500,
            "files": [
                {
                    "source_file": "proteins.fasta",
                    "record_count": 100,
                    "total_length": 35000
                },
                {
                    "source_file": "combined_AA.fasta",
                    "original_source": "combined.fasta",
                    "record_count": 25,
                    "total_length": 7500
                }
            ],
            "average_length": 340.0
        }
    }
}

