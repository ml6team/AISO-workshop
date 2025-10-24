"""
This file will be used to evaluate the performance of your agent.
Make sure to set the API key in the `my_agent/.env` file. See `README.md` for more details.
"""
import argparse
import datetime
import json
import os
import pathlib

import dotenv
import pydantic
from google import genai

from utils import server

dotenv.load_dotenv(dotenv_path=pathlib.Path("my_agent/.env"))


class JudgeResponse(pydantic.BaseModel):
    """Pydantic model for LLM judge response."""
    is_correct: bool


# Initialize client for LLM judge (only needed if string matching fails)
api_key = os.getenv("GOOGLE_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    print("Warning: GEMINI_API_KEY not set. LLM judge will not be available.")


DATASET_PATH = "benchmark/train.json"
ATTACHMENTS_FOLDER_PATH = "benchmark/attachments"

def _load_dataset():
    """Load the train dataset."""
    dataset_path = DATASET_PATH

    try:
        with open(dataset_path, "r") as f:
            data = json.load(f)
            # Handle both array format and dict with "dataset" key
            if isinstance(data, dict) and "dataset" in data:
                return data["dataset"]
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in dataset file: {e}")


def string_match(response: str, expected_answer: str) -> bool:
    """
    Check if response matches expected answer using string comparison.
    Handles both exact matches and partial matches.
    """
    # Exact match
    if response.strip().lower() == expected_answer.strip().lower():
        return True

    return False


def llm_judge(response: str, expected_answer: str, question: str) -> bool:
    """
    Use LLM as a judge to determine if the response is correct.
    Returns a boolean indicating if the response is correct.
    """
    if client is None:
        raise ValueError("GOOGLE_API_KEY not set")
    if response is None or response.strip() == "":
        return False
    prompt = f"""
    You are an evaluation judge.
    Determine if the agent's response is semantically completely equivalent to the expected answer.

Question: {question}

Expected Answer: {expected_answer}

Agent's Response: {response}

Evaluate whether the agent's response is semantically equivalent to the expected answer, even if worded differently.
Be strict but fair - minor variations in wording are acceptable if the core answer is correct.
"""

    try:
        llm_response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": JudgeResponse,
            }
        )

        result: JudgeResponse = llm_response.parsed
        return result.is_correct
    except Exception as e:
        print(f"Error in LLM judge: {e}")
        raise e


def evaluate_single_question(question_data: dict, question_idx: int) -> dict:
    """
    Evaluate a single question.

    Args:
        question_data: Dict containing question, answer, and optional file_name
        question_idx: Index of the question in the dataset

    Returns:
        Dict with evaluation results
    """
    # Extract question and answer based on dataset format
    if "Question" in question_data:  # verbose format
        question = question_data["Question"]
        expected_answer = question_data["Final answer"]
        file_name = question_data.get("file_name", "")
    else:  # simple format
        question = question_data["question"]
        expected_answer = question_data["answer"]
        file_name = ""

    # Prepare file paths if files are provided
    file_paths = None
    if file_name:
        # Handle comma-separated file names
        files = [f.strip() for f in file_name.split(",") if f.strip()]
        if files:
            file_paths = [f"{ATTACHMENTS_FOLDER_PATH}/{f}" for f in files]

    print(f"\n{'='*80}")
    print(f"Question {question_idx + 1}")
    print(f"{'='*80}")
    print(f"Question: {question[:100]}..." if len(question) > 100 else f"Question: {question}")
    if file_paths:
        print(f"Files: {file_paths}")

    # Run the agent (using USER_ID env var if set, otherwise default "dev_user")
    user_id = os.getenv("USER_ID", "dev_user")
    try:
        agent_response = server.run_agent(question, file_paths, user_id=user_id)
        print(f"\nAgent Response: {agent_response}")
        print(f"Expected Answer: {expected_answer}")
    except Exception as e:
        print(f"Error running agent: {e}")
        raise e

    # First try string matching
    string_matches = string_match(agent_response, expected_answer)

    if string_matches:
        print("✓ Correct (string match)")
        return {
            "question_idx": question_idx,
            "question": question,
            "expected_answer": expected_answer,
            "agent_response": agent_response,
            "correct": True,
            "method": "string_match"
        }

    # Fall back to LLM judge
    print("\nString match failed, using LLM judge...")
    is_correct = llm_judge(agent_response, expected_answer, question)

    print(f"LLM Judge: {'✓ Correct' if is_correct else '✗ Incorrect'}")

    return {
        "question_idx": question_idx,
        "question": question,
        "expected_answer": expected_answer,
        "agent_response": agent_response,
        "correct": is_correct,
        "method": "llm_judge",
    }


def evaluate_all(dataset_path=None, output_file=None) -> dict:
    """
    Evaluate all questions in the dataset.

    Returns:
        Dict with aggregated results
    """
    dataset = _load_dataset()

    results = []
    correct_count = 0
    total_count = len(dataset)

    print(f"\nStarting evaluation of {total_count} questions...")
    print("=" * 80)

    for idx, question_data in enumerate(dataset):
        result = evaluate_single_question(question_data, idx)
        results.append(result)

        if result["correct"]:
            correct_count += 1

    # Calculate accuracy
    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0

    # Prepare summary
    summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_questions": total_count,
        "correct": correct_count,
        "incorrect": total_count - correct_count,
        "accuracy": round(accuracy, 2),
        "results": results
    }

    # Print summary
    print(f"\n{'='*80}")
    print("EVALUATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total Questions: {total_count}")
    print(f"Correct: {correct_count}")
    print(f"Incorrect: {total_count - correct_count}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"{'='*80}")

    # Save results to file
    if output_file is None:
        output_file = f"evaluation_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nResults saved to: {output_file}")
    except IOError as e:
        raise IOError(f"Failed to write results to {output_file}: {e}")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the agent on train dataset")
    parser.add_argument(
        "--question",
        type=int,
        help="Question index to evaluate (0-based). If not provided, evaluates all questions."
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path for results. Default: evaluation_results_<timestamp>.json"
    )

    args = parser.parse_args()

    if args.question is not None:
        # Evaluate single question
        dataset = _load_dataset()
        if args.question < 0 or args.question >= len(dataset):
            raise ValueError(f"Question index {args.question} out of range (0-{len(dataset)-1})")

        result = evaluate_single_question(dataset[args.question], args.question)
        print(f"\nResult: {'✓ Correct' if result['correct'] else '✗ Incorrect'}")
    else:
        # Evaluate all questions
        evaluate_all(output_file=args.output)
