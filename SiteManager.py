from DataManager import DataManager

class SiteManager:
    def __init__(self):
        self.listDataManagers = self._initialize_DataManagers()
        self.listOfCurrentlyFailedSites = []   
        self.listOfCurrentlyAvailableSites = self.listDataManagers.copy() # this should technically copy the object references

    def _initialize_DataManagers(self) -> list:
        li = []
        for i in range(1, 11):
            li.append(DataManager(i)) 
        # print('In SiteManager init: ', li)
        return li
    
    def failSite(self, site: 'DataManager', timestamp: int):
        site.lastFailTimestamp = timestamp
        
        for i in range(len(self.listOfCurrentlyAvailableSites)):
            if site.name == self.listOfCurrentlyAvailableSites[i].name:
                self.listOfCurrentlyAvailableSites.remove(site) 

        flag = 0
        for i in range(len(self.listOfCurrentlyFailedSites)):
            if site.name == self.listOfCurrentlyFailedSites[i].name:
                flag = 1
        if flag ==0:
            self.listOfCurrentlyFailedSites.append(site) 
        
    
    def recoverSite(self, site: 'DataManager', timestamp: int):
        site.lastRecoveryTimestamp = timestamp
        
        for i in range(len(self.listOfCurrentlyFailedSites)):
            if site.name == self.listOfCurrentlyFailedSites[i].name:
                self.listOfCurrentlyFailedSites.remove(site) 

        flag = 0
        for i in range(len(self.listOfCurrentlyAvailableSites)):
            if site.name == self.listOfCurrentlyAvailableSites[i].name:
                flag = 1
        if flag ==0:
            self.listOfCurrentlyAvailableSites.append(site) 
