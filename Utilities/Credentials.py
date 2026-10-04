"""Test-account credentials come from environment variables (or a local, git-ignored .env file),
never from the repo. In CI they come from GitHub Secrets."""
import os

import pytest

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SecretStr(str):
    """A str that prints as **** in repr/f-strings, so it cannot leak through logs, pytest IDs or
    Allure parameters. str(value) still returns the real text, which is what send_keys() needs."""

    def __repr__(self):
        return "'****'"

    def __format__(self, format_spec):
        return "****"


def load_env_file(path=None):
    """Loads KEY=VALUE lines from .env into os.environ. Real environment variables win."""
    path = path or os.path.join(_PROJECT_ROOT, ".env")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def get_user_details():
    """Returns [(mobile, otp)] for pytest.mark.parametrize, with a neutral test id ('test-user')."""
    load_env_file()
    mobile, otp = os.environ.get("TEST_MOBILE"), os.environ.get("TEST_OTP")
    missing = [n for n, v in (("TEST_MOBILE", mobile), ("TEST_OTP", otp)) if not v]
    if missing:
        raise RuntimeError(
            f"Missing test credentials: {', '.join(missing)}. Locally: copy .env.example to .env and fill it in. "
            f"On GitHub: add them under Settings > Secrets and variables > Actions.")
    return [pytest.param(SecretStr(mobile), SecretStr(otp), id="test-user")]
