from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from loguru import logger

from pl_squad.tools import (
    get_full_team_details,
    get_player_details,
    list_clubs,
    search_player,
)

load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))


TOOLS: List[Tool] = [
    Tool(
        name="ListPremierLeagueClubs",
        func=list_clubs,
        description="Fetch metadata (incl. team_id) for every EPL club. Optional season.",
    ),
    Tool(
        name="GetFullTeamDetails",
        func=get_full_team_details,
        description="Detailed profiles for every player in a team. Optional season.",
    ),
    Tool(
        name="GetPlayerDetails",
        func=get_player_details,
        description="Full profile for one player by player_id.",
    ),
    Tool(
        name="SearchPlayer",
        func=search_player,
        description="Search player by name to discover player_id(s).",
    ),
]


llm = ChatOpenAI(temperature=TEMPERATURE, model_name=MODEL_NAME)

custom_react_prompt = (
    custom_template
) = """You are an intelligent football agent specializing exclusively in the English Premier League (EPL).
Always use tools to retrieve information. Rely solely on data provided by these tools; do not use or infer any additional knowledge.
Assume the API always returns complete data - do not supplement it with guesses or external sources
Important: Whenever referencing a player, Final Answer must include (at minimum) their **full name** (first and last), **birthdate** and **playing position**.
If user will ask for more information, feel free to expand the answer.

DO NOT shorten the answer, if asked to provide a list of players, provide the full list with all the information.

Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

custom_prompt = PromptTemplate.from_template(custom_template)

agent = create_react_agent(llm=llm, tools=TOOLS, prompt=custom_prompt)
agent_executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True)


def answer_football_question(question: str) -> str:  # noqa: D401
    """Return the agent’s answer (or refusal)."""

    logger.info(f"Agent invoked with question: {question}")
    result = agent_executor.invoke({"input": question})
    return result["output"]
