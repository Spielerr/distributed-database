class Variable:

    def __init__(self, name: int):
        
        self.name = name # this is type int
        self.currentValue = name*10 # technically redundant
        self.lastCommitedTime = -1 # technically redundant
        self.valueHistory = {}    # [timestamp] = (value, transaction name), i think timestamp is commit time of the transaction
        self.readHistory = {}     # [timestamp] = (transaction name)
        self.listTimeStamps = []  # technically redundant
    

