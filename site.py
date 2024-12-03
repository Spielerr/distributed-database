class Site:
    def __init__(self, site_number):
        self.site_number = site_number
        self.store = dict() # {variable: [(timestamp, value), ...]}
        self.initialize_store()
        self.last_failed_timestamp = None
        self.last_recovered_timestamp = None
        self.live = True

    def initialize_store(self):
        # even-indexed data is stored in all sites
        for i in range(2, 21, 2):
            self.store[i] = [(0, i * 10)]

        # for odd-indexed data
        if self.site_number % 2 == 0:
            self.store[self.site_number - 1] = [(0, (self.site_number - 1) * 10)]
            self.store[self.site_number - 1 + 10] = [(0, (self.site_number - 1 + 10) * 10)]

    def display_store(self):
        all_variables = ""
        for variable, value in sorted(self.store.items()):
            all_variables += "x" + str(variable) + ":" + " " + str(value[-1][1]) + ","
        all_variables = all_variables[:-1]
        print("site " + str(self.site_number) + " - " + all_variables)
