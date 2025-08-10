from pathlib import Path

import pytest
from click.testing import CliRunner

from log_whisperer.cli import main as cli_main


@pytest.fixture()
def temp_home(monkeypatch, tmp_path):
    class _FakeHome(Path):
        _flavour = Path('.')._flavour

    fake_home = _FakeHome(tmp_path)
    monkeypatch.setattr("pathlib.Path.home", lambda: fake_home)
    return tmp_path


def test_status_without_config(temp_home):
    runner = CliRunner()
    result = runner.invoke(cli_main, ["status"])
    assert result.exit_code == 0
    assert "No LLM provider configured" in result.output


def test_status_with_config(temp_home):
    config_dir = Path(temp_home) / ".log-whisperer"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text(
        """
provider:
  provider: openai
  model: gpt-4o-mini
  api_key: test-key
        """.strip()
    )

    runner = CliRunner()
    result = runner.invoke(cli_main, ["status"])
    assert result.exit_code == 0
    assert "Current Configuration" in result.output
    assert "Provider" in result.output
    assert "Model" in result.output


