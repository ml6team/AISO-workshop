#!/usr/bin/env python3
"""Split GAIA metadata.jsonl into balanced validation and test sets.

The split keeps the JSONL structure, while balancing label distributions
across multiple dimensions that proxy for task difficulty and modality.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

# Filtering parameters
ALLOWED_FILE_EXTENSIONS = {".docx", ".pptx", ".jpg", ".jpeg", ".png", ".mp3"}
MAX_TIME_MINUTES = 10  # Exclude tasks that took 10 minutes or more
ALLOWED_TOOLS = {
    "web search",
    "calculator",
    "image",
    "pdf",
    "video",
    "python",
    "youtube",
}
MAX_TOOLS = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create balanced validation/test splits from GAIA metadata.jsonl. "
            "Outputs JSON files with filtered and sorted data."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("metadata.jsonl"),
        help="Path to the source JSONL file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory where split files will be written.",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.5,
        help="Portion of examples assigned to validation (default: 0.5).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=211,
        help="Random seed for deterministic splits.",
    )

    return parser.parse_args()


def parse_first_int(text: str) -> int | None:
    """Extract the first integer appearing in the provided text."""
    matches = re.findall(r"\d+", text or "")
    return int(matches[0]) if matches else None


def extract_time_minutes(time_text: str) -> int | None:
    """Extract time in minutes from various time formats."""
    if not time_text:
        return None

    time_text = time_text.lower().strip()

    # Look for patterns like "5 minutes", "10 min", "2 hours", etc.
    # First check for minutes
    min_match = re.search(r"(\d+)\s*(?:minutes?|mins?|m)\b", time_text)
    if min_match:
        return int(min_match.group(1))

    # Check for hours (convert to minutes)
    hour_match = re.search(r"(\d+)\s*(?:hours?|hrs?|h)\b", time_text)
    if hour_match:
        return int(hour_match.group(1)) * 60

    # Check for combined format like "1h 30m" or "1 hour 30 minutes"
    combined_match = re.search(
        r"(\d+)\s*(?:hours?|hrs?|h).*?(\d+)\s*(?:minutes?|mins?|m)", time_text
    )
    if combined_match:
        hours = int(combined_match.group(1))
        minutes = int(combined_match.group(2))
        return hours * 60 + minutes

    # If just a number without unit, assume minutes
    number_match = re.search(r"^(\d+)$", time_text)
    if number_match:
        return int(number_match.group(1))

    return None


def is_allowed_file_extension(file_name: str) -> bool:
    """Check if file has an allowed extension."""
    if not file_name:
        return True  # Allow records with no file
    ext = Path(file_name).suffix.lower()
    return ext in ALLOWED_FILE_EXTENSIONS


def has_allowed_tools(tools_text: str, num_tools: int | None) -> bool:
    """Check if tools are within allowed set and count limit."""
    # Check tool count limit
    if num_tools is not None and num_tools > MAX_TOOLS:
        return False

    if not tools_text:
        return True  # Allow records with no tools specified

    tools_text = tools_text.lower()

    # Check if any mentioned tools are in the allowed set
    mentioned_tools = set()
    for tool in ALLOWED_TOOLS:
        if tool in tools_text:
            mentioned_tools.add(tool)

    # If specific tools are mentioned, they must be in our allowed set
    # This is a simplified check - in practice you might need more sophisticated parsing
    return (
        len(mentioned_tools) > 0
        or "none" in tools_text
        or not tools_text.strip()
    )


def get_rejection_reason(record: Dict) -> str | None:
    """Return the rejection reason for a record, or None if kept."""
    annot_meta = record.get("Annotator Metadata", {})

    # Check file extension
    file_name = record.get("file_name", "")
    if not is_allowed_file_extension(file_name):
        return "disallowed_file_extension"

    # Check time limit
    time_text = str(annot_meta.get("How long did this take?", "")).strip()
    time_minutes = extract_time_minutes(time_text)
    if time_minutes is not None and time_minutes >= MAX_TIME_MINUTES:
        return "time_too_long"

    # Check tools
    tools_text = str(annot_meta.get("Tools", "")).strip()
    num_tools = parse_first_int(
        str(annot_meta.get("Number of tools", "")).strip()
    )
    if not has_allowed_tools(tools_text, num_tools):
        return "tools_violation"

    return None


def should_keep_record(record: Dict) -> bool:
    """Filter records based on global filtering parameters."""
    return get_rejection_reason(record) is None


def sort_records_by_complexity(records: List[Dict]) -> List[Dict]:
    """Sort records by level (1-3) first, then by time duration."""

    def get_sort_key(record: Dict) -> Tuple[int, float]:
        # Primary sort: Level (1, 2, 3)
        level = record.get(
            "Level", 999
        )  # Use 999 for missing levels to put them last

        # Secondary sort: Time duration in minutes
        annot_meta = record.get("Annotator Metadata", {})
        time_text = str(annot_meta.get("How long did this take?", "")).strip()
        time_minutes = extract_time_minutes(time_text)
        if time_minutes is None:
            time_minutes = 999.0  # Put records with no time info at the end

        return (level, time_minutes)

    return sorted(records, key=get_sort_key)


def step_bucket(steps: int | None) -> str:
    if steps is None:
        return "unknown"
    if steps <= 4:
        return "short"
    if steps <= 8:
        return "medium"
    return "long"


def tool_bucket(tools: int | None) -> str:
    if tools is None:
        return "unknown"
    if tools == 0:
        return "0"
    if tools == 1:
        return "1"
    if tools == 2:
        return "2"
    if tools <= 4:
        return "3-4"
    return "5+"


def file_type_group(file_name: str) -> str:
    if not file_name:
        return "none"
    ext = Path(file_name).suffix.lower()
    # Only categorize allowed extensions
    if ext in {".png", ".jpg", ".jpeg"}:
        return "image"
    if ext == ".mp3":
        return "audio"
    if ext in {".docx", ".pptx"}:
        return "doc"
    return "other"


def compute_features(record: Dict) -> Dict[str, str]:
    annot_meta = record.get("Annotator Metadata", {})
    steps = parse_first_int(str(annot_meta.get("Number of steps", "")).strip())
    tools = parse_first_int(str(annot_meta.get("Number of tools", "")).strip())
    features = {
        "level": str(record.get("Level")),
        "step_bucket": step_bucket(steps),
        "tool_bucket": tool_bucket(tools),
        "file_group": file_type_group(record.get("file_name", "")),
    }
    return features


def _balanced_targets(
    value_counts: Counter, desired_total: int, ratio: float
) -> Dict[str, int]:
    targets: Dict[str, int] = {}
    remainder_pairs: List[Tuple[float, str]] = []
    running_total = 0
    for value, count in value_counts.items():
        exact = count * ratio
        base = math.floor(exact)
        targets[value] = base
        running_total += base
        remainder_pairs.append((exact - base, value))
    remainder_pairs.sort(reverse=True)

    need = desired_total - running_total
    if need > 0:
        for _, value in remainder_pairs:
            if need == 0:
                break
            targets[value] += 1
            need -= 1
    elif need < 0:
        # Remove from the lowest fractional contributions first.
        for _, value in sorted(
            remainder_pairs, key=lambda item: (item[0], item[1])
        ):
            if need == 0:
                break
            if targets[value] > 0:
                targets[value] -= 1
                need += 1
    return targets


def determine_targets(
    feature_table: List[Dict[str, str]], ratio: float
) -> Dict[str, Dict[str, int]]:
    total = len(feature_table)
    desired_val_total = round(total * ratio)
    targets: Dict[str, Dict[str, int]] = {}
    for feature_name in feature_table[0].keys():
        counter = Counter(row[feature_name] for row in feature_table)
        targets[feature_name] = _balanced_targets(
            counter, desired_val_total, ratio
        )
    return targets


def compute_cost(
    current: Dict[str, Counter], targets: Dict[str, Dict[str, int]]
) -> int:
    cost = 0
    for feature, value_counts in targets.items():
        for value, target in value_counts.items():
            cost += (current[feature][value] - target) ** 2
    return cost


def assign_splits(
    records: List[Dict],
    features: List[Dict[str, str]],
    ratio: float,
    seed: int,
) -> Tuple[List[Dict], List[Dict]]:
    total = len(records)
    desired_val_total = round(total * ratio)
    targets = determine_targets(features, ratio)

    indices = list(range(total))
    random.Random(seed).shuffle(indices)

    current_counts: Dict[str, Counter] = {feat: Counter() for feat in targets}
    validation_indices: List[int] = []

    for position, idx in enumerate(indices):
        remaining = len(indices) - position
        remaining_need = desired_val_total - len(validation_indices)
        feature_row = features[idx]

        if remaining_need == 0:
            continue  # everything else goes to test
        if remaining_need == remaining:
            validation_indices.append(idx)
            for feature, value in feature_row.items():
                current_counts[feature][value] += 1
            continue

        tentative_counts = {
            feat: counter.copy() for feat, counter in current_counts.items()
        }
        for feature, value in feature_row.items():
            tentative_counts[feature][value] += 1

        cost_if_val = compute_cost(tentative_counts, targets)
        cost_if_test = compute_cost(current_counts, targets)

        if cost_if_val < cost_if_test or (
            cost_if_val == cost_if_test
            and len(validation_indices) < desired_val_total
        ):
            validation_indices.append(idx)
            current_counts = tentative_counts

    validation_set = [records[i] for i in sorted(validation_indices)]
    test_set = [
        record
        for i, record in enumerate(records)
        if i not in validation_indices
    ]
    return validation_set, test_set


def write_json(path: Path, records: List[Dict]) -> None:
    """Write records to a JSON file with proper formatting."""
    with path.open("w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)


def write_validation_json(path: Path, records: List[Dict]) -> None:
    """Write validation records in the specific format with dataset wrapper."""
    validation_data = {
        "dataset": [
            {
                "question": record.get("Question", ""),
                "answer": record.get("Final answer", ""),
            }
            for record in records
        ]
    }
    with path.open("w", encoding="utf-8") as fh:
        json.dump(validation_data, fh, ensure_ascii=False, indent=4)


def copy_attachments(
    records: List[Dict],
    target_dir: Path,
    source_attachments_dir: Path,
) -> None:
    """Copy attachment files referenced in records to target directory's attachements folder."""
    if not source_attachments_dir.exists():
        print(
            f"Warning: Attachments directory not found: "
            f"{source_attachments_dir}"
        )
        return

    # Create attachements subdirectory
    target_attachments_dir = target_dir / "attachements"
    target_attachments_dir.mkdir(parents=True, exist_ok=True)

    copied_files = set()
    for record in records:
        file_name = record.get("file_name", "").strip()
        if not file_name:
            continue

        source_file = source_attachments_dir / file_name
        if source_file.exists() and file_name not in copied_files:
            target_file = target_attachments_dir / file_name
            shutil.copy2(source_file, target_file)
            copied_files.add(file_name)
            print(
                f"Copied attachment: {file_name} -> "
                f"{target_dir.name}/attachements/"
            )
        elif not source_file.exists():
            print(f"Warning: Attachment file not found: {file_name}")

    if copied_files:
        print(
            f"Total attachments copied to "
            f"{target_dir.name}/attachements/: {len(copied_files)}"
        )
    else:
        print(f"No attachments needed for {target_dir.name}/")


def main() -> None:
    args = parse_args()
    records: List[Dict] = []
    for line in args.input.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    if not records:
        raise SystemExit("Input file is empty.")

    print(f"Total records loaded: {len(records)}")

    # Filter records based on global parameters and track rejections by reason
    filtered_records = []
    rejected_by_reason: Dict[str, List[Dict]] = {
        "disallowed_file_extension": [],
        "time_too_long": [],
        "tools_violation": [],
    }

    for record in records:
        reason = get_rejection_reason(record)
        if reason is None:
            filtered_records.append(record)
        else:
            rejected_by_reason[reason].append(record)

    total_rejected = sum(
        len(rejected) for rejected in rejected_by_reason.values()
    )
    print(
        f"Records after filtering: {len(filtered_records)} "
        f"(removed {total_rejected})"
    )
    for reason, records in rejected_by_reason.items():
        if records:
            print(f"  - {reason}: {len(records)} records")

    if not filtered_records:
        raise SystemExit("No records remain after filtering.")

    # Sort records by complexity (level first, then time duration)
    sorted_records = sort_records_by_complexity(filtered_records)
    print("Records sorted by level (1-3) and time duration")

    features = [compute_features(record) for record in sorted_records]
    val_set, test_set = assign_splits(
        sorted_records, features, args.val_ratio, args.seed
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Sort both sets by complexity before writing
    val_set_sorted = sort_records_by_complexity(val_set)
    test_set_sorted = sort_records_by_complexity(test_set)

    # Create separate directories for validation and test sets
    val_dir = args.output_dir / "validation_sets"
    test_dir = args.output_dir / "test_set"
    val_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON files only
    # Validation set: save in both formats
    # 1. Simple Q&A format with dataset wrapper
    val_json_path = val_dir / "validation.json"
    write_validation_json(val_json_path, val_set_sorted)
    print(f"Validation JSON written in dataset format -> {val_json_path}")

    # 2. Verbose format (original full metadata)
    val_json_verbose_path = val_dir / "validation_verbose.json"
    write_json(val_json_verbose_path, val_set_sorted)
    print(
        f"Validation JSON written in verbose format -> {val_json_verbose_path}"
    )

    # Test set: use original format (full metadata)
    test_json_path = test_dir / "test.json"
    write_json(test_json_path, test_set_sorted)
    print(f"Test JSON written in original format -> {test_json_path}")

    print(f"Validation set: {len(val_set_sorted)} examples")
    print(f"Test set: {len(test_set_sorted)} examples")

    # Copy attachment files to corresponding directories
    source_attachments_dir = args.input.parent / "attachements"
    copy_attachments(val_set_sorted, val_dir, source_attachments_dir)
    copy_attachments(test_set_sorted, test_dir, source_attachments_dir)

    # Write rejected records by reason
    rejected_dir = args.output_dir / "rejected"
    rejected_dir.mkdir(parents=True, exist_ok=True)

    for reason, rejected_records in rejected_by_reason.items():
        if not rejected_records:
            continue

        # Create directory for this rejection reason
        reason_dir = rejected_dir / reason
        reason_dir.mkdir(parents=True, exist_ok=True)

        # Sort rejected records by complexity
        sorted_rejected = sort_records_by_complexity(rejected_records)

        # Write both simplified and verbose versions
        rejected_json_path = reason_dir / f"{reason}.json"
        write_validation_json(rejected_json_path, sorted_rejected)
        print(
            f"Rejected ({reason}) JSON written in dataset format -> "
            f"{rejected_json_path}"
        )

        rejected_json_verbose_path = reason_dir / f"{reason}_verbose.json"
        write_json(rejected_json_verbose_path, sorted_rejected)
        print(
            f"Rejected ({reason}) JSON written in verbose format -> "
            f"{rejected_json_verbose_path}"
        )

        # Copy attachments for rejected records
        copy_attachments(sorted_rejected, reason_dir, source_attachments_dir)

        print(f"Rejected ({reason}): {len(sorted_rejected)} examples")


if __name__ == "__main__":
    main()
