"""Document-grounded quiz generation using Vertex AI via LangChain."""

from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI

from tasks.Quiz_Generator.question_validation import is_distinct, parse_question


PROMPT = """You are writing a study quiz about {topic}.
Use only the supplied document excerpt. If it does not contain enough information, do not invent facts.
Write exactly one clear, specific question grounded in the excerpt, four plausible answer choices, one correct answer key, and a concise explanation grounded in the excerpt.
Return only a JSON object with keys:
"question" (string), "choices" (list of four objects with "key" A/B/C/D and "value" strings),
"answer" (one of A/B/C/D), and "explanation" (string).
Do not reuse the following previously generated questions: {previous}

Document excerpt:
{context}
"""


class QuizGenerator:
    def __init__(self, topic, num_questions, vectorstore, *, model_name="gemini-pro", llm=None):
        if not 1 <= num_questions <= 10:
            raise ValueError("Choose between one and ten questions.")
        self.topic = topic.strip() or "General knowledge"
        self.num_questions = num_questions
        self.vectorstore = vectorstore
        self.llm = llm or VertexAI(model_name=model_name, temperature=0.5, max_output_tokens=850)

    def generate_quiz(self, *, max_attempts_per_question=4):
        if self.vectorstore is None:
            raise ValueError("Upload a PDF before generating a quiz.")
        prompt = PromptTemplate.from_template(PROMPT)
        results = []
        for _ in range(self.num_questions):
            question = None
            for _attempt in range(max_attempts_per_question):
                docs = self.vectorstore.similarity_search(self.topic, k=4)
                if not docs:
                    raise ValueError("No matching document context was found. Try a different topic.")
                context = "\n\n".join(d.page_content for d in docs)
                formatted = prompt.format(
                    topic=self.topic,
                    context=context,
                    previous="; ".join(q["question"] for q in results) or "(none)",
                )
                try:
                    response = self.llm.invoke(formatted)
                    proposed = parse_question(response)
                except (ValueError, TypeError):
                    continue
                if is_distinct(proposed["question"], [q["question"] for q in results]):
                    question = proposed
                    break
            if question is None:
                if results:
                    break  # Return the validated partial quiz rather than looping forever.
                raise ValueError("Could not generate a valid, distinct question. Try another topic or document.")
            results.append(question)
        return results
