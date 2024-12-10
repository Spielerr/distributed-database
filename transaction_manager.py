"""
Authors for all functions: Karan Kumar Gangadhar and Aryaman Shaan jointly

This file defines all transaction operations functions
"""


from transaction import Transaction


def check_time_overlap(begin_time, begin_time2, end_time, end_time2):
    """
    Check overlap between two given time ranges

    :param begin_time: begin time for the first time range
    :param begin_time2: begin time for the second time range
    :param end_time: end time for the first time range
    :param end_time2: end time for the second time range
    :return: true if there exists an overlap, false otherwise
    """
    return not (end_time <= begin_time2 or end_time2 <= begin_time)

def common_write_operations(write_operations1, write_operations2):
    """
    Find if there are common write operations in the given two write operations lists

    :param write_operations1: first list of write operations
    :param write_operations2: second list of write operations
    :return: true if there are common write operations in the given two write operations lists, false otherwise
    """
    variables1 = {op[1] for op in write_operations1}
    variables2 = {op[1] for op in write_operations2}

    return not variables1.isdisjoint(variables2)

class TransactionManager:
    def __init__(self, site_manager):
        self.all_transactions = dict() # {transaction_number: Transaction obj}
        self.site_manager = site_manager
        self.graph = {} # {transaction: [(transaction, 'rw' or 'wr' or 'ww'), ...]}


    def begin_transaction(self, transaction_number: int, timestamp: int):
        """
        Create a new transaction and add it the all_transactions dictionary
        :param transaction_number: transaction number as inputted
        :param timestamp: time when transaction begins
        :return: None
        """
        new_transaction = Transaction(transaction_number, timestamp)
        self.all_transactions[transaction_number] = new_transaction
        print("T" + str(transaction_number) + " begins")


    def add_write_operation(self, transaction_number: int, variable: int, value: int, timestamp: int):
        """
        Add a write operation to the transaction
        :param transaction_number: transaction number as inputted
        :param variable: variable which is being written
        :param value: value for the variable
        :param timestamp: time when write operation was received
        :return: None
        """
        self.all_transactions[transaction_number].write_operations.append((timestamp, variable, value))


    def add_read_operation(self, transaction_number: int, variable: int, timestamp: int):
        """
        Add a read operation to the transaction
        :param transaction_number: transaction number as inputted
        :param variable: variable which is being read
        :param timestamp: time when read operation was received
        :return: None
        """
        self.all_transactions[transaction_number].read_operations.append((timestamp, variable))
        transaction_begin_time = self.all_transactions[transaction_number].begin_timestamp

        value_read, from_site_number = self.site_manager.return_value(variable, transaction_begin_time, self.all_transactions[transaction_number])
        if value_read is not None and from_site_number is not None:
            self.site_manager.sites[from_site_number].store_read[variable].append(self.all_transactions[transaction_number])
            print("x" + str(variable) + ": " + str(value_read) + " read from site " + str(
                from_site_number + 1) + " by transaction " + str(transaction_number))
        elif value_read is not None:
            print("x" + str(variable) + ": " + str(value_read) + " (from the same transaction)")
        elif from_site_number is not None:
            if from_site_number == -1:
                print("T" + str(transaction_number) + " that wants to read variable " + str(
                    variable) + " cannot be read from any site at the moment")
            elif from_site_number == -2:
                print("T" + str(transaction_number) + " aborts")
                self.remove_from_graph(self.all_transactions[transaction_number])
                self.all_transactions[transaction_number].succeeded = False


    def end_transaction(self, transaction_number: int, timestamp: int):
        """
        Process end of a transaction, commit or abort accordingly
        :param transaction_number: transaction number as inputted
        :param timestamp: commit time for the transaction
        :return: None
        """
        self.all_transactions[transaction_number].end_timestamp = timestamp

        # update the waiting_read_operations list - remove all waiting operations on this transaction (end of lifespan oops)
        for write in self.site_manager.waiting_read_operations:
            self.site_manager.waiting_read_operations = [t for t in self.site_manager.waiting_read_operations if t[1] != transaction_number]

        if not self.transaction_has_all_reads(transaction_number):
            if (self.transaction_is_first_committer(transaction_number) and
                    self.check_and_update_graph(self.all_transactions[transaction_number], timestamp) and
                    self.update_transaction_values(transaction_number, timestamp)):
                self.all_transactions[transaction_number].succeeded = True
                print("T" + str(transaction_number) + " commits")
                self.all_transactions[transaction_number].succeeded = True
            else:
                #abort
                print("T" + str(transaction_number) + " aborts")
                self.remove_from_graph(self.all_transactions[transaction_number])
                self.all_transactions[transaction_number].succeeded = False
        else:
            print("T" + str(transaction_number) + " commits")
            self.all_transactions[transaction_number].succeeded = True


    def transaction_has_all_reads(self, transaction_number: int):
        """
        Determine if all operations in the transaction are reads
        :param transaction_number: transaction number as inputted
        :return: true if transaction only has reads and no writes, false otherwise
        """
        return not self.all_transactions[transaction_number].write_operations

    def transaction_is_first_committer(self, transaction_number: int):
        """
        Determine if the transaction is the first committer
        :param transaction_number: transaction number of transaction under consideration
        :return: true if transaction is first committer, false otherwise
        """
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
        """
        Update all values for a single transaction according to all write operations as included in the transaction
        :param transaction_number: transaction number as inputted
        :param timestamp: time when this update has to happen (which is the commit time)
        :return: true if update succeeded, false otherwise
        """
        for new_write in self.all_transactions[transaction_number].write_operations:
            if not self.site_manager.update_site(new_write[1], new_write[2], timestamp, new_write[0], self.all_transactions[transaction_number]):
                return False
        return True

    def check_and_update_graph(self, transaction, end_timestamp):
        """
        Find cycles in the synchronization graph
        :param transaction: current transaction for which the graph data structure should be updated
        :param end_timestamp: commit time for the transaction
        :return: true if there are no cycles and the transaction can commit, false otherwise
        """
        # populate graph
        buffer = []  # helps to populate graph
        for ops in transaction.write_operations:
            variable_to_write = ops[1]
            for site in self.site_manager.sites:
                if variable_to_write in site.store_read:
                    for trn in site.store_read[variable_to_write]:
                        if trn.begin_timestamp < end_timestamp:  # adding rw edge
                            if [trn, transaction, 'rw'] not in buffer:
                                buffer.append([trn, transaction, 'rw'])
                if variable_to_write in site.store:
                    for tuple in site.store[variable_to_write]:
                        if tuple[2] == 'begin state':
                            continue
                        trn = tuple[2]
                        if trn.end_timestamp < transaction.begin_timestamp:  # adding ww edge
                            if [trn, transaction, 'ww'] not in buffer:
                                buffer.append([trn, transaction, 'ww'])
        for ops in transaction.read_operations:
            variable_to_read = ops[1]
            for site in self.site_manager.sites:
                if variable_to_read in site.store:
                    for tuple in site.store[variable_to_read]:
                        if tuple[2] == 'begin state':
                            continue
                        trn = tuple[2]
                        if trn.end_timestamp < transaction.begin_timestamp:  # adding wr edge
                            if [trn, transaction, 'wr'] not in buffer:
                                buffer.append([trn, transaction, 'wr'])

        for li in buffer:
            if li[0] not in self.graph:
                self.graph[li[0]] = [(li[1], li[2])]
            else:
                if (li[1], li[2]) not in self.graph[li[0]]:
                    self.graph[li[0]].append((li[1], li[2]))

        # do modified dfs to find all cycles that start from transaction
        all_cycles = self.find_cycles((transaction, 'origin'))

        for cycle in all_cycles:
            count = 0
            # abort on two consecutive rw edges in the cycle
            for i in range(len(cycle) - 1):
                if cycle[i][1] == 'rw' and cycle[i + 1][1] == 'rw':
                    print('2 consecutive rw edges detected - transaction aborts due to rw edges cycle')
                    return False

        return True  # can commit

    def find_cycles(self, start_vertex):
        """
        Find all cycles in the graph from a starting vertex
        :param start_vertex: origin node to determine cycles from
        :return: all cycles in the graph
        """
        path = []  # Stack to store the current path
        visited_in_path = set()  # Track visited vertices in the current path
        all_cycles = []  # List to store detected cycles

        def dfs(current_vertex):
            path.append(current_vertex)
            visited_in_path.add(current_vertex)

            if current_vertex[0] in self.graph:
                for neighbor in self.graph[current_vertex[0]]:
                    if neighbor[0] == start_vertex[0]:  # Cycle detected
                        all_cycles.append(path.copy())
                        all_cycles[-1].append(neighbor)
                    elif neighbor not in visited_in_path:
                        dfs(neighbor)

            path.pop()  # Backtrack
            visited_in_path.remove(current_vertex)

        dfs(start_vertex)
        return all_cycles

    def remove_from_graph(self, transaction):
        """
        Update the graph data structure whenever there are any aborted transactions
        :param transaction: the aborted transaction
        :return: None
        """
        if transaction in self.graph:
            del self.graph[transaction]

        for key in self.graph:
            self.graph[key] = [item for item in self.graph[key] if item[0] != transaction]
