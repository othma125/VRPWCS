from csv import DictReader


class data:
    def __init__(self, file_name, day: str, max_lines: int = 10):
        self.working_day = day.lower()
        self.file_name = file_name
        self.vehicles_speed_average: int = 60  # km/h
        self.battery_capacity: int = 68000  # Wh
        self.I_min: float = 0.2 * self.battery_capacity  # min state of charging
        self.energy_consumption_rate: float = 1.25  # consumption rate by WH / Km / Kg
        self.reload_battery_cost_in_depot: float = 0.15  # by dollar / KWh
        self.reload_battery_cost_in_stations: float = 0.55  # by dollar / KWh
        self.reload_battery_time: float = 1.5  # by minutes / KWh
        self.vehicle_initial_weight: float = 1300  # kg
        self.drivers_daily_cost: int = 13 * 8  # dollars * 8 hours of working day
        with open('instances/Solomon/' + self.file_name, mode='r') as instance_file:
            lines = instance_file.readlines()
            # Read vehicle information
            vehicle_info = lines[4].split()
            self.vehicle_number = int(vehicle_info[0])
            self.vehicle_capacity = int(vehicle_info[1])
            self.stops = []
            # Read customer information
            i = 0
            for line in lines[9:]:
                # if line.strip():  # Skip empty lines
                is_charging_station = i % 5 == 0
                stop_info = line.split()
                new_stop = {
                    'service_time': int(stop_info[6]),
                    'is_charging_station': is_charging_station,  # depot is a charging station
                    'demand': 0 if is_charging_station else int(stop_info[3]),
                    'coordinates': stop(float(stop_info[1]), float(stop_info[2])),
                    'time_window': time_window(int(stop_info[4]), int(stop_info[5]))
                }
                self.stops.append(new_stop)
                if len(self.stops) > max_lines:
                    break
                i += 1
            self.stops_count = len(self.stops)
        with open('rush_hour_singapore.csv', mode='r', newline='') as csvfile:
            # CSV reader with default delimiter ',' and quote character '"'
            reader = DictReader(csvfile)
            self.rush_hours = {}
            for row in reader:
                # The 'Time' column will be the key for each dictionary
                time: str = row.pop('Time')
                # The rest of the columns are days with their respective percentages
                days_data = {day.lower(): int(percentage.split('%')[0]) / 100 for day, percentage in row.items()}
                # Append the dictionary to the array
                self.rush_hours.update({time: days_data})
        self.distance = {}

    def travel_distance(self, i, j):
        if i == j:
            return 0
        key = f'{i}_{j}'
        try:
            return self.distance[key]
        except KeyError:
            try:
                return self.distance[f'{j}_{i}']
            except KeyError:
                coordinate1 = self.stops[i]['coordinates']
                coordinate2 = self.stops[j]['coordinates']
                self.distance[key] = coordinate1.get_distance(coordinate2)
                return self.distance[key]

    def travel_time(self, i, j, vehicle_speed):  # in minutes
        return (self.travel_distance(i, j) / vehicle_speed) * 60


class stop:
    def __init__(self, x_coord: float, y_coord: float):
        self.x = x_coord
        self.y = y_coord

    def get_distance(self, other_stop):
        return ((self.x - other_stop.x) ** 2 + (self.y - other_stop.y) ** 2) ** 0.5

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __repr__(self) -> str:
        return self.__str__()


class time_window:
    def __init__(self, rt: int, dt: int) -> None:
        if rt >= dt:
            raise ValueError('Ready time must be less than due time')
        self.ready_time = rt
        self.due_time = dt

    def __str__(self) -> str:
        return f'({self.ready_time}, {self.due_time})'

    def __repr__(self) -> str:
        return self.__str__()
