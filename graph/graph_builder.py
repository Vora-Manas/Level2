from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from tools import yahoo_stock_info, tavily_search
from prompts.system_prompt import get_system_prompt

def build_graph(llm):
    tools = [yahoo_stock_info, tavily_search]
    llm_with_tools = llm.bind_tools(tools)

    def reasoner(state: MessagesState):
        sys_msg = get_system_prompt()
        return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("reasoner", reasoner)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "reasoner")
    builder.add_conditional_edges("reasoner", tools_condition)
    builder.add_edge("tools", "reasoner")
    return builder.compile()