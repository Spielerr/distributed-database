import re
from TransactionManager import TransactionManager
from SiteManager import SiteManager
from Transaction import Transaction

class MainManager:
    def __init__(self):
        self.site_manager = SiteManager()
        self.transaction_manager = TransactionManager(site_manager=self.site_manager)
        self.currentTime = 0

    def parse_commands(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                self.currentTime += 1

                line = line.strip()  # Remove leading/trailing whitespaces

                # Skip comments and empty lines
                if not line or line.startswith('//'):
                    continue

                # Match 'begin(T1)'
                if re.match(r'^begin\s*\(\s*(T\d+)\s*\)$', line, re.IGNORECASE):
                    transaction_name = re.findall(r'\d+', line)[0]  # Extract transaction number
                    print(f"Begin transaction: {transaction_name}")
                    transaction_name = int(transaction_name)
                    self.transaction_manager.begin_transaction(transaction_name, self.currentTime)
                
                # Match 'end(T1)'
                elif re.match(r'^end\s*\(\s*(T\d+)\s*\)$', line, re.IGNORECASE):
                    transaction_name = re.findall(r'\d+', line)[0]  # Extract transaction number
                    print(f"End transaction: {transaction_name}")

                # Match 'W(T1, x1, 101)'
                elif re.match(r'^w\s*\(\s*(T\d+)\s*,\s*(x\d+)\s*,\s*(\d+)\s*\)$', line, re.IGNORECASE):
                    numbers = re.findall(r'\d+', line)
                    transaction_name, variable_name, value = numbers  # Unpack into variables
                    transaction_name = int(transaction_name)
                    variable_name = int(variable_name)
                    value = int(value)
                    print(f"Write: Transaction {transaction_name} writes {value} to variable {variable_name}")
                    self.transaction_manager.update_transaction_writes(transaction_name, variable_name, value, self.currentTime)
                
                # Match 'R(T1, x1)'
                elif re.match(r'^r\s*\(\s*(T\d+)\s*,\s*(x\d+)\s*\)$', line, re.IGNORECASE):
                    transaction_name, variable_name = re.findall(r'\d+', line)
                    print(f"Read: Transaction {transaction_name} reads variable {variable_name}")

                # Match 'fail(2)'
                elif re.match(r'^fail\s*\(\s*(\d+)\s*\)$', line, re.IGNORECASE):
                    site_number = re.findall(r'\d+', line)[0]
                    print(f"Fail site: {site_number}")

                # Match 'recover(2)'
                elif re.match(r'^recover\s*\(\s*(\d+)\s*\)$', line, re.IGNORECASE):
                    site_number = re.findall(r'\d+', line)[0]
                    print(f"Recover site: {site_number}")

                # Match 'dump()'
                elif re.match(r'^dump\s*\(\s*\)$', line, re.IGNORECASE):
                    print("Dump operation")

                else:
                    print(f"Unknown command: {line}")



if __name__ == "__main__":
    main_manager_instance = MainManager()
    main_manager_instance.parse_commands('test.txt')
