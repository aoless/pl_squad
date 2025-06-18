from __future__ import annotations

import os
import sys
from typing import List

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger

from pl_squad.agents.squad_lookup_agent import answer_football_question
from pl_squad.model import Player, Squad

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))

_llm = ChatOpenAI(model_name=MODEL_NAME, temperature=TEMPERATURE)


_squad_parser = PydanticOutputParser(pydantic_object=Squad)
_fixing_parser = OutputFixingParser.from_llm(parser=_squad_parser, llm=_llm)

_REFORMAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are an expert data extractor. Extract all relevant information from the following JSON."
                "Return a JSON object that matches the following schema:\n{format_instructions}"
            ),
        ),
        ("human", "{agent_answer}"),
    ]
)


def _parse_agent_answer(raw_answer: str) -> Squad:
    """Run the re-formatting LLM + parser pipeline and return a Squad object."""
    runnable = _REFORMAT_PROMPT | _llm | _fixing_parser
    return runnable.invoke(
        {
            "agent_answer": raw_answer,
            "format_instructions": _squad_parser.get_format_instructions(),
        }
    )


def _pretty_print_players(players: List[Player]) -> str:
    """Human-friendly multi-line string showing all player data with spacing."""
    return "\n\n".join(
        f"**{p.firstname} {p.lastname}** ({p.position})\n"
        f"Number: {p.number}, Age: {p.age}\n"
        f"Birth Date: {p.birth_date}, Birth Place: {p.birth_place}\n"
        f"Photo: {p.photo}"
        for p in players
    )


def squad_chain(question: str) -> str:
    """
    1. Delegates the question to the ReAct agent.
    2. Parses the agent output into structured Player / Squad data, with full player details.
    3. Returns a nicely formatted string for display.
    """
    logger.info("Received question: {}", question)
    raw_answer = answer_football_question(question)
    logger.debug("Raw agent answer: {}", raw_answer)

    try:
        squad = _parse_agent_answer(raw_answer)
        logger.debug("Parsed {} player records", len(squad.players))
        return _pretty_print_players(squad.players)
    except Exception as exc:
        logger.warning(
            "Could not structure output, falling back to raw answer: {}", exc
        )
        # Fallback: return whatever the agent said
        return raw_answer


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python -m chains.squad_chain '<your question here>'",
            file=sys.stderr,
        )
        sys.exit(1)

    _q = " ".join(sys.argv[1:])
    print(squad_chain(_q))
