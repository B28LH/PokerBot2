from collections import Counter
from itertools import product, chain, combinations
import random
import re

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

def ExpectedPotIncrease(Players, Bet, StdRaise): #This is probably totally off Watch this when the bot bets
    return Bet*(Players-float(Bet*Players)/(4*StdRaise))


def RaiseCheckReturn(Pot, MyOldBets, Bet, StdRaise, Players, WinProb):
    EBR = ExpectedPotIncrease(Players, Bet, StdRaise)
    CouldWin = Pot + EBR - MyOldBets
    return round(CouldWin*WinProb - MyOldBets - Bet,4)

#Need some method of accounting for future bets
def RaiseCheckFold(Pot, MyOldBets, Bet, StdRaise, Players, WinProb): #Bet >= 0. If no bet, Bet = 0
    limit = max(Bet,StdRaise)
    WinProb *= random.random()+0.5
    FoldReturn = -MyOldBets
    CheckReturn = RaiseCheckReturn(Pot, MyOldBets, Bet, StdRaise, Players, WinProb)
    Raises = [RaiseCheckReturn(Pot, MyOldBets, i, StdRaise, Players, WinProb) for i in range(Bet+1,limit*3)]#Change 3*StdRaise??
    RaisePos = Raises.index(max(Raises))
    RaiseReturn = (RaisePos + Bet, Raises[RaisePos])
    BestPlay = max(FoldReturn, CheckReturn, RaiseReturn[1])
    if BestPlay == CheckReturn:
        if Bet == 0:
            return ("Check", '', BestPlay)
        else:
            return ("Call", '',  BestPlay)
    elif BestPlay == FoldReturn:
        return ("Fold", '', BestPlay)
    else:
        return ("Raise by ", RaiseReturn[0]-Bet, RaiseReturn[1]) #Takes initial bet into account

def CardsToInts(Cards):
    SplitUp = re.findall(r'([\dJQKA]\d?)([sdch])', Cards)
    return [(Proper[y],Proper[x]) for (x,y) in SplitUp]

'''
Pot = 60
MyOldBets = 4
StdRaise = 10
Players = 1
Chance = 0.6

print(RaiseCheckFold(Pot, MyOldBets, 0, StdRaise, Players, Chance, False))      
'''

def PlayThrough(Sims, StdRaise): #TODO: Implement bluffing
    print('-'*10+'Type H for Help'+'-'*10)
    Guide = {'O[dds]':'Reveals the current odds', 'C[ards]': 'Records new cards being put down',
             'I[ncrease]': 'Logs an increase in the pot size', 'P[layers]': 'Logs players folding',
             'E[nd]': 'Starts a new round', 'M[ove]' : 'Gives a move after a bet',
             'B[et]': 'Logs a bet', 'H[elp]' : 'Shows help guide'}       
    Com = []
    MyBets = Pot = 0
    Ante = int(input("Ante: "))
    MyCards = CardsToInts(input("My Hand: "))
    Players = OPlayers = int(input("Players (excl me): "))
    MyBets += Ante
    Pot += Ante*(Players + 1)
    Odds = WinProb(MyCards, Com, Players, Sims)
    while True:
        Choice = input("Action: ").split()
        Top = Choice[0][0].upper()
        if Top == 'O':
            print(round(100*Odds,4), '%', sep='')
        elif Top == 'C':
            Com.extend(CardsToInts(' '.join(Choice[1:])))
            Odds = WinProb(MyCards, Com, Players, Sims)
        elif Top == 'I':
            Pot += int(Choice[1])
            print('Pot is now', Pot)
        elif Top == 'P':
            Players -= int(Choice[1])
            print("There are now %s other players" % (Players-1))
            Odds = WinProb(MyCards, Com, Players, Sims)
        elif Top == 'M':
            Advice = RaiseCheckFold(Pot, MyBets, int(Choice[1]), StdRaise, Players, Odds)
            print("Advice is to ",Advice[0],Advice[1], sep='')
        elif Top == 'B':
            MyBets += int(Choice[1])
            Pot += int(Choice[1])
        elif Top == 'E':
            PlayThrough(Sims, StdRaise)
            break
        else:
            print('Commands:')
            for key in Guide:
                print(key, Guide[key])
            print('')
        
PlayThrough(1000, 12) #StdRaise is quite important (should be renamed: risk)
