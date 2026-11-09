


def validate_fastq(file_path):
    """Validate basic FASTQ structure and DNA sequence."""

    valid_bases = set("ATGCN")

    with open(file_path, "r") as file:

        line_number = 0
        record_count = 0

        while True:

            identifier = file.readline()

            if not identifier:
                break

            sequence = file.readline()
            separator = file.readline()
            quality = file.readline()

            line_number += 4

            if not sequence or not separator or not quality:
                return {
                    "valid": False,
                    "message": "Incomplete FASTQ record."
                }

            identifier = identifier.strip()
            sequence = sequence.strip()
            separator = separator.strip()
            quality = quality.strip()

            if not identifier.startswith("@"):
                return {
                    "valid": False,
                    "message": f"Invalid read identifier at line {line_number - 3}."
                }

            if not sequence:
                return {
                    "valid": False,
                    "message": "Empty DNA sequence."
                }

            if not set(sequence.upper()).issubset(valid_bases):
                return {
                    "valid": False,
                    "message": "Invalid DNA sequence characters."
                }

            if not separator.startswith("+"):
                return {
                    "valid": False,
                    "message": "Invalid FASTQ separator."
                }

            if len(sequence) != len(quality):
                return {
                    "valid": False,
                    "message": "Sequence and quality lengths do not match."
                }

            record_count += 1

    if record_count == 0:
        return {
            "valid": False,
            "message": "FASTQ file contains no records."
        }

    return {
        "valid": True,
        "message": "FASTQ validation successful.",
        "records": record_count
    }
