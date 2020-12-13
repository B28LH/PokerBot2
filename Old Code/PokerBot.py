"""
Creating a representation of cards and evaluating hand strengths
"""
from itertools import product as prod
cardValues = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
for i in range(10):
    cardValues[str(i)] = i
valueNames = {'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
fullSuits = {'C': 'Clubs', 'H': 'Hearts', 'S': 'Spades', 'D': 'Diamonds'}


class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        if value.isdigit():
            self.num = value
            self.picture = False
        else:
            self.num = cardValues[value]
            self.picture = True

    def __str__(self):
        if self.picture:
            return f"{valueNames[self.value]} of {fullSuits[self.suit]}"
        else:
            return f"{self.value} of {fullSuits[self.suit]}"

    def __repr__(self):
        return f"{self.value} {self.suit}"

    def __le__(self, other):
        return self.value <= other.value


print(list(prod(fullSuits.keys(), cardValues.keys())))



