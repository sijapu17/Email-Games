#Generic and specific player classes

#Create list of CodenamesPlayers from txt file of names and email addresses
def createCodenamesPlayers(file):
    f = open(file)
    lines=f.read().splitlines()
    players=[]
    for l in lines:
        players.append(CodenamesPlayer(l.split(',')[0],l.split(',')[1]))
    return(players)
    
#Player with specific attributes for Codenames
class CodenamesPlayer(): 
    
    def __init__(self,name,email):
        self.name=name
        self.email=email        
        self.team=None
        self.spymaster=False
        
    def __repr__(self):
        return('Player({0})'.format(self.name))
    
    def setTeam(self,team,prnt=True): #Set player to either blue or red team
        if team.upper() in ('BLUE','B'):
            self.team='Blue'
        elif team.upper() in ('RED','R'):
            self.team='Red'
        else:
            print('{0} is not a valid team name - try RED or BLUE'.format(team))
            return()
        if prnt:
            print('{0} is on the {1} team'.format(self.name,self.team))
            
    def setSpymaster(self,prnt=True): #Set player to be spymaster
        self.spymaster=True
        if prnt:
            print('{0} is the spymaster for the {1} team'.format(self.name,self.team))
            
    def removeSpymaster(self): #Set player to not be spymaster
        self.spymaster=False
        
        
        
        
        
        