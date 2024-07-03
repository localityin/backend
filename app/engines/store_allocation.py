class StoreAllocator():
    def __init__(self, db, user_id) -> None:
        self.db = db
        self.locating = True
        self.user_id = user_id
        pass

    def run(self):
        # form a union of stores_by_location and stores_by_order
        # sort by rating of the store
        # sort by number of orders recieved by store today
        # sort by distance from user
        self.locating = False
        pass

    def get_stores_by_location(self):
        pass

    def get_stores_by_order(self):
        pass

    def get_user_address(self):
        pass
