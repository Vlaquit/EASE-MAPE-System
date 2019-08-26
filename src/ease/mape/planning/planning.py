from abc import ABC, abstractmethod


def planning(alert):
    switcher = {0: "Nothing", 1: "Add", 2: "Remove"}
    return switcher.get(alert, "Invalid alert")



class Planning:
    def __init__(self):
        self.decision = 0
