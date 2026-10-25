import os
import re

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

ABSTENTION_MESSAGE = (
    "No encuentro información suficiente "
    "en los documentos para responder."
)


def generate_answer(
    question: str,
    contexts: list[dict],
) -> dict:
    """Genera una respuesta utilizando el contexto recuperado."""

    if not contexts:
        return {
            "answer": ABSTENTION_MESSAGE,
            "sources": [],
        }

    context_blocks = []

    for index, context in enumerate(contexts, start=1):
        context_blocks.append(
            f"[{index}]\n"
            f"Documento: {context['source']}\n"
            f"Fragmento: {context['chunk_id']}\n"
            f"Contenido: {context['text']}"
        )

    context_text = "\n\n".join(context_blocks)

    system_prompt = (
        "Eres un asistente documental. "
        "Responde en español utilizando exclusivamente "
        "la información de los fragmentos proporcionados. "
        "No utilices conocimiento externo ni inventes datos. "

        "Si la pregunta contiene varias partes, evalúa cada parte "
        "de manera independiente. La ausencia de información para "
        "una parte NO invalida las respuestas de las demás. "

        "Debes responder todas las partes respaldadas por el contexto, "
        "aunque otra parte de la pregunta no pueda resolverse. "
        "Para cada parte respondible, proporciona la información "
        "documentada e incluye sus referencias numéricas. "

        "Para las partes sin evidencia suficiente, indica expresamente "
        "qué información no está especificada. No asumas autorizaciones, "
        "prohibiciones ni condiciones que no aparezcan en los documentos. "

        "Si existe información pertinente para responder al menos "
        "una parte, NO devuelvas una abstención total. "

        "Únicamente cuando ninguna parte de la pregunta pueda "
        "responderse con la evidencia disponible, responde exactamente: "
        f"'{ABSTENTION_MESSAGE}' "

        "Cuando utilices información de un fragmento, "
        "incluye su referencia numérica, por ejemplo [1]. "
        "No inventes referencias."
    )

    client = OpenAI(
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_BASE_URL"],
        timeout=30.0,
        max_retries=1,
    )

    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": (
                    f"PREGUNTA:\n{question}\n\n"
                    f"CONTEXTO:\n{context_text}"
                ),
            },
        ],
    )

    answer = response.choices[0].message.content

    if not answer or not answer.strip():
        raise ValueError("El modelo devolvió una respuesta vacía.")

    answer = answer.strip()

    references = {
        int(number)
        for number in re.findall(r"\[(\d+)\]", answer)
    }

    valid_references = set(range(1, len(contexts) + 1))

    if not references.issubset(valid_references):
        raise ValueError(
            "El modelo generó referencias inexistentes."
        )

    sources = []

    for index, context in enumerate(contexts, start=1):
        if index in references:
            sources.append(
                {
                    "reference": index,
                    "source": context["source"],
                    "chunk_id": context["chunk_id"],
                    "excerpt": context["text"],
                    "distance": context["distance"],
                }
            )

    if not sources and answer != ABSTENTION_MESSAGE:
        raise ValueError(
            "El modelo respondió sin citar evidencia documental."
        )

    return {
        "answer": answer,
        "sources": sources,
    }