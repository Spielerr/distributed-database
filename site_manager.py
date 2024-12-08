from site_module import Site


class SiteManager:
    def __init__(self):
        self.sites = []
        self.initialize_sites()
        self.waiting_read_operations = [] #[(variable, transaction_number, transaction_begin_timestamp), ...]

    def initialize_sites(self):
        """
        Create 10 sites and add them to the site list
        :return:
        """
        for i in range(0, 10):
            self.sites.append(Site(i))


    def return_value(self, variable, time, transaction):
        """
        Returns the value of the variable to the read operation
        :param variable: variable whose value to return
        :param time: transaction begin time which made the read request
        :param transaction: the transaction object which made the read request
        :return: (variable value, site number which provided the variable value) -> on success
                 (variable value, None) -> returning latest value as written by operation within the SAME transaction
                 (None, -1) -> when there are no relevant sites available, read request should wait
                 (None, -2) -> abort case because all relevant sites have failed since last commit
        """
        # check if the transaction had any writes before this read, if so, then return that
        # check if there were any writes to "variable" after "time"
        for write in transaction.write_operations[::-1]:
            if write[0] < time:
                break
            if write[0] > time and write[1] == variable:
                return write[2], None

        count_for_abort = 0
        for site in self.sites:
            if variable in site.store and self.return_read_mask_at_timestamp(site.read_mask[variable], transaction.begin_timestamp) == 1:
                if not site.live:
                    self.waiting_read_operations.append(
                        (variable, transaction.transaction_number, transaction.begin_timestamp))
                    return None, -1 # wait
                else:
                    for i in range(len(site.store[variable])):
                        if site.store[variable][i][0] > time:
                            return site.store[variable][i - 1][1], site.site_number
                    return site.store[variable][-1][1], site.site_number
            else:
                count_for_abort += 1

        if count_for_abort == 10:
            if variable % 2 == 0:
                return None, -2 # abort
            else:
                self.waiting_read_operations.append(
                    (variable, transaction.transaction_number, transaction.begin_timestamp))
                return None, -1 #wait


    def update_site(self, variable, value, update_timestamp, write_timestamp, transaction):
        """
        Update value of a variable across all sites if possible
        :param variable: variable whose value to update
        :param value: new value for the variable
        :param update_timestamp: current time when attempting to update the value (this is commit time of transaction)
        :param write_timestamp: time when the write operation was received by the transaction
        :param transaction: the transaction object which made the write request
        :return: true if update was successful, false otherwise
        """
        for site in self.sites:
            if write_timestamp < site.last_failed_timestamp < update_timestamp:
                #abort
                return False

        sites_affected = []
        for site in self.sites:
            if site.last_failed_timestamp < write_timestamp and (
                    site.last_failed_timestamp <= site.last_recovered_timestamp < write_timestamp):
                if variable in site.store:
                    site.store[variable].append((update_timestamp, value, transaction))
                    sites_affected.append(site)
                    if site.read_mask[variable][-1][0] == 0:
                        site.read_mask[variable].append((1, update_timestamp))
            elif site.last_failed_timestamp < write_timestamp < site.last_recovered_timestamp:
                # site is not live, no update
                continue

        if len(sites_affected) != 0:
            for site in sites_affected:
                print("Variable " + str(variable) + " in site " + str(site.site_number + 1) + " got affected by T" + str(transaction.transaction_number))

        return True

    def fail_site(self, site_number, timestamp):
        """
        Fail a site and update the read mask to notify that variables on this site cannot be read currently
        :param site_number: site number of the site to fail
        :param timestamp: time when fail command was received
        :return: None
        """
        self.sites[site_number].last_failed_timestamp = timestamp
        self.sites[site_number].fail_list.append(timestamp)
        self.sites[site_number ].live = False
        for i in range(2, 21, 2):  # setting read mask of all even numbered variables to 0
            self.sites[site_number].read_mask[i].append((0, timestamp))

    def recover_site(self, site_number, timestamp):
        """
        Recover a site from failure upon command and check if there are any waiting read operations dependent on this site
        :param site_number: site number of the site to be recovered
        :param timestamp: time when the recover command was received
        :return: None
        """
        self.sites[site_number].last_recovered_timestamp = timestamp
        self.sites[site_number].recovers_list.append(timestamp)
        self.sites[site_number].live = True

        # go through every waiting variable, check if it can be read from current site (using read mask)
        for waiting_op in self.waiting_read_operations:
            if waiting_op[0] in self.sites[site_number].store and self.return_read_mask_at_timestamp(self.sites[site_number].read_mask[waiting_op[0]], waiting_op[2]) == 1:
                print("Site " + str(site_number + 1) + " has recovered. Variable " + str(waiting_op[0]) + " value: " + str(self.sites[site_number].store[waiting_op[0]][-1][1]))

    def return_read_mask_at_timestamp(self, read_mask_list, begin_timestamp):
        """
        Return the value of the read mask at a given timestamp
        :param read_mask_list: the read mask list for a particular site
        :param begin_timestamp: the time when a transaction begun during which we wish to get the read mask value
        :return: read mask value -> 1 or 0 for being able to read or not respectively
        """
        for i in read_mask_list[::-1]:
            if i[1] < begin_timestamp:
                return i[0]

    def dump(self):
        """
        Display full information about all sites
        :return: None
        """
        for site in self.sites:
            site.display_store(site.live)
