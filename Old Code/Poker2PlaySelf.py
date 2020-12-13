#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 11:18:40 2018

@author: Ben
"""

from collections import Counter
from itertools import product, combinations
import random
import re
import matplotlib.pyplot as plt
from math import e

#TODO: Bluffing, testing

FullDeck = list(product(list(range(4)),list(range(2,15))))
Suits = {0: 'Diamonds', 1:'Spades', 2:'Clubs', 3:'Hearts'}
Proper = {'J': 11, 'Q': 12, 'K':13, 'A':14, 'd': 0, 's': 1, 'c': 2, 'h': 3}
for i in range(2,11):
    Proper[str(i)] = i

def Flush(L):
    return all([x[0] == L[0][0] for x in L[1:]])

def Straight(L):
    primary = all([L[i][1] == L[0][1]-i for i in range(1,len(L))])
    if L[0][1] != 14:
        return primary
    return any([primary, Straight(L[1:]+[(0,1)])])

def Multiples(L):
    return sorted(list(Counter([y for (x,y) in L]).items()), key=lambda x: (x[1],x[0]),reverse=True)

def RankHand(L):
    L = sorted(L, key=lambda x: x[1], reverse=True)
    comp = list(L)
    flush = Flush(L)
    straight = Straight(L)
    if flush:
        if straight:
            if L[0][1] == 14:
                strong = 9
            else:
                strong = 8
        else:
            strong = 5
    elif straight:
        strong = 4
    else:
        multi = Multiples(L)
        if multi[0][1] == 1:
            strong = 0
        else:
            comp = [(y,x) for (x,y) in multi]
            if multi[0][1] == 4:
                strong = 7
            elif multi[0][1] == 3:
                if multi[1][1] == 2:
                    strong = 6
                else:
                    strong = 3
            elif multi[1][1] == 2:
                strong = 2
            else:
                strong = 1
    return (strong, comp)

def BestofHands(LL):
    return max([(L,RankHand(L)) for L in LL], key=lambda x: (x[1][0],[y[1] for y in x[1][1]]))

    
def WinProb(Pocket, Com, Players, Sims):
    CardsLeft = list(FullDeck)
    for item in Pocket + Com:
        CardsLeft.remove(item)
    wins = 0
    NumCardsLeft = len(CardsLeft)
    Place = 5-len(Com)
    CardsToDeal = Place+2*Players
    for _ in range(Sims):
        others = random.sample(list(range(NumCardsLeft)),CardsToDeal)
        NewCom = Com + [CardsLeft[others.pop()] for _ in range(Place)]
        People = [BestofHands(combinations([CardsLeft[others.pop()] for _ in range(2)]+NewCom,5)) for i in range(Players)]
        MyBestHand = BestofHands(combinations(Pocket+NewCom,5))
        People.append(MyBestHand)
        TheBestHand = max(People, key=lambda x: (x[1][0],[y[1] for y in x[1][1]]))
        wins += int(MyBestHand == TheBestHand) #deal with draws?
    return wins*1.0/Sims

def logistic(x):
    return 1/(1+e**(1*(-0.5+x)))

def RaiseCheckReturn(Pot, MyOldBets, Bet, StdRaise, Players, WinProb):
    PlayersLeft = Players-float(Bet*Players)/(3*StdRaise)
    CouldWin = Pot + PlayersLeft*Bet - MyOldBets
    return round(CouldWin*WinProb - MyOldBets - Bet + Pot*1*abs(logistic(PlayersLeft)),4)

#Need some method of accounting for future bets
def RaiseCheckFold(Pocket, Com, Pot, MyOldBets, Bet, StdRaise, Players, Sims): #Bet >= 0. If no bet, Bet = 0
    WinProb = WinProb(Pocket, Com, Players, Sims)
    limit = max(Bet,StdRaise)
    if len(Com) < 4:
        a = 2
    else: a = 3
    FoldReturn = -MyOldBets
    CheckReturn = RaiseCheckReturn(Pot, MyOldBets, Bet, StdRaise, Players, WinProb)
    Raises = [RaiseCheckReturn(Pot, MyOldBets, i, StdRaise, Players, WinProb) for i in range(Bet+1,limit*a)]#Change 3*StdRaise??
    RaisePos = Raises.index(max(Raises))
    RaiseReturn = (RaisePos + Bet, Raises[RaisePos])
    BestPlay = max(FoldReturn, CheckReturn, RaiseReturn[1])
    if BestPlay == CheckReturn:
        if Bet == 0:
            return (0, Raises, (Bet+1,limit*a))
        else:
            return (0, Raises, (Bet+1,limit*a))
    elif BestPlay == FoldReturn:
        return (-1, Raises, (Bet+1,limit*a))
    else:
        return (RaiseReturn[0]-Bet, Raises, (Bet+1,limit*a)) #Takes initial bet into account

def CardsToInts(Cards):
    SplitUp = re.findall(r'([\dJQKA]\d?)([sdch])', Cards)
    return [(Proper[y],Proper[x]) for (x,y) in SplitUp]

#Pot = 60
#MyOldBets = 10
#StdRaise = 10
#Players = 4
#Chance = 0.5


#plt.scatter(list(range(20)), [logistic(Players-float(i*Players)/(3*StdRaise)) for i in range(20)])
#
##plt.scatter(list(range(1,20)), [Players-float(i*Players)/(2*StdRaise) for i in range(1,20)])
#
##plt.scatter(list(range(1,40)), [logistic(Players-float(i*Players)/(2*StdRaise)) for i in range(1,40)])
#Bets = list(range(StdRaise*2))
#Outs = [RaiseCheckReturn(Pot, MyOldBets, i, StdRaise, Players, Chance) for i in Bets]
#
##plt.scatter(list(range(-100,100)), [e**(-pi*x**2) for x in range(-100,100)])
#
#
#plt.scatter(Bets, Outs)     
#plt.xlabel("Bet")
#plt.ylabel("Return")

def BotsvsBots(Players):
    nums = random.shuffle(Players*2+5, range(52))
    BotCards = []
    for x in range(Players):
        BotCards.append([FullDeck[nums.pop()],FullDeck[nums.pop()]])
    print(BotCards)
    com = []
    pot = 0
    players = Players
    
BotsvsBots(4)