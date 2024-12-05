from transaction import Transaction


def check_time_overlap(begin_time, begin_time2, end_time, end_time2):
    return not (end_time <= begin_time2 or end_time2 <= begin_time)

def common_write_operations(write_operations1, write_operations2):
    variables1 = {op[1] for op in write_operations1}
    variables2 = {op[1] for op in write_operations2}

    return not variables1.isdisjoint(variables2)

class TransactionManager:
    def __init__(self, site_manager):
        self.all_transactions = dict() # {transaction_number: Transaction obj}
        self.site_manager = site_manager
        self.graph = {} # {transaction : [transaction, ...]} contains only rw edges

    def begin_transaction(self, transaction_number: int, timestamp: int):
        # create new transaction object
        new_transaction = Transaction(transaction_number, timestamp)
        self.all_transactions[transaction_number] = new_transaction
        print("T" + str(transaction_number) + " begins")

    def add_write_operation(self, transaction_number: int, variable: int, value: int, timestamp: int):
        # fetch the transaction object
        self.all_transactions[transaction_number].write_operations.append((timestamp, variable, value))

    def add_read_operation(self, transaction_number: int, variable: int, timestamp: int):
        # fetch the transaction object
        ## TODO discuss - should only add to read_operations if the read is succesful 
        self.all_transactions[transaction_number].read_operations.append((timestamp, variable))
        # also print the value at the start of this transaction as requested by read
        transaction_begin_time = self.all_transactions[transaction_number].begin_timestamp
        value_read, from_site_number = self.site_manager.return_value(variable, transaction_begin_time)
        if value_read is not None:
            # if transaction successfuly reads then add to store_read of that var at that site
            self.site_manager.sites[from_site_number].store_read[variable].append(self.all_transactions[transaction_number])
            print("x" + str(variable) + ": " + str(
                self.site_manager.return_value(variable, transaction_begin_time)) + " read from site " + str(
                from_site_number) + " by transaction " + str(transaction_number))
        else:
            # TODO need to put transaction status should abort
            print("transaction " + str(transaction_number) + " that wants to read variable " + str(
                variable) + " cannot be read from any site atm")

    def end_transaction(self, transaction_number: int, timestamp: int):
        self.all_transactions[transaction_number].end_timestamp = timestamp

        if not self.transaction_has_all_reads(transaction_number):
            if self.transaction_is_first_committer(transaction_number) and self.update_transaction_values(transaction_number, timestamp):
                if self.check_graph(self.all_transactions[transaction_number], timestamp):
                    self.all_transactions[transaction_number].succeeded = True
                    # TODO : print where all transaction wrote?
                    print("T" + str(transaction_number) + " commits")
                    self.all_transactions[transaction_number].succeeded = True
                else:
                    # abort
                    print("T" + str(transaction_number) + " aborts")
                    self.remove_from_graph(self.all_transactions[transaction_number])
                    self.all_transactions[transaction_number].succeeded = False
            else:
                #abort
                print("T" + str(transaction_number) + " aborts")
                self.remove_from_graph(self.all_transactions[transaction_number])
                self.all_transactions[transaction_number].succeeded = False
        else:
            print("T" + str(transaction_number) + " commits")
            self.all_transactions[transaction_number].succeeded = True

    def transaction_has_all_reads(self, transaction_number: int):
        return not self.all_transactions[transaction_number].write_operations

    def transaction_is_first_committer(self, transaction_number: int):
        # gather all time overlapping transactions and check if they have succeeded
        begin_time = self.all_transactions[transaction_number].begin_timestamp
        end_time = self.all_transactions[transaction_number].end_timestamp
        for current_transaction_number, current_transaction in self.all_transactions.items():
            current_transaction_begin_time = current_transaction.begin_timestamp
            current_transaction_end_time = current_transaction.end_timestamp
            if (check_time_overlap(begin_time, current_transaction_begin_time, end_time, current_transaction_end_time) and
                    common_write_operations(self.all_transactions[transaction_number].write_operations, current_transaction.write_operations) and
                    current_transaction.succeeded):
                return False
        return True

    def update_transaction_values(self, transaction_number: int, timestamp: int):
        for new_write in self.all_transactions[transaction_number].write_operations:
            if not self.site_manager.update_site(new_write[1], new_write[2], timestamp, new_write[0]):
                return False
        return True

    def check_graph(self, transaction, end_timestamp):
        '''
        should only be called if first-committer and site-failue checks have been performed
        need to use - transaction, graph, read_store from variable, write_operations and read_operations
        '''
        buffer = []
        for ops in transaction.write_operations:
            variable_to_write = ops[1]
            for site in self.site_manager.sites:
                for trn in site.store_read[variable_to_write]:
                    if trn.begin_timestamp < end_timestamp:
                        if [trn, transaction] not in buffer:
                            buffer.append([trn, transaction])
                            if transaction in self.graph and len(self.graph[transaction]) > 0: # look upstream
                                print('transaction aborts due to rw edges')
                                return False # abort transaction
                            for key in self.graph:
                                if trn in self.graph[key]: # look downstream
                                    print('transaction aborts due to rw edges')
                                    return False # abort transaction
        
        for li in buffer:
            if li[0] not in self.graph:
                self.graph[li[0]] = [li[1]]
            else:
                self.graph[li[0]].append(li[1])
        return True # can commit
    

    def remove_from_graph(self, transaction):
        if transaction in self.graph:
            del self.graph[transaction]
        
        for key in self.graph:
            self.graph[key] = [item for item in self.graph[key] if item != transaction]
