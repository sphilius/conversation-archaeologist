"""
Unit tests for Branch Detector nano-agent.

Run with: pytest tests/test_branch_detector.py -v
"""

import pytest
from nano_agents.branch_detector import BranchDetector, MessageNode, ConversationTree


class TestBranchDetector:
    """Test suite for BranchDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = BranchDetector()
    
    def test_linear_conversation(self):
        """Test simple linear conversation with no branches."""
        messages = [
            {
                "id": "msg_1",
                "parent_id": None,
                "role": "user",
                "content": "Hello",
                "timestamp": "2024-01-01T10:00:00Z"
            },
            {
                "id": "msg_2",
                "parent_id": "msg_1",
                "role": "assistant",
                "content": "Hi there!",
                "timestamp": "2024-01-01T10:00:01Z"
            }
        ]
        
        tree = self.detector.build_tree(messages)
        
        assert len(tree.nodes) == 2
        assert len(tree.branches) == 1
        assert tree.active_branch == "main"
        assert tree.root_id == "msg_1"
    
    def test_single_branch_point(self):
        """Test conversation with one branch point."""
        messages = [
            {
                "id": "msg_1",
                "parent_id": None,
                "role": "user",
                "content": "Hello",
                "timestamp": "2024-01-01T10:00:00Z"
            },
            {
                "id": "msg_2",
                "parent_id": "msg_1",
                "role": "assistant",
                "content": "Response 1",
                "timestamp": "2024-01-01T10:00:01Z"
            },
            {
                "id": "msg_3",
                "parent_id": "msg_1",  # Alternative response
                "role": "assistant",
                "content": "Response 2",
                "timestamp": "2024-01-01T10:00:02Z"  # More recent
            }
        ]
        
        tree = self.detector.build_tree(messages)
        
        assert len(tree.nodes) == 3
        assert len(tree.branches) == 2  # main + branch_1
        assert "main" in tree.branches
        assert "branch_1" in tree.branches
        
        # msg_3 is more recent, so branch_1 should be active
        assert tree.active_branch == "branch_1"
        assert tree.nodes["msg_3"].is_active
    
    def test_nested_branches(self):
        """Test conversation with branches within branches."""
        messages = [
            {"id": "1", "parent_id": None, "role": "user", 
             "content": "Q1", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": "2", "parent_id": "1", "role": "assistant",
             "content": "A1", "timestamp": "2024-01-01T10:00:01Z"},
            {"id": "3", "parent_id": "2", "role": "user",
             "content": "Q2", "timestamp": "2024-01-01T10:00:02Z"},
            {"id": "4", "parent_id": "3", "role": "assistant",
             "content": "A2a", "timestamp": "2024-01-01T10:00:03Z"},
            {"id": "5", "parent_id": "3", "role": "assistant",
             "content": "A2b", "timestamp": "2024-01-01T10:00:04Z"},
        ]
        
        tree = self.detector.build_tree(messages)
        
        assert len(tree.nodes) == 5
        assert len(tree.branches) == 2
    
    def test_metrics_calculation(self):
        """Test that metrics are calculated correctly."""
        messages = [
            {"id": "1", "parent_id": None, "role": "user",
             "content": "Q", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": "2", "parent_id": "1", "role": "assistant",
             "content": "A1", "timestamp": "2024-01-01T10:00:01Z"},
            {"id": "3", "parent_id": "1", "role": "assistant",
             "content": "A2", "timestamp": "2024-01-01T10:00:02Z"},
        ]
        
        tree = self.detector.build_tree(messages)
        metrics = self.detector.get_metrics(tree)
        
        assert metrics['total_messages'] == 3
        assert metrics['total_branches'] == 2
        assert metrics['branch_points'] == 1  # One node with multiple children
        assert metrics['max_depth'] == 2
    
    def test_empty_message_list(self):
        """Test that empty message list is rejected."""
        with pytest.raises(ValueError, match="empty message list"):
            self.detector.build_tree([])
    
    def test_missing_required_fields(self):
        """Test that messages with missing fields are rejected."""
        invalid_messages = [
            {"id": "1", "parent_id": None},  # Missing role, content, timestamp
        ]
        
        with pytest.raises(ValueError, match="missing required fields"):
            self.detector.build_tree(invalid_messages)
    
    def test_invalid_role(self):
        """Test that invalid roles are rejected."""
        invalid_messages = [
            {
                "id": "1",
                "parent_id": None,
                "role": "invalid_role",  # Should be 'user' or 'assistant'
                "content": "Test",
                "timestamp": "2024-01-01T10:00:00Z"
            }
        ]
        
        with pytest.raises(ValueError, match="Invalid role"):
            self.detector.build_tree(invalid_messages)
    
    def test_multiple_roots(self):
        """Test that multiple root messages are rejected."""
        invalid_messages = [
            {"id": "1", "parent_id": None, "role": "user",
             "content": "Q1", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": "2", "parent_id": None, "role": "user",  # Another root!
             "content": "Q2", "timestamp": "2024-01-01T10:00:01Z"},
        ]
        
        with pytest.raises(ValueError, match="Multiple root messages"):
            self.detector.build_tree(invalid_messages)
    
    def test_message_node_properties(self):
        """Test MessageNode dataclass properties."""
        node = MessageNode(
            id="test_id",
            parent_id="parent_id",
            role="user",
            content="Test content",
            timestamp="2024-01-01T10:00:00Z",
            artifacts=[{"type": "code", "content": "print('hi')"}],
            tool_calls=[{"tool": "web_search", "query": "test"}]
        )
        
        assert node.id == "test_id"
        assert node.parent_id == "parent_id"
        assert node.role == "user"
        assert len(node.artifacts) == 1
        assert len(node.tool_calls) == 1
        assert node.branch_id == "main"  # Default
        assert not node.is_active  # Default
    
    def test_active_branch_selection(self):
        """Test that most recent branch is marked as active."""
        messages = [
            {"id": "1", "parent_id": None, "role": "user",
             "content": "Q", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": "2", "parent_id": "1", "role": "assistant",
             "content": "A1", "timestamp": "2024-01-01T10:00:01Z"},  # Older
            {"id": "3", "parent_id": "1", "role": "assistant",
             "content": "A2", "timestamp": "2024-01-01T10:00:05Z"},  # Newer
        ]
        
        tree = self.detector.build_tree(messages)
        
        # msg_3's branch should be active (more recent)
        assert tree.nodes["3"].is_active
        assert not tree.nodes["2"].is_active


class TestBranchDetectorComplexCases:
    """Test complex branching scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = BranchDetector()
    
    def test_three_way_branch(self):
        """Test branching with three alternatives."""
        messages = [
            {"id": "1", "parent_id": None, "role": "user",
             "content": "Q", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": "2", "parent_id": "1", "role": "assistant",
             "content": "A1", "timestamp": "2024-01-01T10:00:01Z"},
            {"id": "3", "parent_id": "1", "role": "assistant",
             "content": "A2", "timestamp": "2024-01-01T10:00:02Z"},
            {"id": "4", "parent_id": "1", "role": "assistant",
             "content": "A3", "timestamp": "2024-01-01T10:00:03Z"},
        ]
        
        tree = self.detector.build_tree(messages)
        
        assert len(tree.branches) == 3  # main, branch_1, branch_2
        assert len(tree.nodes) == 4
    
    def test_long_linear_then_branch(self):
        """Test long linear conversation followed by branch."""
        messages = []
        
        # Create 10 linear messages
        for i in range(10):
            messages.append({
                "id": f"msg_{i+1}",
                "parent_id": f"msg_{i}" if i > 0 else None,
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message {i+1}",
                "timestamp": f"2024-01-01T10:00:{i:02d}Z"
            })
        
        # Add branch at message 10
        messages.append({
            "id": "msg_11",
            "parent_id": "msg_10",
            "role": "assistant",
            "content": "Alternative response",
            "timestamp": "2024-01-01T10:00:10Z"
        })
        
        tree = self.detector.build_tree(messages)
        
        assert len(tree.nodes) == 11
        assert len(tree.branches) == 2
        assert tree.nodes["msg_10"].children[0].id in ["msg_11"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
