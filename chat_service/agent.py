import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from tools import get_tools

REACT_PROMPT = PromptTemplate.from_template("""你是一个专业的股票分析助手，请用中文回答。

你可以使用以下工具：
{tools}

工具名称列表：{tool_names}

回答格式必须严格如下：
Question: 用户的问题
Thought: 你的思考过程
Action: 工具名称（必须是工具名称列表中的一个）
Action Input: 工具的输入参数
Observation: 工具返回的结果
... (可以重复 Thought/Action/Action Input/Observation)
Thought: 我现在知道最终答案了
Final Answer: 最终答案

开始！

Question: {input}
Thought: {agent_scratchpad}""")

def get_agent():
    llm = ChatOllama(
        model="llama3.1",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
        temperature=0,
    )

    tools = get_tools()
    agent = create_react_agent(llm, tools, REACT_PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )