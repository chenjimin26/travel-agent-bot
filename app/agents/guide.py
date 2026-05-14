"""
GuideAgent — 攻略生成（LangChain ReAct Agent）

Agent 自主决策：先查知识库，KB 不够自动 web search。
"""
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from app.rag.vector_store import VectorStore
from app.llm.qwen_client import get_llm
from app.tools.weather import get_weather


class GuideAgent:
    def __init__(self):
        from langchain_openai import ChatOpenAI
        from app.config import Config

        self.llm = ChatOpenAI(
            model=Config.MODEL_REGISTRY.get("kimi", "kimi-k2.6"),
            openai_api_key=Config.DASHSCOPE_API_KEY,
            openai_api_base=Config.BASE_URL,
            temperature=0
        )
        self.kb = VectorStore()
        self.web_search = DuckDuckGoSearchResults(max_results=5)
        self._start_date = None
        self._days = 3

        def search_kb(query: str) -> str:
            """搜索内部知识库中的景点。优先使用此工具。输入：城市名，如'北京景点'。"""
            docs = self.kb.similarity_search(query, k=10)
            names = [d.metadata.get("name", "") for d in docs if d.metadata.get("name")]
            return "知识库景点：\n" + "\n".join(f"- {n}" for n in names[:15]) if names else "未找到相关景点"

        def search_web(query: str) -> str:
            """联网搜索景点。知识库结果不足时使用。输入：搜索关键词，如'喀什 必去景点'。"""
            return self.web_search.invoke(query)

        def search_weather(query: str) -> str:
            """查询目的地天气。必须先调用！输入：城市名，如'北京'。返回温度、晴雨等。"""
            return get_weather(query.strip(), self._start_date, self._days)

        self.agent = create_react_agent(
            model=self.llm,
            tools=[search_kb, search_web, search_weather],
            prompt="""你是旅行攻略总设计师。工作流程：
1. search_weather 查目的地天气
2. search_kb 查内部知识库景点
3. 知识库不够时用 search_web

根据天气决定每天行程风格，输出完整 JSON：
{
  "weather": "北京 5/13 ☀️晴 19-32°C, 5/14 ☀️晴, 5/15 ⛅多云",
  "attractions": ["故宫", "天坛"],
  "daily_plan": [
    {"day": 1, "spots": ["天安门", "故宫"], "indoor": false, "theme": "皇城中轴线"},
    {"day": 2, "spots": ["八达岭长城"], "indoor": false, "theme": "万里长城"},
    {"day": 3, "spots": ["国家博物馆", "天坛"], "indoor": true, "theme": "文化收官"}
  ],
  "tips": ["故宫提前7天预约"]
}
- weather 字段：把 search_weather 返回结果原文放入
- spots 里只放景点名称字符串
- 每天给一个 theme 主题
- indoor: 该天≥50%景点室内则为 true
- 下雨天优先安排室内景点"""
        )

    def search(self, destination: str, days: int, preferences: list[str] = None, start_date: str = None) -> dict:
        import json

        pref = " ".join(preferences) if preferences else ""
        date_info = f" | 出发日期：{start_date}" if start_date else ""
        query = f"目的地：{destination} | {days}天 | 偏好：{pref}{date_info}"

        # 注入日期上下文给天气 tool
        self._start_date = start_date
        self._days = days

        try:
            result = self.agent.invoke({"messages": [("user", query)]})
            messages = result.get("messages", [])
            output = messages[-1].content if messages else ""
            start = output.find("{")
            end = output.rfind("}") + 1
            return json.loads(output[start:end]) if start != -1 else {}
        except Exception as e:
            return {"attractions": [], "daily_plan": [], "tips": []}

    def get_attraction_names(self, guide: dict) -> list[str]:
        names = set(guide.get("attractions", []))
        for day in guide.get("daily_plan", []):
            for spot in day.get("spots", []):
                names.add(spot)
        return list(names)
