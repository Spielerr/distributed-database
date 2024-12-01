'''
This is basically a Site
'''

from Variable import Variable

class DataManager:

    def __init__(self, name: int):
        
        self.name = name
        self.listVariables = self._initialize_variables(name)
        self.lastFailTimestamp = -1
        self.lastRecoveryTimestamp = -1
        self.readMask = {var: 1 for var in self.listVariables}  # 1 means that the var can be read, 0 othw
    

    # TODO Need to check
    def _initialize_variables(self, name: int) -> list:
        li = []
        for i in range(1, 21):
            if (i%2==0):
                li.append(Variable(i))
            if (name == 1+ i%10):
                li.append(Variable(i))  
        # print('In DataManager init: ', li)
        return li
    

    def checkStatus(self) -> bool:    # returns true if site is up, false othw
        if self.lastFailTimestamp > self.lastRecoveryTimestamp:
            return False
        else:
            return True
    
