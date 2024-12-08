import re

from site_manager import SiteManager
from transaction_manager import TransactionManager

"""
Authors: Karan Kumar Gangadhar and Aryaman Shaan

This file parses input and calls relevant functions to process each of the different types of expected input
"""

"""
This is the main class initializing two objects - site manager and transaction manager
It also keeps track of the current time, which gets incremented with every line of the input
"""
class MainManager:
    def __init__(self):
        self.site_manager = SiteManager()
        self.transaction_manager = TransactionManager(self.site_manager)
        self.current_time = 0


    def run(self):
        """
        Takes in input from user through command line
        """
        print("Transaction Management System. Type 'exit' to quit.")
        while True:
            try:
                line = input().strip()
                if line.lower() == 'exit':
                    break
                if not line or line.startswith('//'):
                    continue

                # Remove inline comments
                line = line.split('//')[0].strip()

                if not line:
                    continue

                self.current_time += 1
                self.parse_input(line)
            except EOFError:
                break
            except Exception as e:
                print(f"Error processing input: {e}")


    def parse_input(self, line):
        """
        Uses regex to match various kinds of input and accordingly call the corresponding function in transaction and site managers

        :param line: each line as inputted by the user
        """
        # Match 'begin(T1)'
        if re.match(r'^begin\s*\(\s*(T\d+)\s*\)$', line, re.IGNORECASE):
            transaction_number = int(re.findall(r'\d+', line)[0])
            self.transaction_manager.begin_transaction(transaction_number, self.current_time)

        # Match 'end(T1)'
        elif re.match(r'^end\s*\(\s*(T\d+)\s*\)$', line, re.IGNORECASE):
            transaction_number = int(re.findall(r'\d+', line)[0])
            self.transaction_manager.end_transaction(transaction_number, self.current_time)

        # Match 'W(T1, x1, 101)'
        elif re.match(r'^w\s*\(\s*(T\d+)\s*,\s*(x\d+)\s*,\s*(\d+)\s*\)$', line, re.IGNORECASE):
            params = re.findall(r'\d+', line)
            transaction_number, variable_id, value = params  # Unpack into variables
            transaction_number = int(transaction_number)
            variable_id = int(variable_id)
            value = int(value)
            self.transaction_manager.add_write_operation(transaction_number, variable_id, value, self.current_time)

        # Match 'R(T1, x1)'
        elif re.match(r'^r\s*\(\s*(T\d+)\s*,\s*(x\d+)\s*\)$', line, re.IGNORECASE):
            transaction_number, variable_id = re.findall(r'\d+', line)
            transaction_number = int(transaction_number)
            variable_id = int(variable_id)
            self.transaction_manager.add_read_operation(transaction_number, variable_id, self.current_time)

        # Match 'fail(2)'
        elif re.match(r'^fail\s*\(\s*(\d+)\s*\)$', line, re.IGNORECASE):
            site_number = re.findall(r'\d+', line)[0]
            site_number = int(site_number) - 1
            self.site_manager.fail_site(site_number, self.current_time)

        # Match 'recover(2)'
        elif re.match(r'^recover\s*\(\s*(\d+)\s*\)$', line, re.IGNORECASE):
            site_number = re.findall(r'\d+', line)[0]
            site_number = int(site_number) - 1
            self.site_manager.recover_site(site_number, self.current_time)

        # Match 'dump()'
        elif re.match(r'^dump\s*\(\s*\)$', line, re.IGNORECASE):
            self.site_manager.dump()

        else:
            print(f"Unknown command: {line}")


if __name__ == "__main__":
    main_manager = MainManager()
    main_manager.run()
