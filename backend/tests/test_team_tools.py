import types
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tools


class StubUser:
    def __init__(self, metadata):
        self.private_metadata = metadata


class StubUsers:
    def __init__(self):
        self.metadata = {}

    def get(self, user_id):
        return StubUser(self.metadata)

    def update(self, user_id, private_metadata):
        self.metadata = private_metadata


class StubClerk:
    def __init__(self):
        self.users = StubUsers()


def test_set_fpl_user_id_updates_metadata(monkeypatch):
    stub = StubClerk()
    monkeypatch.setattr(tools, "_get_clerk_client", lambda: stub)
    tools.set_current_user({"sub": "user_123"})

    message = tools.set_fpl_user_id("My ID is 1234567")

    assert "Saved" in message
    assert stub.users.metadata.get("fpl_entry_id") == 1234567


def test_analyse_current_team_prompts_for_id(monkeypatch):
    monkeypatch.setattr(tools, "_get_user_private_metadata", lambda: {})
    tools.set_current_user({"sub": "user_123"})

    message = tools.analyse_current_team()

    assert "FPL entry ID" in message
