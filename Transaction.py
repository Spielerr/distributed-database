class Transaction:
    def __init__(self, name: str, timestamp: int):
       
        self.name = name  
        self.startTime = timestamp  
        self.status = 'active'  # other possible states are 'waiting', 'aborted', 'committed'. maybe add enum
        
        self.dictAllOperations = {}  # {timestamp: ('r' or 'w', var, value or None)}
        self.readList = {}  # {timestamp: (variable name, list of sites where it was read from)} (for successful reads)
        self.writeList = {}  # {timestamp: (variable name, value, list of sites to be written to on commit)}
        
        # Dictionaries for waiting operations
        self.waitOnSiteRead = {}  # {site: timestamp of operation waiting for read}
        self.waitOnSiteWrite = {}  # {site: timestamp of operation waiting for write}

