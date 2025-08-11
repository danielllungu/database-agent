import React, { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function useDragScroll<T extends HTMLElement>() {
  const ref = useRef<T | null>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let isDown = false;
    let startX = 0;
    let startY = 0;
    let scrollLeft = 0;
    let scrollTop = 0;

    const onDown = (e: MouseEvent) => {
      // Only left click
      if (e.button !== 0) return;
      isDown = true;
      startX = e.pageX - el.offsetLeft;
      startY = e.pageY - el.offsetTop;
      scrollLeft = el.scrollLeft;
      scrollTop = el.scrollTop;
      el.classList.add('drag-scroll');
    };
    const onLeave = () => { isDown = false; el.classList.remove('drag-scroll'); };
    const onUp = () => { isDown = false; el.classList.remove('drag-scroll'); };
    const onMove = (e: MouseEvent) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - el.offsetLeft;
      const y = e.pageY - el.offsetTop;
      const walkX = x - startX;
      const walkY = y - startY;
      el.scrollLeft = scrollLeft - walkX;
      el.scrollTop = scrollTop - walkY;
    };

    el.addEventListener('mousedown', onDown);
    el.addEventListener('mouseleave', onLeave);
    el.addEventListener('mouseup', onUp);
    el.addEventListener('mousemove', onMove);
    return () => {
      el.removeEventListener('mousedown', onDown);
      el.removeEventListener('mouseleave', onLeave);
      el.removeEventListener('mouseup', onUp);
      el.removeEventListener('mousemove', onMove);
    };
  }, []);
  return ref;
}

type Msg = { id: string; role: "user" | "assistant"; text: string; loading?: boolean };
type AskResp = {
  session_id: string;
  reply_text: string;
  final_sql?: string | null;
  rows: any[];
  rowcount: number;
  messages: { role: "user" | "assistant"; text: string }[];
};

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [question, setQuestion] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showSQL, setShowSQL] = useState(true);
  const [lastSQL, setLastSQL] = useState<string>("");
  const [lastRows, setLastRows] = useState<any[]>([]);
  const [lastRowcount, setLastRowcount] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [sqlLoading, setSqlLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const sqlPreRef = useDragScroll<HTMLPreElement>();
  const jsonPreRef = useDragScroll<HTMLPreElement>();

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, lastSQL, lastRows, sqlLoading]);

async function ask() {
  if (!question.trim() || loading) return;
  setLoading(true);
  setSqlLoading(true);
  setLastSQL("");
  setLastRows([]);
  setLastRowcount(0);

  const makeId = () => (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()));
  const userId = makeId();
  const pendingId = makeId();

  setMessages(prev => [
    ...prev,
    { id: userId, role: "user", text: question },
    { id: pendingId, role: "assistant", text: "Searching…", loading: true },
  ]);

  const asked = question;
  setQuestion("");

  try {
    const res = await fetch(`${API}/api/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: asked, show_sql: showSQL, session_id: sessionId }),
    });
    const data: AskResp = await res.json();
    setSessionId(data.session_id);

    setMessages(prev =>
      prev.map(m =>
        m.id === pendingId ? { ...m, text: data.reply_text || "(no reply)", loading: false } : m
      )
    );

    setLastSQL(data.final_sql || "");
    setLastRows(data.rows || []);
    setLastRowcount(data.rowcount || 0);
  } catch (e) {
    setMessages(prev =>
      prev.map(m =>
        m.id === pendingId ? { ...m, text: "Sorry, something went wrong.", loading: false } : m
      )
    );
  } finally {
    setSqlLoading(false);
    setLoading(false);
  }
}

  async function resetConversation() {
    const res = await fetch(`${API}/api/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: "", session_id: sessionId }),
    });
    const data = await res.json();
    setSessionId(data.session_id);
    setMessages([]);
    setLastSQL("");
    setLastRows([]);
    setLastRowcount(0);
    setQuestion("");
    setSqlLoading(false);
  }

  return (
    <div className="min-h-[100dvh] flex flex-col bg-zinc-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="mx-auto max-w-3xl px-4 py-3 flex items-center justify-between">
          <h1 className="text-lg font-semibold">SQL Agent</h1>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={showSQL} onChange={(e) => setShowSQL(e.target.checked)} />
            Show generated SQL
          </label>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-4 py-4">

          <div className="space-y-3">
            {messages.map((m) => (
                <div key={m.id} className={`rounded-2xl p-3 ${m.role === "user" ? "bg-blue-50" : "bg-white border"}`}>
                <div className="text-xs text-zinc-500 mb-1">{m.role === "user" ? "You" : "Assistant"}</div>

                {m.loading ? (
                <div className="text-sm text-zinc-500 animate-pulse">Searching…</div>
                ) : (
                <div className="prose prose-zinc max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {m.text}
                  </ReactMarkdown>
                </div>
                )}
            </div>
            ))}
          </div>

          {showSQL && (
            <div className="mt-4 rounded-2xl border bg-white p-3">
              <div className="text-xs text-zinc-500 mb-2">Generated SQL</div>
              {sqlLoading ? (
                <div className="text-sm text-zinc-500 animate-pulse">Generating SQL…</div>
              ) : (
                <pre
                  ref={sqlPreRef}
                  className="scrollbar drag-scroll overflow-x-scroll overflow-y-auto whitespace-pre font-mono text-[13px] leading-6 max-h-[60vh] min-h-40"
                >
                  {lastSQL || "(no SQL generated)"}
                </pre>
              )}

              <div className="mt-4 text-xs text-zinc-500">Database Response</div>
              {sqlLoading ? (
                <div className="text-sm text-zinc-500 animate-pulse">Querying database…</div>
              ) : (
                <>
                  <div className="mt-1 text-xs text-zinc-500">Rows: {lastRowcount}</div>
                  {!!lastRows.length && (
                    <pre
                      ref={jsonPreRef}
                      className="scrollbar drag-scroll overflow-x-scroll overflow-y-auto whitespace-pre font-mono text-[13px] leading-6 max-h-[60vh]"
                    >
                      {JSON.stringify(lastRows.slice(0, 100), null, 2)}
                    </pre>
                  )}
                </>
              )}
            </div>
          )}

          <div ref={scrollRef} className="h-24" />
        </div>
      </main>

      <footer className="border-t bg-white">
        <div className="mx-auto max-w-3xl px-4 py-3">
          <div className="flex gap-2">
            <textarea
              className="flex-1 rounded-xl border p-3 focus:outline-none focus:ring"
              placeholder="Ask a question about your database…"
              rows={2}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <div className="flex flex-col gap-2">
              <button
                onClick={resetConversation}
                className="rounded-lg border px-3 py-2 text-sm bg-zinc-50 hover:bg-zinc-100"
                disabled={loading}
              >
                Reset conversation
              </button>
              <button
                onClick={ask}
                className="rounded-lg bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
                disabled={loading}
              >
                {loading ? "Asking…" : "Ask"}
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}