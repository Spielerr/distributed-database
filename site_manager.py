from site import Site


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
                for i in range(len(site.store[variable])):
                    if site.store[variable][i][0] > time:
                        return site.store[variable][i-1][1]
                return site.store[variable][-1][1]

        # if read failed and we have exited out of the for loop, then need to WAIT

    def update_site(self, variable, value, time):
        for site in self.sites:
            if variable in site.store:
                site.store[variable].append((time, value))

        # if write failed and we have exited out of the for loop, then need to WAIT

    def fail_site(self, site_number, timestamp):
        self.sites[site_number].last_failed_timestamp = timestamp
        self.sites[site_number].live = False

    def recover_site(self, site_number, timestamp):
        self.sites[site_number].last_recovered_timestamp = timestamp
        self.sites[site_number].live = True

    def dump(self):
        for site in self.sites:
            site.display_store()
