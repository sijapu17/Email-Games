#Codenames#
from sendemail import send_email
from players import *
import random
import math

players=createCodenamesPlayers('C:/Users/Simon/SkyDrive/Home Stuff/Python/Email Games/player list.txt')

def otherTeam(team): #Helper function to return red if blue is input, and vice versa
    if team.upper()=='BLUE':
        return('Red')
    elif team.upper()=='RED':
        return('Blue')
    print('Invalid team {0}'.format(team))

class Game(): #Codenames top-level class
    
    def __init__(self,players,seed=None):
        
        #Set round number
        self.round=1
        #Set random seed if predictable state is required for testing
        random.seed(seed)
        #Global variable to determine whether game has finished
        self.completed=False
        self.winningTeam=None
        
        #Create board of words
        f = open('C:/Users/Simon/SkyDrive/Home Stuff/Python/Email Games/Noun list.txt')
        contents = f.read()
        word_list=contents.splitlines()
        self.words=random.sample(word_list,25)
        self.currentTeam=random.choice(('Red','Blue')) #Choose starting team
        
        #Dict of word categories (Blue, Red, Assassin, Bystander)
        self.wordCats={} 
        self.wordCats[self.currentTeam]=self.words[:9] #Assign first 9 words to starting team
        self.wordCats[otherTeam(self.currentTeam)]=self.words[9:17] #Assign next 8 words to other team
        self.wordCats['Assassin']=self.words[17] #Assign one word to assassin
        self.wordCats['Bystanders']=self.words[18:] #Assign remaining words as bystanders
        self.wordCats['Guessed']=set() #Set of words that have been guessed
        random.shuffle(self.words) #Shuffle list of words
        
        #Dict to count number of remaining words for each team left to guess
        self.nRemaining={}
        self.nRemaining['Blue']=len(self.wordCats['Blue'])
        self.nRemaining['Red']=len(self.wordCats['Red'])
        
        #Create dict of players
        self.players={}
        for p in players:
            self.players[p.name]=p
            
        #Assign teams
        self.nPlayers=len(self.players)
        teamSizes=(int(math.ceil(self.nPlayers/2)),int(math.floor(self.nPlayers/2))) #Team sizes
        names=[x for x in self.players.keys()]
        random.shuffle(names) #Put names into random order
        for name in names[:teamSizes[0]]: #Assign first half of list to Blue team
            self.players[name].setTeam('Blue',prnt=False)
        for name in names[teamSizes[0]:]: #Assign second half of list to Red team
            self.players[name].setTeam('Red',prnt=False)
        self.players[names[0]].setSpymaster(prnt=False)
        self.players[names[teamSizes[0]]].setSpymaster(prnt=False)
        
    def __repr__(self):
        ret='\n'
        #List current round
        ret+="Round {0}: {1} team's turn\n\n".format(self.round,self.currentTeam)
        #List teams
        for t in ('Blue','Red'):
            ret+='{0} team ({1} words left):\n'.format(t,self.nRemaining[t])
            #List spymaster first
            for n,p in self.players.items():
                if p.team==t and p.spymaster:
                    ret+=n+' (spymaster)\n'
            #Then list other team members
            for n,p in self.players.items():
                if p.team==t and not p.spymaster:
                    ret+=n+'\n'
        ret+='\n'
        
        #Print grid of words
        colWid=max([len(x) for x in self.words])+1 #Width of a column, calculated as length of longest word length plus gap of 1
        i=1
        for word in self.words:
            if word in self.wordCats['Guessed']:
                ret+=word.lower()
            else:
                ret+=word
            if i%5==0: #Start new line after each 5 words
                ret+='\n'
            else:
                spaceLen=colWid-len(word)
                ret+=' '*spaceLen
            i+=1
            
        return(ret)
    
    
    def createHTMLBody(self,spymaster): #Create HTML string for status email
        
        ret='<html><body><p style= "font-family: Arial, Helvetica, sans-serif;">' #HTML set-up
        #List teams
        for t in ('Blue','Red'):
            ret+='<font color="{0}">{0} team ({1} words left):</font><br>'.format(t,self.nRemaining[t])
            #List spymaster first
            for n,p in self.players.items():
                if p.team==t and p.spymaster:
                    ret+=n+' (spymaster)<br>'
            #Then list other team members
            for n,p in self.players.items():
                if p.team==t and not p.spymaster:
                    ret+=n+'<br>'
        ret+='</p><p style= "font-family: Courier New, Courier, monospace;"><pre><b>' #New paragraph
        
        colWid=max([len(x) for x in self.words])+1 #Width of a column, calculated as length of longest word length plus gap of 1
        i=1
        for word in self.words:
            #Set color based on word
            if spymaster or word in self.wordCats['Guessed']: #Set color only for spymasters or words that have already been guessed          
                if word in self.wordCats['Blue']:
                    ret+='<font color="blue">'
                elif word in self.wordCats['Red']:
                    ret+='<font color="red">'
                elif word in self.wordCats['Assassin']:
                    ret+='<font color="black">'
                elif word in self.wordCats['Bystanders']:
                    ret+='<font color="chocolate">'
            else:
                ret+='<font color="black">'
            if word in self.wordCats['Guessed']: #Strikethrough words that have already been guessed
                ret+='<s>'+word+'</s>'
            else: 
                ret+=word #Add word
            if spymaster:
                ret+='</font>'
            
            if i%5==0: #Start new line after each 5 words
                ret+='<br>'
            else:
                spaceLen=colWid-len(word)
                ret+=' '*spaceLen
            i+=1
            
        ret+='</b></pre></p></body></html>' #HTML end
        
        return(ret)
    
    def emailGroup(self): #Send out email to group with current status
        for player in self.players.values():
            if self.completed: #At end of game, send out spymaster version of email to all players
                send_email(to=player.email,subject="{0} team wins".format(self.currentTeam),body=game.createHTMLBody(True))
            else: #At the start of each round, send out colour email to spymasters and b/w to other players
                send_email(to=player.email,subject="Codenames Round {0}: {1} team's turn".format(self.round,self.currentTeam),body=game.createHTMLBody(player.spymaster))
            
    def guess(self,word): #Guess a word and update game state accordingly
        word=word.upper() #Convert to upper case
        if word not in self.words: #Check if word is valid in game
            print('"{0}" was not recognised'.format(word))
            return(None)
        elif word in self.wordCats['Guessed']: #Check if word has already been guessed
            print('"{0}" has already been guessed'.format(word))
            return(None)
        else:
            self.wordCats['Guessed'].add(word) #Add word to set of guessed words
            #Check with category of word was chosen
            if word in self.wordCats['Assassin']:
                print('Assassin! {0} team loses'.format(self.currentTeam))
                self.endGame(otherTeam(self.currentTeam)) #Declare win for other team
            elif word in self.wordCats['Bystanders']:
                print("Unlucky, that was a bystander. End of {0} team's turn".format(self.currentTeam))
                self.nextRound()
            elif word in self.wordCats[self.currentTeam]:
                self.nRemaining[self.currentTeam]-=1
                print('Well done, you found a {0} spy'.format(self.currentTeam))
                if self.nRemaining[self.currentTeam]==0:
                    print('{0} team wins'.format(self.currentTeam))
                    self.endGame(self.currentTeam) #Declare win for team
            elif word in self.wordCats[otherTeam(self.currentTeam)]:
                self.nRemaining[otherTeam(self.currentTeam)]-=1
                print("Oops, you found a {0} spy. End of {1} team's turn".format(otherTeam(self.currentTeam),self.currentTeam))
                if self.nRemaining[otherTeam(self.currentTeam)]==0:
                    print('{0} team wins'.format(otherTeam(self.currentTeam)))
                    self.endGame(otherTeam(self.currentTeam)) #Declare win for other team
                else:
                    self.nextRound()
                
    def endGame(self,winner): #End game and declare a winner
        self.completed=True
        self.winningTeam=winner
        self.emailGroup()
                
    def nextRound(self): #End round and move on to next round
        self.round+=1 #Increment round counter
        self.currentTeam=otherTeam(self.currentTeam) #Swap turn to other team
        print(self)
        self.emailGroup()
        
    def play(self): #Enter 'input mode' to type in guesses
        if self.round==1: #At start of game, send out email
            self.emailGroup()
        if self.completed:
            print('Game already completed')
        print(self)
        while not self.completed:
            command=input("{0} team type a guess ('N' to go to next round, 'X' to exit game)\n".format(self.currentTeam))
            if command.upper()=='X':
                break
            elif command.upper()=='N':
                self.nextRound()
            else:
                self.guess(command)
            
        
        
game=Game(players=players,seed=3)
#print(game)
game.play()
#game.guess('OLYMPUS')
#game.guess('BILL')
#game.nextRound()
#game.emailGroup()
#send_email(to='simon.purkess+player1@gmail.com',subject='Another Test',body=game.createHTMLBody(False))

#Test email with HTML formatting
html="""
<html>
<body>
<p style= "font-family: Courier New, Courier, monospace;">
<pre>
<font color="chocolate">SHARK     <font color="red">BANK      <font color="red">HIMALAYAS <font color="chocolate">ROUND     <font color="blue">TAP<br><font color="chocolate">FALL      <font color="blue">CHOCOLATE <font color="black">ICE CREAM <font color="red">FORCE     <font color="blue">LIMOUSINE<br><font color="chocolate">STRAW     <font color="red">HORSESHOE <font color="red">BUCK      <font color="blue">WITCH     <font color="blue">GERMANY<br><font color="chocolate">COMIC     <font color="red">CIRCLE    <font color="chocolate">PUPIL     <font color="blue">CODE      <font color="red">NOVEL<br><font color="red">RABBIT    <font color="red">BAND      <font color="blue">MEXICO    <font color="blue">IRON      <font color="chocolate">CONCERT<br>
</pre>
</p>
</body>
</html>
"""

#send_email(to='simon.purkess+player1@gmail.com',subject='Color Test',body=html)