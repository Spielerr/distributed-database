class Transaction:
    def __init__(self, transaction_number: int, timestamp: int):
        self.transaction_number = transaction_number
        self.begin_timestamp = timestamp
        self.end_timestamp = -1 # should be set when a transaction ends
        self.read_operations = [] # [(timestamp, variable), ...]
        self.write_operations = [] # [(timestamp, variable, value), ...]
        self.succeeded = False # True if transaction goes through, remains False if aborted
