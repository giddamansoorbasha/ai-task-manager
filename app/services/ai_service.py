from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_tasks(tasks: list) -> str:
    if not tasks:
        return "You have no tasks to summarize."

    task_lines = []
    for task in tasks:
        line = f"- [{task.priority.value.upper()}] {task.title} (status: {task.status.value})"
        if task.description:
            line += f" — {task.description}"
        task_lines.append(line)

    task_text = "\n".join(task_lines)

    prompt = f"""You are a productivity assistant. A user has the following tasks:

{task_text}

Give a clear, concise summary covering:
1. Total tasks and how many are pending vs completed
2. High priority tasks that need immediate attention
3. One actionable suggestion for the user

Keep it under 100 words. Be direct and helpful."""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content