import re

def parse_and_filter_diff(raw_diff: str) -> list[dict]:
    """
    Splits a raw diff into individual files and filters out noise (e.g., lockfiles).
    Returns a list of dictionaries containing the filename and the chunked diff.
    """

    # Split the diff by the standard git diff header
    file_diffs = re.split(r'^diff --git ', raw_diff, flags=re.MULTILINE)

    # Files to ignore (saves AI tokens and prevents false positives)
    ignore_extensions = ('.lock', '.svg', '.png', '.jpg', '.md', '.csv')

    processed_chunks = []

    for file_diff in file_diffs:
        if not file_diff.strip():
            continue  # Skip empty chunks

        # Re-attach the 'diff --git ' that was stripped by the split
        file_diff = f"diff --git {file_diff}"

        # Extract the filename (e.g., a/backend/main.py b/backend/main.py)
        match = re.search(r'^diff --git a/(.+?) b/', file_diff, re.MULTILINE)
        if not match:
            continue  # Skip if we can't find a filename

        filename = match.group(1)

        # Skip noise files
        if filename.endswith(ignore_extensions):
            print(f"Skipping noise file: {filename}")
            continue

        processed_chunks.append({
            "filename": filename,
            "content": file_diff
        })

    return processed_chunks