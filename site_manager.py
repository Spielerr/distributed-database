from site_module import Site


class SiteManager:
    def __init__(self):
        self.sites = []
        self.initialize_sites()

    def initialize_sites(self):
        for i in range(1, 11):
            self.sites.append(Site(i))

    '''
    TODO: Add code here to determine if site containing the variable has failed since last committed time
    check last failed timestamp for the site
    check last value in site's store and fetch the timestamp, that is the last committed timestamp
    '''

    def check_failure_since_last_commit(self, site, variable):
        """
        Returns true if site did not fail between these time and variable's last commit at the site
        else returns false
        """
        last_commit_time_on_var = site.store[variable][-1][0]
        if site.last_failed_timestamp > last_commit_time_on_var:
            return False
        return True

    '''
    TODO: Also add code making sure a site which has recovered doesn't have it's variables open to reading,
    but only to writing, so that logic needs to come in this function. Based on this excerpt:
    "Upon recovery of a site s, all non-replicated variables are available for reads and writes. 
    Regarding replicated variables, the site makes them available for writing, but not reading for 
    transactions that begin after the recovery until a commit has happened. In fact, a read from a transaction that
    begins after the recovery of site s for a replicated variable x will not be
    allowed at s until a committed write to x takes place on s."
    '''
    def return_value(self, variable, time):
        for site in self.sites:
            if site.live and variable in site.store:
                if site.read_mask[variable] == 0:
                    continue
                if variable % 2 == 0 and not self.check_failure_since_last_commit(site, variable):
                    continue
                for i in range(len(site.store[variable])):
                    if site.store[variable][i][0] > time:
                        return site.store[variable][i - 1][1], site.site_number
                return site.store[variable][-1][1], site.site_number  # added the site_number to be returned as well
        return None, None # transaction should be put on wait or aborted or whatever

        # if read failed and we have exited out of the for loop, then need to WAIT

    def update_site(self, variable, value, update_timestamp, write_timestamp):
        for site in self.sites:
            if write_timestamp < site.last_failed_timestamp < update_timestamp:
                #abort
                return False

        for site in self.sites:
            if site.last_failed_timestamp < write_timestamp and (
                    site.last_failed_timestamp <= site.last_recovered_timestamp < write_timestamp):
                if variable in site.store:
                    site.store[variable].append((update_timestamp, value))
                    if site.read_mask[variable] == 0:
                        site.read_mask[variable] = 1
            elif site.last_failed_timestamp < write_timestamp < site.last_recovered_timestamp:
                # site is not live, no update
                continue

        return True

        # if write failed and we have exited out of the for loop, then need to WAIT

    def fail_site(self, site_number, timestamp):
        self.sites[site_number].last_failed_timestamp = timestamp
        self.sites[site_number].live = False
        for i in range(2, 21, 2):  # setting read mask of all even numbered variables to 0
            self.sites[site_number].read_mask[i] = 0

    def recover_site(self, site_number, timestamp):
        self.sites[site_number].last_recovered_timestamp = timestamp
        self.sites[site_number].live = True

    def dump(self):
        for site in self.sites:
            site.display_store()
