"""测试 Memory 和 Coordinator"""
from app.memory.memory import Memory


class TestMemory:
    def test_buffer_within_limit(self):
        m = Memory(buffer_size=3)
        m.add("q1", "a1")
        m.add("q2", "a2")
        assert len(m.buffer) == 2
        assert m.summary == ""

    def test_get_context(self):
        m = Memory(buffer_size=3)
        m.add("北京有什么好玩的", "推荐故宫")
        ctx = m.get_context()
        assert "北京有什么好玩的" in ctx
        assert "推荐故宫" in ctx

    def test_clear(self):
        m = Memory(buffer_size=3)
        m.add("q", "a")
        m.clear()
        assert len(m.buffer) == 0
        assert m.summary == ""
