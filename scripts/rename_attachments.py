#!/usr/bin/env python3

"""
Rename attachment files to sequential numbers and update dataset references.

The script walks `data/original/raw_gaia_dataset.jsonl` in order, assigns each
referenced attachment a numeric name (`1.ext`, `2.ext`, …), renames the files in
`data/original/attachements`, and rewrites the corresponding `file_name` fields.
Attachments that never appear in the dataset are still renamed with the next
available number. A CSV mapping of old → new names is written alongside the
dataset for traceability.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    attachments_dir = repo_root / "data" / "original" / "attachements"
    dataset_path = repo_root / "data" / "original" / "raw_gaia_dataset.jsonl"

    if not attachments_dir.is_dir():
        raise SystemExit(f"Attachment directory not found: {attachments_dir}")
    if not dataset_path.is_file():
        raise SystemExit(f"Dataset file not found: {dataset_path}")

    attachment_files = sorted(
        [path.name for path in attachments_dir.iterdir() if path.is_file()]
    )
    if not attachment_files:
        raise SystemExit(f"No files found in {attachments_dir}")

    mapping: dict[str, str] = {}
    dataset_records: list[dict[str, object]] = []
    counter = 1

    # Assign names in the order attachments appear within the dataset.
    with dataset_path.open("r", encoding="utf-8") as dataset_file:
        for line_number, raw_line in enumerate(dataset_file, start=1):
            stripped = raw_line.rstrip("\n")
            if not stripped:
                dataset_records.append({})
                continue

            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise SystemExit(
                    f"Failed to parse JSON on line {line_number}: {exc}"
                ) from exc

            file_name = record.get("file_name")
            if file_name:
                stem = Path(file_name).stem
                if stem.isdigit():
                    mapping.setdefault(file_name, file_name)
                else:
                    if file_name not in mapping:
                        suffix = Path(file_name).suffix
                        new_name = f"{counter}{suffix}"
                        mapping[file_name] = new_name
                        counter += 1

            dataset_records.append(record)

    # Ensure any remaining attachment gets a numeric name.
    for file_name in attachment_files:
        if file_name in mapping:
            continue

        stem = Path(file_name).stem
        if stem.isdigit():
            mapping[file_name] = file_name
        else:
            suffix = Path(file_name).suffix
            new_name = f"{counter}{suffix}"
            mapping[file_name] = new_name
            counter += 1

    new_names = set(mapping.values())
    if len(new_names) != len(mapping):
        raise SystemExit("Generated duplicate filenames; aborting.")

    # Rename the attachment files.
    renamed_count = 0
    for old_name, new_name in mapping.items():
        old_path = attachments_dir / old_name
        new_path = attachments_dir / new_name
        if old_path == new_path:
            continue
        if new_path.exists():
            raise SystemExit(f"Target file already exists: {new_path}")
        old_path.rename(new_path)
        renamed_count += 1

    # Update the dataset with the new attachment names.
    updated_lines: list[str] = []
    for record in dataset_records:
        if not record:
            updated_lines.append("")
            continue

        file_name = record.get("file_name")
        if file_name:
            try:
                record["file_name"] = mapping[file_name]
            except KeyError as exc:
                raise SystemExit(
                    f"Attachment referenced in dataset not found after renaming: "
                    f"{file_name}"
                ) from exc

        updated_lines.append(json.dumps(record, ensure_ascii=False))

    with dataset_path.open("w", encoding="utf-8") as dataset_file:
        dataset_file.write("\n".join(updated_lines))
        dataset_file.write("\n")

    # Write the mapping CSV for reference.
    mapping_path = repo_root / "data" / "original" / "attachment_mapping.csv"
    ordered_mapping = sorted(
        mapping.items(), key=lambda item: int(Path(item[1]).stem)
    )
    with mapping_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["original_name", "renamed_to"])
        writer.writerows(ordered_mapping)

    print(
        f"Renamed {renamed_count} attachments and updated dataset references in "
        f"{dataset_path}"
    )


if __name__ == "__main__":
    main()
