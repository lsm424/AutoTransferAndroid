#encoding=utf-8

class MyError(Exception):
    def __init__(self, msg):
        self.msg = msg

class UserError(Exception):
    def __init__(self, msg):
        self.msg = msg

class NomoneyError(Exception):
    def __init__(self, msg):
        self.msg = msg

class RePlayError(Exception):
    def __init__(self, msg):
        self.msg = msg