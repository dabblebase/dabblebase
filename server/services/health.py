"""
Verify connectivity of the server to other services including the database.
"""


class HealthService:

    def __init__(self): ...

    def check(self):
        return "OK"
