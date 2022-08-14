

class Route:

    def __init__(self):
        self.branch_id = None
        self.next = None

    def append(self, branch_id):
        end = Route()
        end.branch_id = branch_id
        while (self.next):
            self=self.next
        self.next = end

    def copy(self):
        route_copy = Route()
        route_copy.branch_id = self.branch_id
        #route_copy.next = self.next
        while (self.next):
            self = self.next
            route_copy.append(self.branch_id)
        return route_copy

    def print(self):
        s=str(self.branch_id)
        while (self.next):
            self = self.next
            s+=" -> "+str(self.branch_id)
        return s

    def cutFirstNull(self):
        if self.branch_id == None:
            next = self.next
            if next != None:
                self = next
        return self

    def getBranchListByRoute(self):
        ls = []
        ls.append(self.branch_id)
        while (self.next):
            self = self.next
            ls.append(self.branch_id)
        return ls
