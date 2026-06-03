import sqlite3

class dataload:
    def __new__(self):
        self.sql = sqlite3.connect("environment.db")