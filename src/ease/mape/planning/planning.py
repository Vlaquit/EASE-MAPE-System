from abc import ABC, abstractmethod


def planning(alert):
    switcher = {0: "Nothing", 1: "Add", 2: "Remove"}
    return switcher.get(alert, "Invalid alert")


print(planning(2))
print(planning(1))
print(planning(3))


class Planning:
    def __init__(self):
        pass
