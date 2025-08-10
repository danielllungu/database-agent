from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from agent.types import ConversationTurn
from agent.llm.nodes.respond import respond_node
from agent.llm.nodes.rephrase import rephrase_node
from agent.types import QueryContext
from agent.schema_cache.cache import get_schema_snapshot
from agent.llm.nodes.plan_sql import plan_sql_node
from agent.llm.nodes.validate_fix import validate_fix_node
from agent.llm.nodes.run_query import run_query_node


class AgentState(TypedDict, total=False):
    user_query: str
    now_iso: str
    timezone: str
    previous_turns: list[ConversationTurn]
    rephrased: str
    schema: object
    sql_draft: str
    validated_sql: str | None
    result_rows: list[dict]
    rowcount: int
    reply_text: str
    error: Optional[str]

def build_graph():
    g = StateGraph(AgentState)

    def n1(state: AgentState):

        ctx = QueryContext(
            user_query=state["user_query"],
            now_iso=state["now_iso"],
            timezone=state["timezone"],
            previous_turns=state.get("previous_turns", []),
        )
        out = rephrase_node(ctx)
        state["rephrased"] = out.rephrased_query
        return state

    def n2(state: AgentState):
        schema = get_schema_snapshot()
        state["schema"] = schema
        plan = plan_sql_node(state["user_query"], state["rephrased"], schema)
        state["sql_draft"] = plan.sql_draft
        return state

    def n3(state: AgentState):
        val = validate_fix_node(state["sql_draft"], state["schema"])
        state["validated_sql"] = val.validated_sql
        if not val.validated_sql:
            state["error"] = val.last_error
        return state

    def n4(state: AgentState):
        if not state.get("validated_sql"):
            state["result_rows"] = []
            state["rowcount"] = 0
            return state
        exec_res = run_query_node(state["validated_sql"])
        state["result_rows"] = exec_res.rows
        state["rowcount"] = exec_res.rowcount
        return state

    def n5(state: AgentState):
        prev = state.get("previous_turns", [])
        minimal_prev = [
            {
                "original_question": t.original_question,
                "rephrased_question": t.rephrased_question,
                "final_sql": t.final_sql,
                "rowcount": t.rowcount,
                "timestamp_iso": t.timestamp_iso,
            } for t in prev[-10:]
        ]
        text = respond_node(
            now_iso=state["now_iso"],
            timezone=state["timezone"],
            original_question=state["user_query"],
            rephrased_question=state.get("rephrased", state["user_query"]),
            final_sql=state.get("validated_sql") or state.get("sql_draft", ""),
            result_rows=state.get("result_rows", []),
            rowcount=state.get("rowcount", 0),
            previous_turns_minimal=minimal_prev,
        )
        state["reply_text"] = text

        turn = ConversationTurn(
            original_question=state["user_query"],
            rephrased_question=state.get("rephrased", state["user_query"]),
            final_sql=state.get("validated_sql") or state.get("sql_draft", ""),
            result_preview=state.get("result_rows", [])[:10],
            rowcount=state.get("rowcount", 0),
            timestamp_iso=state["now_iso"],
        )
        state["previous_turns"] = prev + [turn]
        return state

    g.add_node("rephrase", n1)
    g.add_node("plan_sql", n2)
    g.add_node("validate_fix", n3)
    g.add_node("run_query", n4)
    g.add_node("respond", n5)

    g.set_entry_point("rephrase")
    g.add_edge("rephrase", "plan_sql")
    g.add_edge("plan_sql", "validate_fix")
    g.add_edge("validate_fix", "run_query")
    g.add_edge("run_query", "respond")
    g.add_edge("respond", END)

    return g.compile()
