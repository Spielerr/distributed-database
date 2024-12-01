from SiteManager import SiteManager
from Transaction import Transaction

class TransactionManager:
    def __init__(self, site_manager : 'SiteManager'):
        # Initialize the dictionaries to track transactions in different states
        self.activeTransactions = {}  # {Transaction: timestamp started}
        self.abortedTransactions = {}  # {Transaction: (timestamp started, timestamp aborted)}
        self.waitingTransactions = {}  # {Transaction: (timestamp started, timestamp started waiting)}
        self.committedTransactions = {}  # {TransactionName: (timestamp started, timestamp committed)}
        self.site_manager = site_manager



    def begin_transaction(self, name : int, currentTime : int):
        new_transaction =  Transaction(name, currentTime)

        self.activeTransactions[new_transaction] = currentTime
        print(f"Transaction {new_transaction.name} started at time {currentTime}")


    def update_transaction_writes(self, name : int, variable_name : int, value : int, currentTime : int):
        transaction = None
        for t in self.activeTransactions:
            if name == t.name:
                transaction = t
        transaction.dictAllOperations[currentTime] = ('w', variable_name, value)

        # Need to check whether we need to check which sites are up now or at commit time
        site_list = []
        for site in self.site_manager.listDataManagers:
            for variable in site.listVariables:
                # print(variable.name)
                if variable_name == variable.name:
                    site_list.append(site.name)

        transaction.writeList[currentTime] = (variable_name, value, site_list)
        print(f"In update_transaction_writes : ", transaction.writeList[currentTime])


    # def transaction_read():


    # def transaction_end():

    #     ## Writes

    #     # Check if site failed between write and commit then abort

    #     # Check first committer rule 

