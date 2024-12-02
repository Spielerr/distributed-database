from site import Site


class SiteManager:
    def __init__(self):
        self.sites = []
        self.initialize_sites()

    def initialize_sites(self):
        for i in range(1, 11):
            self.sites.append(Site(i))

    def update_site(self, variable, value):
        for site in self.sites:
            if variable in site.store and site.store[variable] is None:
                site.store[variable] = value

    def dump(self):
        for site in self.sites:
            site.display_store()