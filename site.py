class Site:
    def __init__(self, site_number):
        self.site_number = site_number
        self.store = dict() # {variable: value}
        self.initialize_store()

    def initialize_store(self):
        # even-indexed data is stored in all sites
        for i in range(2, 21, 2):
            self.store[i] = None

        # for odd-indexed data
        if self.site_number % 2 == 0:
            self.store[self.site_number - 1] = None
            self.store[self.site_number - 1 + 10] = None

    def display_store(self):
        all_variables = ""
        for variable, value in self.store.items():
            if not value is None:
                all_variables += "x" + str(variable) + ":" + " " + str(value) + ","
        all_variables = all_variables[:-1]
        print("site " + str(self.site_number) + " - " + all_variables)