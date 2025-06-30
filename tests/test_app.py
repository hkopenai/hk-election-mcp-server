import unittest
from unittest.mock import patch, Mock
from hkopenai.hk_election_mcp_server.server import create_mcp_server

class TestApp(unittest.TestCase):
    @patch('hkopenai.hk_election_mcp_server.server.FastMCP')
    @patch('hkopenai.hk_election_mcp_server.tool_gc_registered_electors.get_gc_registered_electors')
    def test_create_mcp_server(self, mock_tool_security, mock_fastmcp):
        # Setup mocks
        mock_server = unittest.mock.Mock()
        
        # Track decorator calls and capture decorated function
        decorator_calls = []
        decorated_func = None
        
        def tool_decorator(description=None):
            # First call: @tool(description=...)
            decorator_calls.append(((), {'description': description}))
            
            def decorator(f):
                # Second call: decorator(function)
                nonlocal decorated_func
                decorated_func = f
                return f
                
            return decorator
            
        mock_server.tool = tool_decorator
        mock_fastmcp.return_value = mock_server
        mock_tool_security.return_value = [{'year': '2020', 'type': 'Phishing', 'count': 10}]

        # Test server creation
        server = create_mcp_server()

        # Verify server creation
        # mock_fastmcp.assert_called_once()
        # self.assertEqual(server, mock_server)

        # Verify tool was decorated
        # self.assertIsNotNone(decorated_func)
        
        # Test the actual decorated function if it relates to security incidents
        # if decorated_func.__name__ == 'get_gc_registered_electors':
        #     result = decorated_func()
        #     mock_tool_security.assert_called_once()
        #     self.assertEqual(result, [{'year': '2020', 'type': 'Phishing', 'count': 10}])

if __name__ == "__main__":
    unittest.main()
