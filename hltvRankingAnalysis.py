# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 19:44:39 2019

@author: Nicolas
"""
import cfscrape
from bs4 import BeautifulSoup
import json
import datetime
import time
from collections import defaultdict 

    
class HLTVTopsList:
    def __init__(self, startDate="2015-10-1", endDate=str(datetime.date.today())):
        self.startDate = startDate
        self.endDate = endDate                
        self.tops = None
    
    def getDate(self):
        return (self.startDate,self.endDate)
    
    def getTopsDates(self):
        return (self.tops[0].date,self.tops[-1].date)
    
    def isCompleted(self):
        if self.tops == None:
            return False
        else:
            return True
        
    def getTeams(self):
        listTeams=[]
        for t in self.tops:
            listTeams += t.getTeams()
        listTeams = list(dict.fromkeys(listTeams))
        listTeams.sort(key=lambda s: s.casefold())
        return listTeams
        
    def getPlayers(self):
        listPlayers=[]
        for t in self.tops:
            listPlayers += t.getPlayers()
        listPlayers = list(dict.fromkeys(listPlayers))
        listPlayers.sort(key=lambda s: s.casefold())
        return listPlayers
    
    def getCountries(self):
        listCountries=[]
        for t in self.tops:
            listCountries += t.getCountries()
        listCountries = list(dict.fromkeys(listCountries))
        listCountries.sort(key=lambda s: s.casefold())
        return listCountries

    def download(self):
        if self.isCompleted():
            print("Already downloaded")
        else:
            listTops = []  
            print("Start downloading : " + self.startDate + " to " + self.endDate)
            date = datetime.date(*list(map(int, self.startDate.split("-"))))
            while datetime.date(*list(map(int, self.endDate.split("-")))) >= date: 
                top = HLTVTop(date.year,date.month,date.day)
                response = top.download()
                while (response==False and datetime.date(*list(map(int, self.endDate.split("-")))) > date):
                    print("Pas de classement : "+ str(date))
                    date += datetime.timedelta(days=1)
                    top = HLTVTop(date.year,date.month,date.day)
                    response = top.download()
                    time.sleep(1)
                if datetime.date(*list(map(int, self.endDate.split("-")))) >= date: 
                    if  response==True:
                        listTops.append(top) 
                        print("Classement : "+ str(date))
                    date += datetime.timedelta(days=4)
                    time.sleep(1)
            
            print("Download finished")
            self.tops = listTops
    
    def save(self,filename):
        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(self,outfile, ensure_ascii=False, indent=2,default=lambda o: o.__dict__)
            print("Saved " + filename)
        
    
        
    @staticmethod
    def getObjectFromFile(filename):
        with open(filename, encoding='utf-8') as data_file:
            data = json.loads(data_file.read())
            return HLTVTopsList(data["startDate"],data["endDate"])
                
            
            
    def fromFile(self, filename):
        with open(filename, encoding='utf-8') as data_file:
            data = json.loads(data_file.read())
            if(datetime.date(*list(map(int,data["startDate"].split("-")))) <= datetime.date(*list(map(int, self.startDate.split("-")))) and datetime.date(*list(map(int,data["endDate"].split("-")))) >= datetime.date(*list(map(int, self.endDate.split("-"))))):
                topsHLTV = []
                for d in data["tops"]:
                    if (datetime.date(*list(map(int,  d["date"].split("-")))) >= datetime.date(*list(map(int, self.startDate.split("-")))) and datetime.date(*list(map(int,  d["date"].split("-")))) <= datetime.date(*list(map(int, self.endDate.split("-"))))):
                        topHLTV = []
                        for e in d["top"]:
                            playerList = []
                            for f in e["team"]["playerList"]:
                                playerList.append(Player(f["name"],f["country"]))
                            topHLTV.append(HLTVTeamScore(e["pos"],e["points"],Team(e["team"]["name"],playerList)))
                        topsHLTV.append(HLTVTop(*list(map(int,  d["date"].split("-"))),topHLTV))
                self.tops = topsHLTV
            else:
                startDate = self.startDate
                endDate = self.endDate
                if(datetime.date(*list(map(int,data["startDate"].split("-")))) > datetime.date(*list(map(int, self.startDate.split("-"))))) :
                    startDate = data["startDate"]
                if(datetime.date(*list(map(int,data["endDate"].split("-")))) < datetime.date(*list(map(int, self.endDate.split("-"))))):
                    endDate = data["endDate"]
                print("ERROR : The file don't have every ranking for this dates. Create a new HLTVTopsList object with this dates : " + startDate + " to " + endDate + " or download it")
               
               
    def update(self,newStartDate="2015-10-1",newEndDate=str(datetime.date.today())):
        if self.isCompleted():
            if(datetime.date(*list(map(int,newStartDate.split("-")))) < datetime.date(*list(map(int,self.startDate.split("-"))))):
                newStartListTops = [] 
                print("Start downloading : " + newStartDate + " to " + self.startDate)
                date = datetime.date(*list(map(int, newStartDate.split("-"))))
                while datetime.date(*list(map(int, self.startDate.split("-")))) > date: 
                    print(date)
                    top = HLTVTop(date.year,date.month,date.day)
                    response = top.download()
                    while (response==False and datetime.date(*list(map(int, self.startDate.split("-")))) > date):
                        print("Pas de classement : "+ str(date))
                        date += datetime.timedelta(days=1)
                        top = HLTVTop(date.year,date.month,date.day)
                        response = top.download()
                        time.sleep(1)
                    if datetime.date(*list(map(int, self.startDate.split("-")))) > date: 
                        if  response==True:
                            newStartListTops.append(top) 
                            print("Classement : "+ str(date))
                        date += datetime.timedelta(days=4)
                        time.sleep(1)
                self.tops = newStartListTops + self.tops
                print("Download finished")
                    
            if(datetime.date(*list(map(int,newEndDate.split("-")))) > datetime.date(*list(map(int,self.endDate.split("-"))))):
                newEndListTops = [] 
                print("Start downloading : " + self.endDate + " to " + newEndDate)
                date = datetime.date(*list(map(int, self.endDate.split("-")))) + datetime.timedelta(days=1)
                while datetime.date(*list(map(int, newEndDate.split("-")))) >= date: 
                    top = HLTVTop(date.year,date.month,date.day)
                    response = top.download()
                    while (response==False and datetime.date(*list(map(int, newEndDate.split("-")))) > date):
                        print("Pas de classement : "+ str(date))
                        date += datetime.timedelta(days=1)
                        top = HLTVTop(date.year,date.month,date.day)
                        response = top.download()
                        time.sleep(1)
                    if datetime.date(*list(map(int, newEndDate.split("-")))) >= date: 
                        if  response==True:
                            newEndListTops.append(top) 
                            print("Classement : "+ str(date))
                        date += datetime.timedelta(days=4)
                        time.sleep(1)
                self.tops = self.tops + newEndListTops
                print("Download finished")
            
            for top in self.tops:
                if (datetime.date(*list(map(int,top.date.split("-")))) < datetime.date(*list(map(int,newStartDate.split("-")))) or datetime.date(*list(map(int,top.date.split("-")))) > datetime.date(*list(map(int,newEndDate.split("-"))))):
                    self.tops.remove(top)
            
            self.startDate= self.tops[0].date
            self.endDate= self.tops[-1].date
        else:
            print("ERROR : HLTVTopsList object is empty. Use download() or fromFile() at first.")
            
    def trackTeam(self,team):
        teamTops = []
        for top in self.tops:
            teamTops.append(top.trackTeam(team))
        return teamTops
    
    def trackPlayer(self,player):
        playerTops=[]
        for top in self.tops:
            playerTops.append(top.trackPlayer(player))
        return playerTops
        
    def trackCountry(self,country,nbMin):
        playerTops=[]
        for top in self.tops:
            playerTops.append(top.trackCountry(country,nbMin))
        return playerTops
            
        
        
class HLTVTop:
    month = ["january","february","march","april","may","june","july","august","september","october","november","december"]
    def __init__(self,y,m,d,top=None):
        self.date = str(y) + "-" + str(m) + "-" +str(d)
        self.url = "https://www.hltv.org/ranking/teams/"+str(y)+"/"+self.month[m-1]+"/"+str(d)
        self.top = top
        
    def isValid(self):
        scraper = cfscrape.create_scraper()
        r = scraper.get(self.url).content
        soup = BeautifulSoup(r, 'html.parser')
        spanName = soup.find_all("span", class_="name")
        if(len(spanName) > 1):
            return (True,soup)
        else:
            return (False,)
        
    def getTeams(self):
        listTeams = []
        for t in self.top:
            listTeams.append(t.team.name)
        return listTeams
        
    def getPlayers(self):
        listPlayers = []
        for t in self.top:
            listPlayers += t.team.getPlayers()
        return listPlayers
    
    def getCountries(self):
        listCountries = []
        for t in self.top:
            listCountries += t.team.getCountries()
        return listCountries
            
    def findByPos(self,pos):
        for x in self.top:
            if x.pos == pos:
                    return x
        return None
            
    def trackTeam(self,team):
        for teamScore in self.top:
            if teamScore.team.name == team:
                return (self.date,teamScore)
        return (self.date,None)
        
    def trackPlayer(self,player):
        for teamScore in self.top:
            for playerL in teamScore.team.playerList:
                if playerL.name == player:
                    return (self.date,teamScore)
        return (self.date,None)
            
    def trackCountry(self,country,nbMin=1):
        countryTop=[]
        for teamScore in self.top:
            countryList = teamScore.team.country(nbMin)
            if(country in countryList):
                countryTop.append(teamScore)

        if len(countryTop) == 0:
            return (self.date,None)
        else:
            return (self.date,countryTop)
      
            
    def isDownloaded(self):
        if self.top == None:
            return False
        else:
            return True
        
    def download(self):
        result = self.isValid()
        if(result[0]):
            soup = result[1]
            spanName = soup.find_all("span", class_="name")
            spanPoints = soup.find_all("span", class_="points")
            spanAllTeam =  soup.find_all("table", class_="lineup")
            topHLTV = []
            for key,spanTeam in enumerate(spanAllTeam):
                playerList = []
                for spanPlayer in spanTeam.find_all("div", class_="nick"):
                     playerList.append(Player(spanPlayer.contents[1],spanPlayer.contents[0]['title']))
                topHLTV.append(HLTVTeamScore(key+1,spanPoints[key].string[1:].replace(" points)", ""),Team(spanName[key].string,playerList)))
            self.top = topHLTV
            return True
        else:
            return False
            
      
class HLTVTeamScore:
    def __init__(self,pos,points,team):
        self.pos = pos
        self.points = points
        self.team = team
        
class Team:
    def __init__(self,name,playerList):
        self.name = name
        self.playerList = playerList
        
    def country(self,nbMin):
        countCountry = defaultdict(int)
        country = []
        for player in self.playerList:
            countCountry[player.country] += 1
        for item in countCountry.items():
            if(item[1] >= nbMin):
                country.append(item[0])
        return country
    
    def getPlayers(self):
        listPlayers = []
        for t in self.playerList:
            listPlayers.append(t.name)
        return listPlayers
    
    def getCountries(self):
        listCountries = []
        for t in self.playerList:
            listCountries.append(t.country)
        return listCountries
        
class Player:
    def __init__(self,name,country):
        self.name = name
        self.country = country
        

