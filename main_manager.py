import re

from site_manager import SiteManager
from transaction_manager import TransactionManager

class MainManager:
    def __init__(self):
        self.site_manager = SiteManager()
        self.transaction_manager = TransactionManager(self.site_manager)
        self.current_time = 0

    def parse_input(self, file_path):
         with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespaces

                # # Skip comments and empty lines
                # if not line or line.startswith('//'):
                #     continue
                # Remove inline comments (everything after //)
                line = line.split('//')[0].strip()

                # Skip comments and empty lines
                if not line:
                    continue

                self.current_time += 1

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
    main_manager.parse_input("tests/test18.txt")
