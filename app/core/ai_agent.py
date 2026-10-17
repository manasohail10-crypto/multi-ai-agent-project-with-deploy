from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

from app.common.custom_exception import CustomException
from app.common.logger import get_logger
from app.config.settings import GROQ_API_KEY

logger = get_logger(__name__)

# LangChain changed the helper name over time. We try the new one first.
try:
    from langchain.agents import create_agent

    def _build_agent(llm, tools, system_prompt):
        return create_agent(model=llm, tools=tools, system_prompt=system_prompt)

except ImportError:
    from langgraph.prebuilt import create_react_agent

    def _build_agent(llm, tools, system_prompt):
        return create_react_agent(llm, tools=tools, prompt=system_prompt)


def get_response_for_ai_agent(
    llm_id: str,
    query: list[str],
    allow_search: bool,
    system_prompt: str,
) -> str:
    """Ask the agent and return the final text answer."""
    try:
        logger.info(f"Agent called. Model={llm_id}, web search={allow_search}")

        llm = ChatGroq(model=llm_id, api_key=GROQ_API_KEY)

        tools = [TavilySearch(max_results=2)] if allow_search else []

        agent = _build_agent(llm, tools, system_prompt)

        messages = [HumanMessage(content=text) for text in query]
        result = agent.invoke({"messages": messages})

        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        if not ai_messages:
            raise ValueError("The agent returned no answer")

        answer = ai_messages[-1].content
        logger.info("Agent answered successfully")
        return answer

    except Exception as e:
        logger.error(f"Agent failed: {e}")
        raise CustomException("Failed to get response from AI agent", e)