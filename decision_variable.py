from pulp import LpContinuous, LpInteger, LpBinary, LpVariable


class X_variable:
    def __init__(self, route: int, stop1: int, stop2: int):
        self.stop1 = stop1
        self.stop2 = stop2
        self.route = route

    def get_key(self) -> str:
        key_tuple = str(self.route), str(self.stop1), str(self.stop2)
        return 'x'.join(key_tuple)

    def get_decision_variable(self):
        return LpVariable(self.get_key(),
                          lowBound=0,
                          upBound=1,
                          cat=LpBinary)


class Y_variable:
    def __init__(self, route: int):
        self.route = route

    def get_key(self) -> str:
        return f'y{self.route}'

    def get_decision_variable(self):
        return LpVariable(self.get_key(),
                          lowBound=0,
                          upBound=1,
                          cat=LpBinary)


class D_variable:
    def __init__(self, route: int, stop: int):
        self.stop = stop
        self.route = route

    def get_key(self) -> str:
        key_tuple = str(self.route), str(self.stop)
        return 'd'.join(key_tuple)

    def get_decision_variable(self):
        return LpVariable(self.get_key(),
                          cat=LpInteger)


class W_variable:
    def __init__(self, route: int, stop: int):
        self.stop = stop
        self.route = route

    def get_key(self) -> str:
        key_tuple = str(self.route), str(self.stop)
        return 'w'.join(key_tuple)

    def get_decision_variable(self):
        return LpVariable(self.get_key(),
                          cat=LpContinuous)


class WW_variable:
    def __init__(self, route: int):
        self.route = route

    def get_key(self) -> str:
        return f'ww{self.route}'

    def get_decision_variable(self):
        return LpVariable(self.get_key(),
                          cat=LpContinuous)


class I_variable:
    def __init__(self, route: int, stop: int):
        self.stop = stop
        self.route = route

    def get_key(self) -> str:
        key_tuple = str(self.route), str(self.stop)
        return 'i'.join(key_tuple)

    def get_decision_variable(self):
        return LpVariable(self.get_key(),
                          cat=LpContinuous)
