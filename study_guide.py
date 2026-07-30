import time

try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Local Ollama model used by all three agents.
if OLLAMA_AVAILABLE:
    MODEL = ChatOllama(
        model="llama3.2",
        temperature=0,
    )
else:
    MODEL = None


def ask(system: str, user: str) -> str:
    """Run one LLM call with a system prompt and user input."""
    if not OLLAMA_AVAILABLE or MODEL is None:
        raise RuntimeError("LangChain Ollama package or model is not available.")
    response = MODEL.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])
    return response.content


def run_agent(name: str, system: str, user: str) -> dict:
    """Helper that logs how long each agent takes and returns result with timing."""
    print(f"Calling agent {name}...")
    start = time.time()
    result = ask(system, user)
    elapsed = round(time.time() - start, 2)
    print(f"Finished {name} in {elapsed}s")
    return {
        "name": name,
        "content": result,
        "elapsed": elapsed
    }


# Agent 1: Create a short outline
def planner_agent(topic: str) -> dict:
    return run_agent(
        "planner_agent",
        "Break this topic into 3 short study sections with clear section headers.",
        topic,
    )


# Agent 2: Turn the outline into notes
def teacher_agent(topic: str, outline: str) -> dict:
    return run_agent(
        "teacher_agent",
        "Write short beginner-friendly notes using the outline. Keep it concise with key terms and bullet points.",
        f"Topic: {topic}\n\nOutline:\n{outline}",
    )


# Agent 3: Write review questions from the notes
def quiz_agent(topic: str, notes: str) -> dict:
    return run_agent(
        "quiz_agent",
        "Write 3 short review questions with clear numbered questions based on the notes. For each question, provide a clear answer in parentheses or format like Q1: ... Answer: ...",
        f"Topic: {topic}\n\nNotes:\n{notes}",
    )


def generate_study_guide_data(topic: str) -> dict:
    """Runs all 3 agents and returns structured timing and content data."""
    start_total = time.time()
    
    plan_res = planner_agent(topic)
    teacher_res = teacher_agent(topic, plan_res["content"])
    quiz_res = quiz_agent(topic, teacher_res["content"])
    
    total_elapsed = round(time.time() - start_total, 2)
    
    full_markdown = (
        f"# Study Guide: {topic}\n\n"
        f"## Outline\n{plan_res['content']}\n\n"
        f"## Notes\n{teacher_res['content']}\n\n"
        f"## Review Questions\n{quiz_res['content']}\n"
    )

    return {
        "topic": topic,
        "total_elapsed": total_elapsed,
        "outline": plan_res,
        "notes": teacher_res,
        "quiz": quiz_res,
        "markdown": full_markdown
    }


def build_study_guide(topic: str) -> str:
    """Run all three agents in sequence and combine their output string (legacy CLI helper)."""
    data = generate_study_guide_data(topic)
    return data["markdown"]


if __name__ == "__main__":
    print("Warming up model...")
    if OLLAMA_AVAILABLE:
        try:
            MODEL.invoke("Say ready.")
            print("Model ready.\n")
        except Exception as e:
            print(f"Warning warming up model: {e}")
    else:
        print("Langchain Ollama not installed in current environment.")

    topic = input("Enter a study topic: ").strip()

    if topic:
        print("\n" + build_study_guide(topic))
    else:
        print("Please enter a valid study topic.")