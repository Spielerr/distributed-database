from site import Site


class SiteManager:
    def __init__(self):
        self.sites = []
        self.initialize_sites()

    def initialize_sites(self):
        for i in range(1, 11):
            self.sites.append(Site(i))

    def return_value(self, variable, time):
        for site in self.sites:
            if variable in site.store:
                for i in range(len(site.store[variable])):
                    if site.store[variable][i][0] > time:
                        return site.store[variable][i-1][1]
                return site.store[variable][-1][1]

    def update_site(self, variable, value, time):
        for site in self.sites:
            if variable in site.store:
                site.store[variable].append((time, value))

    def dump(self):
        for site in self.sites:
            site.display_store()
