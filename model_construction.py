import pulp as p
from pandas import DataFrame as df

from decision_variable import *
from input_data import data


class math_model:
    def __init__(self, input_data: data, r: int = 1):
        self.__inputs: data = input_data
        self.__routes_count: int = r
        self.__model: p.LpProblem = p.LpProblem("VRP_for_EV", p.LpMinimize)
        self.__M = sum(self.__inputs.stops[i]['time_window'].due_time for i in range(self.__inputs.stops_count))
        self.__X_variables = {}
        for r in range(self.__routes_count):
            for i in range(self.__inputs.stops_count):
                for j in range(self.__inputs.stops_count):
                    if i != j:
                        X: X_variable = X_variable(r, i, j)
                        self.__X_variables[X.get_key()] = X.get_decision_variable()
        # visit all customers constraints
        for i in range(self.__inputs.stops_count):
            if not self.__inputs.stops[i]['is_charging_station']:
                sum_x = 0
                for r in range(self.__routes_count):
                    for j in range(self.__inputs.stops_count):
                        if i != j:
                            sum_x += self.__X_variables[X_variable(r, i, j).get_key()]
                self.__model += sum_x == 1
        for r in range(self.__routes_count):
            for j in range(self.__inputs.stops_count):
                sum_1 = 0
                sum_2 = 0
                for i in range(self.__inputs.stops_count):
                    if i != j:
                        sum_1 += self.__X_variables[X_variable(r, i, j).get_key()]
                        sum_2 += self.__X_variables[X_variable(r, j, i).get_key()]
                self.__model += sum_1 == sum_2
        # vehicle usage constraints
        self.__Y_variables = {}
        for r in range(self.__routes_count):
            Y: Y_variable = Y_variable(r)
            key: str = Y.get_key()
            self.__Y_variables[key] = Y.get_decision_variable()
            sum_x = 0
            for j in range(1, self.__inputs.stops_count):
                sum_x += self.__X_variables[X_variable(r, 0, j).get_key()]
            self.__model += sum_x == self.__Y_variables[key]
        # capacity constraints
        self.__D_variables = {}
        max_weight = self.__inputs.vehicle_initial_weight + self.__inputs.vehicle_capacity
        for r in range(self.__routes_count):
            for i in range(self.__inputs.stops_count):
                D: D_variable = D_variable(r, i)
                key: str = D.get_key()
                self.__D_variables[key] = D.get_decision_variable()
                self.__model += self.__D_variables[key] >= self.__inputs.vehicle_initial_weight + self.__inputs.stops[i]['demand']
                self.__model += self.__D_variables[key] <= max_weight
        for r in range(self.__routes_count):
            for i in range(self.__inputs.stops_count):
                key_i: str = D_variable(r, i).get_key()
                for j in range(1, self.__inputs.stops_count):
                    if i != j:
                        key_j: str = D_variable(r, j).get_key()
                        key_x: str = X_variable(r, i, j).get_key()
                        self.__model += self.__D_variables[key_i] - self.__D_variables[key_j] \
                                        >= max_weight * (self.__X_variables[key_x] - 1) + self.__inputs.stops[i]['demand']
        # # state of charge constraints
        self.__I_variables = {}
        for r in range(self.__routes_count):
            for i in range(self.__inputs.stops_count):
                I: I_variable = I_variable(r, i)
                key: str = I.get_key()
                self.__I_variables[key] = I.get_decision_variable()
                if self.__inputs.stops[i]['is_charging_station']:
                    if i > 0:
                        self.__model += self.__I_variables[key] >= 0
                    else:
                        self.__model += self.__I_variables[key] == (1 - self.__Y_variables[Y_variable(r).get_key()]) * self.__inputs.battery_capacity
                else:
                    self.__model += self.__I_variables[key] >= self.__inputs.I_min
                self.__model += self.__I_variables[key] <= self.__inputs.battery_capacity
        for r in range(self.__routes_count):
            for i in range(self.__inputs.stops_count):
                key_Ii: str = I_variable(r, i).get_key()
                key_Di: str = D_variable(r, i).get_key()
                for j in range(1, self.__inputs.stops_count):
                    if i != j:
                        key_Ij: str = I_variable(r, j).get_key()
                        key_x: str = X_variable(r, i, j).get_key()
                        if self.__inputs.stops[i]['is_charging_station']:
                            self.__model += self.__inputs.battery_capacity - self.__inputs.energy_consumption_rate * \
                                            self.__inputs.travel_distance(i, j) * self.__D_variables[key_Di] \
                                            >= self.__I_variables[key_Ij] - (1 - self.__X_variables[key_x]) * \
                                            self.__inputs.battery_capacity
                        else:
                            self.__model += self.__I_variables[key_Ii] - self.__inputs.energy_consumption_rate * \
                                            self.__inputs.travel_distance(i, j) * self.__D_variables[key_Di] \
                                            >= self.__I_variables[key_Ij] - (1 - self.__X_variables[key_x]) * \
                                            self.__inputs.battery_capacity

        # time window constraints
        self.__W_variables = {}
        for r in range(self.__routes_count):
            for i in range(self.__inputs.stops_count):
                W: W_variable = W_variable(r, i)
                key: str = W.get_key()
                self.__W_variables[key] = W.get_decision_variable()
                if self.__inputs.stops[i]['is_charging_station']:
                    self.__model += self.__W_variables[key] >= self.__inputs.stops[0]['time_window'].ready_time
                    self.__model += self.__W_variables[key] <= self.__inputs.stops[0]['time_window'].due_time
                else:
                    self.__model += self.__W_variables[key] >= self.__inputs.stops[i]['time_window'].ready_time
                    self.__model += self.__W_variables[key] <= self.__inputs.stops[i]['time_window'].due_time
        for r in range(self.__routes_count):
            for i in range(self.__inputs.stops_count):
                key_wi: str = W_variable(r, i).get_key()
                time_stamp = time_in_minutes_to_canonical_format(self.__inputs.stops[i]['time_window'].ready_time)
                speed_deviation: float = (1 - self.__inputs.rush_hours[time_stamp][self.__inputs.working_day])
                vehicle_speed: float = speed_deviation * self.__inputs.vehicles_speed_average
                if self.__inputs.stops[i]['is_charging_station']:
                    service_time: float = (self.__inputs.battery_capacity - self.__I_variables[I_variable(r, i).get_key()]) / 1000  # in KWH
                    service_time *= self.__inputs.stops[i]['service_time'] / 60  # in minutes
                else:
                    service_time: float = self.__inputs.stops[i]['service_time'] * self.__inputs.stops[i]['demand'] / 60  # in minutes
                for j in range(1, self.__inputs.stops_count):
                    if i != j:
                        key_wj: str = W_variable(r, j).get_key()
                        key_x: str = X_variable(r, i, j).get_key()
                        self.__model += self.__W_variables[key_wi] + service_time + self.__inputs.travel_time(i, j, vehicle_speed)\
                                        <= self.__W_variables[key_wj] + (1 - self.__X_variables[key_x]) * self.__M
        self.__WW_variables = {}
        for r in range(self.__routes_count):
            WW: WW_variable = WW_variable(r)
            key: str = WW.get_key()
            self.__WW_variables[key] = WW.get_decision_variable()
            self.__model += self.__WW_variables[key] <= self.__inputs.stops[0]['time_window'].due_time
        for r in range(self.__routes_count):
            key_ww: str = WW_variable(r).get_key()
            for i in range(1, self.__inputs.stops_count):
                key_w: str = W_variable(r, i).get_key()
                key_x: str = X_variable(r, i, 0).get_key()
                time_stamp = time_in_minutes_to_canonical_format(self.__inputs.stops[i]['time_window'].ready_time)
                speed_deviation: float = (1 - self.__inputs.rush_hours[time_stamp][self.__inputs.working_day])
                vehicle_speed: float = speed_deviation * self.__inputs.vehicles_speed_average
                if self.__inputs.stops[i]['is_charging_station']:
                    service_time: float = (self.__inputs.battery_capacity - self.__I_variables[I_variable(r, i).get_key()]) / 1000  # in KWH
                    service_time *= self.__inputs.stops[i]['service_time'] / 60  # in minutes
                else:
                    service_time: float = self.__inputs.stops[i]['service_time'] * self.__inputs.stops[i]['demand'] / 60  # in minutes
                self.__model += self.__W_variables[key_w] + service_time + self.__inputs.travel_time(i, 0, vehicle_speed)\
                                <= self.__WW_variables[key_ww] + (1 - self.__X_variables[key_x]) * self.__inputs.stops[0]['time_window'].due_time
        # objective function
        obj = 0
        for r in range(self.__routes_count):
            obj += self.__Y_variables[Y_variable(r).get_key()] * self.__inputs.drivers_daily_cost
            for i in range(self.__inputs.stops_count):
                if self.__inputs.stops[i]['is_charging_station']:
                    charged_amount = self.__inputs.battery_capacity - self.__I_variables[I_variable(r, i).get_key()]
                    if i == 0:
                        obj += self.__inputs.reload_battery_cost_in_depot * charged_amount / 1000
                    else:
                        obj += self.__inputs.reload_battery_cost_in_stations * charged_amount / 1000
        self.__model += obj

    def solve(self):
        # path_to_cplex = r'C:\Program Files\IBM\ILOG\CPLEX_Studio128\cplex\bin\x64_win64\cplex.exe'
        # solver = p.CPLEX_CMD(path=path_to_cplex)
        # self.__model.solve(solver)
        self.__model.solve()
        status: str = p.LpStatus[self.__model.status]
        print(f'Result status = {status}')
        if status == 'Infeasible':
            print('No solution found')
            return
        print(f'Objective function value = {round(p.value(self.__model.objective))} dollars')
        result = []
        route = 1
        for r in range(self.__routes_count):
            c = False
            for i in range(self.__inputs.stops_count):
                for j in range(self.__inputs.stops_count):
                    if i != j and p.value(self.__X_variables[X_variable(r, i, j).get_key()]) > 0:
                        key_D: str = D_variable(r, i).get_key()
                        key_W: str = W_variable(r, i).get_key()
                        key_I: str = I_variable(r, i).get_key()
                        time_stamp = time_in_minutes_to_canonical_format(self.__inputs.stops[i]['time_window'].ready_time)
                        traffic: float = self.__inputs.rush_hours[time_stamp][self.__inputs.working_day]
                        vehicle_speed: float = (1 - traffic) * self.__inputs.vehicles_speed_average
                        state_of_charge: float = self.__inputs.battery_capacity if self.__inputs.stops[i]['is_charging_station'] else p.value(self.__I_variables[key_I])
                        state_of_charge = state_of_charge / self.__inputs.battery_capacity
                        result.append({
                            'route': route,
                            'coordinates': self.__inputs.stops[i]['coordinates'].__str__(),
                            'stop_id': i,
                            'next_stop_id': j,
                            'is_charging_station': self.__inputs.stops[i]['is_charging_station'],
                            'load': round(p.value(self.__D_variables[key_D])) - self.__inputs.vehicle_initial_weight,
                            'visit_time_stamp': toTimeFormat(round(p.value(self.__W_variables[key_W]))),
                            'travel_time': round(self.__inputs.travel_time(i, j, vehicle_speed), 2),
                            'traffic': traffic,
                            'speed': vehicle_speed,
                            'state_of_charge': round(state_of_charge, 2)
                        })
                        c = True
                        break
            if c:
                route += 1
        for i in range(len(result)):
            for j in range(i + 1, len(result)):
                if result[i]['route'] == result[j]['route'] \
                        and result[i]['next_stop_id'] == result[j]['stop_id'] \
                        and j > i + 1:
                    result.insert(i + 1, result.pop(j))
                    break
                elif result[i]['route'] != result[j]['route']:
                    break
        # sort result by route and stop_id
        file_name = f'result {self.__inputs.file_name.split(".")[0]}_{self.__inputs.stops_count - 1}_{self.__inputs.working_day}.csv'
        df(result).to_csv(file_name, index=False)


def toTimeFormat(time: int) -> str:
    hour = time // 60
    s = ("0" if hour < 10 else "") + str(hour) + ":"
    minutes = time % 60
    s += ("0" if minutes < 10 else "") + str(minutes)
    return s


def time_in_minutes_to_canonical_format(time: int):
    hour = time // 60
    if hour > 12:
        hour -= 12
        return f'{hour}:00 pm'
    elif hour == 12:
        return f'{hour}:00 pm'
    elif hour == 0:
        return '12:00 am'
    return f'{hour}:00 am'
