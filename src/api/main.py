from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.config import settings
from agent.utils.utility import now_iso_tz
from agent.graph import build_graph
from .models import AskRequest, AskResponse, Message
from .session import get_or_create_session, read, reset

app = FastAPI(title="SQL Agent API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

_graph = build_graph()

@app.get("/api/health")
def health():
    return {"ok": True}

@app.post("/api/reset")
def api_reset(req: AskRequest):
    sid = get_or_create_session(req.session_id)
    reset(sid)
    return {"session_id": sid, "ok": True}

@app.post("/api/ask", response_model=AskResponse)
def api_ask(req: AskRequest):
    sid = get_or_create_session(req.session_id)
    sess = read(sid)

    state = {
        "user_query": req.question,
        "now_iso": now_iso_tz(settings.app_timezone),
        "timezone": settings.app_timezone,
        "previous_turns": sess.get("previous_turns", []),
    }
    final = _graph.invoke(state)

    sess["previous_turns"] = final.get("previous_turns", [])

    msgs = [
        Message(role="user", text=req.question),
        Message(role="assistant", text=final.get("reply_text") or ""),
    ]

    return AskResponse(
        session_id=sid,
        reply_text=final.get("reply_text") or "",
        final_sql=final.get("validated_sql"),
        rows=(final.get("result_rows") or [])[:100],
        rowcount=final.get("rowcount", 0),
        messages=msgs,
    )
