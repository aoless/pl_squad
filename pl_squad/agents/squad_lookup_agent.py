from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from loguru import logger

from pl_squad.tools import get_full_team_details, search_team

load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))


TOOLS: List[Tool] = [
    Tool(
        name="SearchTeamID",
        func=search_team,
        description=(
            "Return the API‑Football numeric team ID for a given club name. "
            "Input: the club name (e.g. 'Manchester United'). Output: team ID as string."
        ),
    ),
    Tool(
        name="GetTeamSquad",
        func=get_full_team_details,
        description=(
            "Retrieve the squad for a team ID from available data. Use all the players details available. "
            "Input format: '<team_id>[,<season>]'. Returns raw JSON list."
        ),
    ),
]


llm = ChatOpenAI(temperature=TEMPERATURE, model_name=MODEL_NAME)
react_prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm=llm, tools=TOOLS, prompt=react_prompt)
agent_executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True)


def answer_football_question(question: str) -> str:
    logger.info("Agent invoked with question: %s", question)
    result = agent_executor.invoke({"input": question})
    answer = result["output"]
    return answer
