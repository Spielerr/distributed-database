class Site:
    def __init__(self, site_number):
        self.site_number = site_number # 0, 1, 2, ... 9
        self.store = dict() # {variable: [(timestamp, value, transaction), ...]}
        self.store_read = {} # {variable: [transaction, ...]}
        self.read_mask = {}  # {variable: [(0 or 1, timestamp)]} 0 means cannot read, 1 can
        self.initialize_store()
        self.last_failed_timestamp = 0
        self.last_recovered_timestamp = 0
        self.fail_list = [] # stores all timestamps when a site fails
        self.recovers_list = [] # stores all timestamps when a site recovers
        self.live = True

    def initialize_store(self):
        """
        Initialize the store for each site with the corresponding variables that are mapped as per the requirements
        :return: None
        """
        # even-indexed data is stored in all sites
        for i in range(2, 21, 2):
            self.store[i] = [(0, i * 10, 'begin state')]

        # for odd-indexed data
        if self.site_number % 2 != 0:
            self.store[self.site_number] = [(0, self.site_number * 10, 'begin state')]
            self.store[self.site_number + 10] = [(0, (self.site_number + 10) * 10, 'begin state')]

        # initially, can read from all sites which are up by default
        for key in self.store:
            self.read_mask[key] = [(1,0)]

        # store all the reads on this site
        for key in self.store:
            self.store_read[key] = []

    def display_store(self, is_live):
        """
        Display all variables stored in the site, called by the dump function
        :param is_live: is the site live or not
        :return: None
        """
        all_variables = ""
        for variable, value in sorted(self.store.items()):
            all_variables += "x" + str(variable) + ":" + " " + str(value[-1][1]) + ","
        all_variables = all_variables[:-1]
        if not is_live:
            print("site " + str(self.site_number + 1) + " - " + all_variables + " (site not live, showing values from time when it was last live)")
        else:
            print("site " + str(self.site_number + 1) + " - " + all_variables)
