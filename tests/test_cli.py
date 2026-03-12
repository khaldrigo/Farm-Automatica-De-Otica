from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from otica_scripts.cli import cli


def test_cli_list_stores_empty():
    runner = CliRunner()
    with patch("otica_scripts.cli.StoreManager") as mock_sm:
        mock_instance = mock_sm.return_value
        mock_instance.get_all_stores.return_value = []

        result = runner.invoke(cli, ["list-stores"])
        assert result.exit_code == 0
        assert "No stores found. Add some stores first!" in result.output

def test_cli_add_store():
    runner = CliRunner()
    with patch("otica_scripts.cli.StoreManager") as mock_sm:
        mock_instance = mock_sm.return_value
        mock_store = MagicMock()
        mock_store.name = "Test Ótica"
        mock_store.phone = "+5511999999999"
        mock_instance.add_store.return_value = mock_store

        result = runner.invoke(cli, ["add-store", "--name", "Test Ótica", "--phone", "+5511999999999"])
        assert result.exit_code == 0
        assert "Added store: Test Ótica" in result.output
        mock_instance.add_store.assert_called_once_with("Test Ótica", "+5511999999999", None)

def test_cli_send_message_test_mode():
    runner = CliRunner()
    with patch("otica_scripts.cli.StoreManager") as mock_sm, \
         patch("otica_scripts.cli.EvolutionSender") as mock_sender, \
         patch("otica_scripts.cli.MessageManager"):
        mock_store = MagicMock()
        mock_store.name = "Test"
        mock_store.phone = "123"
        mock_sm.return_value.get_all_stores.return_value = [mock_store]
        mock_sender.return_value.open_whatsapp.return_value = True
        mock_sender.return_value.send_to_all.return_value = {"Test": True}

        result = runner.invoke(cli, ["send", "Testing message", "--test", "--provider", "evolution"])

        assert result.exit_code == 0
        assert "[TEST MODE] Sending to only 1 store..." in result.output
        assert "✅ SENT | Test | 123" in result.output

def test_cli_remove_store():
    runner = CliRunner()
    with patch("otica_scripts.cli.StoreManager") as mock_sm:
        mock_instance = mock_sm.return_value
        mock_instance.remove_store.return_value = True

        result = runner.invoke(cli, ["remove-store", "Test Ótica"])
        assert result.exit_code == 0
        assert "Removed store: Test Ótica" in result.output
