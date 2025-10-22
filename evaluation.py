from agent import run_agent

def run_evaluation():

    for q, a in dataset.items():
        response = run_agent(q)

        correct = classify(response, a)

        if correct:
            correct_count += 1
        else:
            incorrect_count += 1

    return correct_count, len(dataset)

def classify(response, answer):
    # TODO: Add judge logic here (LLM?)
    pass
