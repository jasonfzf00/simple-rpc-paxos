import unittest
from unittest.mock import patch, mock_open, MagicMock
import base64
from rpc_server import RPCServer

class TestServerMethods(unittest.TestCase):
    # Initialize a mock server
    def setUp(self):
        self.node_id = 1
        self.ip = "localhost"
        self.port = 0 # Set to 0 so OS can auto assign port
        self.cluster = [(2, "localhost", 8001), (3, "localhost", 8002)]
        self.server = RPCServer(self.node_id, self.ip, self.port,self.cluster)
    
    # Utility functions test
    @patch("builtins.open", new_callable=mock_open, read_data=b"Initialized")
    def test_read_file_data(self, mock_file):
        expected_data = base64.b64encode(b"Initialized").decode("utf-8")
        mock_file.reset_mock() # Clear the mock calls from __init__ setup
        file_data = self.server.read_file_data()
        self.assertEqual(file_data, expected_data)
        mock_file.assert_called_once_with("node1/CISC5597", "rb")

    @patch("builtins.open", new_callable=mock_open)
    def test_write_file_data(self, mock_file):
        test_data = base64.b64encode(b"TestData").decode("utf-8")
        mock_file.reset_mock() # Clear the mock calls from __init__ setup
        self.server.write_file_data(test_data)
        mock_file.assert_called_once_with("node1/CISC5597", "wb")
        mock_file().write.assert_called_once_with(b"TestData")

    @patch("builtins.open", new_callable=mock_open)
    def test_write_file_data_invalid_base64(self, mock_file):
        invalid_data = "InvalidBase64Data!"

        with patch("builtins.print") as mock_print:
            self.server.write_file_data(invalid_data)
            mock_print.assert_any_call("Error: The provided file data is not valid Base64.")
    
    def test_prepare_with_higher_proposal(self):
        proposal_number = 1.1
        result = self.server.prepare(proposal_number)
        self.assertTrue(result[0]) 
        self.assertEqual(result[1], 0.1) 
        self.assertEqual(result[2], None) 
        self.assertEqual(self.server.promised_number, proposal_number)

    def test_prepare_with_lower_proposal(self):
        self.server.promised_number = 2.0
        input = "previously updated"
        expected_data = base64.b64encode(input.encode("utf-8")).decode("utf-8")
        self.server.accepted_data = expected_data
        proposal_number = 1.1
        result = self.server.prepare(proposal_number)
        self.assertFalse(result[0]) 
        self.assertEqual(result[1], 0.1) 
        self.assertEqual(result[2], expected_data) 
        self.assertEqual(self.server.promised_number, 2.0)  
        
    def test_accept_with_higher_proposal(self):
        proposal_number = 1.1
        input = "value accepted"
        expected_data = base64.b64encode(input.encode("utf-8")).decode("utf-8")
        result = self.server.accept(proposal_number,expected_data)
        self.assertTrue(result)
        self.assertEqual(self.server.promised_number, 1.1)
        self.assertEqual(self.server.accepted_number, 1.1)
        self.assertEqual(self.server.accepted_data, expected_data)
    
    def test_accept_with_lower_proposal(self):
        self.server.promised_number = 2.0
        self.server.accepted_number = 2.0
        input = "previously updated"
        expected_data = base64.b64encode(input.encode("utf-8")).decode("utf-8")
        self.server.accepted_data = expected_data
        proposal_number = 1.1
        result = self.server.accept(proposal_number,expected_data)
        self.assertFalse(result)
        self.assertEqual(self.server.promised_number, 2.0)
        self.assertEqual(self.server.accepted_number, 2.0)
        self.assertEqual(self.server.accepted_data, expected_data)
    
    # Propose phase test
    @patch("rpc_server.ServerProxy")
    def test_propose_with_majority_success(self, MockServerProxy):
        mock_proxy = MagicMock()
        expected_data = base64.b64decode(base64.b64encode(b"AcceptedData"))
        mock_proxy.prepare.return_value = (True, 0.2, expected_data)
        MockServerProxy.return_value = mock_proxy
        self.server.quorum = 2
        result = self.server.propose()
        self.assertTrue(result)
        self.assertEqual(self.server.accepted_data, expected_data) # Check if data updated to previously accepted
        mock_proxy.prepare.assert_called()
    
    # Accept Phase Test  
    @patch("rpc_server.ServerProxy")
    def test_request_accept_with_quorum(self, MockServerProxy):
        mock_proxy = MagicMock()
        mock_proxy.accept.return_value = True
        MockServerProxy.return_value = mock_proxy
        result = self.server.request_accept()
        self.assertTrue(result)  
        self.assertEqual(mock_proxy.accept.call_count, len(self.cluster)) 
    
    # Update value test
    @patch("rpc_server.ServerProxy")
    @patch.object(RPCServer, "commit")
    def test_update_value_with_no_previous_accepted_data(self, mock_commit, MockServerProxy):
        mock_proxy = MagicMock()
        mock_proxy.prepare.return_value = (True, 0.0, None)
        mock_proxy.accept.return_value = True
        MockServerProxy.return_value = mock_proxy
        new_value = "UpdatedData"
        encoded_value = base64.b64encode(new_value.encode("utf-8")).decode("utf-8")
        self.server.update_value(new_value)
        mock_commit.assert_called_once_with(encoded_value)
        self.assertEqual(self.server.accepted_number,1.1)
        self.assertEqual(self.server.promised_number,1.1)
        self.assertEqual(self.server.accepted_data, encoded_value)
    
    @patch("rpc_server.ServerProxy")
    @patch.object(RPCServer, "commit")
    def test_update_value_with_previous_accepted_data(self, mock_commit, MockServerProxy):
        mock_proxy = MagicMock()
        expected_data = base64.b64decode(base64.b64encode(b"AcceptedData"))
        mock_proxy.prepare.return_value = (True, 0.2, expected_data)
        mock_proxy.accept.return_value = True
        MockServerProxy.return_value = mock_proxy
        new_value = "UpdatedData"
        encoded_value = base64.b64encode(new_value.encode("utf-8")).decode("utf-8")
        self.server.update_value(new_value)
        mock_commit.assert_called_once_with(expected_data) # Commit should write 'AcceptedData' since previously accepted
        self.assertEqual(self.server.accepted_data, expected_data)    
    
if __name__ == "__main__":
    unittest.main()
