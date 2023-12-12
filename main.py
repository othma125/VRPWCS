from input_data import data
from model_construction import math_model
from pprint import pprint

if __name__ == '__main__':
    print("Now starting..")
    print("\t..Now reading data..")
    try:
        inputs = data('c101.txt', 'Friday', 5)  # picked up stops including charging stations
        # print(inputs.vehicle_number)
        # print(inputs.vehicle_capacity)
        # pprint(inputs.stops)
        # pprint(inputs.rush_hours)
    except Exception as e:
        print("Reading of the data failed. Try again")
        print(e)
    else:
        try:
            print("\t..Now creating model..")
            model = math_model(inputs, 2)  # routes count
        except Exception as e:
            print("Something went wrong in creating model. Try again")
            print(e)
        else:
            try:
                print("\t..Now solving..")
                model.solve()
            except Exception as e:
                print("Something went wrong in processing. Try again")
                print(e)
