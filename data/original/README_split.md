## GAIA Validation Metadata Overview and Split Strategy

- **File layout**: `metadata.jsonl` is JSON Lines; each row contains top-level fields `task_id`, `Question`, `Level`, `Final answer`, `file_name`, and an `Annotator Metadata` object. The metadata block holds `Steps` (narrative list), `Number of steps`, `Tools`, `Number of tools`, `How long did this take?`, and other free-form notes.

Note that:
- `How long did this take?` is a field to capture the time investment/effort required to complete each task from the annotator's perspective
- `Number of steps` the procedural complexity and methodological approach
Correlation: Generally, more steps correlate with longer time, but not always linearly

- **Preferred storage format**: Keep releases in JSONL to retain nested metadata verbatim. The splitter can optionally emit flattened CSV summaries, but those drop the multi-line rationale fields.

## Filtering Parameters

The dataset is pre-filtered before splitting based on the following constraints (see GAIA dataset documentation for details):

- **File extensions**: Only documents (.docx, .pptx), images (.jpg, .jpeg, .png), and audio (.mp3) files are included
- **Time limit**: Tasks that took 10+ minutes are excluded (based on "How long did this take?" field)
- **Tools**: Focus on web search, calculator, image, PDF, video (YouTube), and Python tools only
- **Tool count**: Maximum 3 tools per task

## Data Organization

After filtering, records are systematically organized by complexity:

1. **Primary sort**: Level of difficulty (1 → 2 → 3)
2. **Secondary sort**: Time duration (shortest → longest within each level)
3. **Output preservation**: Both validation and test sets maintain this ordering

This ensures that easier, quicker tasks appear first in datasets, facilitating progressive difficulty testing and evaluation.

## Split Criteria

- **Difficulty proxy**: balance the `Level` labels (1–3) and step count bucket (`short` ≤4, `medium` 5–8, `long` ≥9) so validation/test cover comparable reasoning depth.
- **Tooling complexity**: balance the parsed `Number of tools` grouped as `0`, `1`, `2`, `3-4`, `5+`, plus an `unknown` catch-all when annotators answered textually.
- **File modality**: balance `file_name` by collapsing extensions into modality groups (`none`, `tabular`, `image`, `audio`, `pdf`, `doc`, `archive`, `json`, `text`, `code`, `molecular`, `other`) to ensure both splits see the same mix of attachments.
- **Split ratio**: default is 50 % validation / 50 % test (82 vs. 83 tasks for this set); changeable via `--val-ratio`.

## Output Formats and Sorting

- **Format**: JSON files only (no JSONL or CSV)
- **Sorting**: All outputs are sorted by complexity level (1, 2, 3) first, then by time duration (shortest first)
- **Directory structure**: 
  - Validation sets: `validation_sets/` folder
  - Test sets: `test_set/` folder
- **Output files**:
  - **Validation**: 
    - `validation.json`: Simple question/answer format with dataset wrapper
    - `validation_verbose.json`: Full metadata format (original structure)
  - **Test**: `test.json` - Full metadata format (original structure)

## Splitting Script

- Entry point: `split_dataset.py`. Deterministic by seed (default `211` chosen for near-perfect balance on the above features).
- Outputs: 
  - `validation_sets/validation.json` (simple Q&A format)
  - `validation_sets/validation_verbose.json` (full metadata format)
  - `validation_sets/attachements/` (relevant attachment files)
  - `test_set/test.json` (full metadata format)
  - `test_set/attachements/` (relevant attachment files)
- **Automatic attachment copying**: Script automatically copies attachment files referenced in the `file_name` field to the appropriate `attachements/` subfolder in each dataset directory
- CLI usage example:
  ```bash
  python split_dataset.py \
    --input raw_gaia_dataset.jsonl \
    --output-dir data \
    --val-ratio 0.5 \
    --seed 211
  ```
- All output files are sorted by complexity level (1-3) and time duration for consistent ordering.

## Attachment Renaming

Run `scripts/rename_attachments.py` to normalize attachment names to a numeric sequence while updating the corresponding `file_name` fields in `raw_gaia_dataset.jsonl`. The script also emits `data/original/attachment_mapping.csv` to document the mapping between the original filenames and their assigned numbers.
