from unittest.mock import Mock, patch

import requests

from otica_scripts.evolution_sender import EvolutionSender
from otica_scripts.store import Store


def test_evolution_sender_init() -> None:
    sender = EvolutionSender()
    assert sender.api_url == "http://localhost:8080"
    assert sender.api_key == "sua_api_key_global"
    assert sender.instance_name == "OticaBot"
    assert "apikey" in sender.headers


def test_format_phone() -> None:
    sender = EvolutionSender()
    assert sender._format_phone("+5511999999999") == "5511999999999"
    assert sender._format_phone("55-11-9999-99999") == "5511999999999"


@patch("requests.post")
def test_send_to_store_success(mock_post: Mock) -> None:
    mock_response = Mock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response
    
    sender = EvolutionSender()
    store = Store(name="Test", phone="+5511999999999")
    
    result = sender.send_to_store(store, "Hello")
    
    assert result is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["number"] == "5511999999999"
    assert kwargs["json"]["textMessage"]["text"] == "Hello"


@patch("requests.post")
def test_send_to_store_failure(mock_post: Mock) -> None:
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response
    
    sender = EvolutionSender()
    store = Store(name="Test", phone="+5511999999999")
    
    result = sender.send_to_store(store, "Hello")
    
    assert result is False
