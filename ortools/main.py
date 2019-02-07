from assembly import  assembly_scheduling, groups


def main():
    qualified_orders = {}
    qualified_orders = assembly_scheduling.read_data_assembly('a_input.csv','14/02/2019')
    groups.capacity_input('capacity.csv')
    for index, list in qualified_orders.items():
        if index < 7:
            assembly_scheduling.schedule(list, groups)
if __name__ == '__main__':
    main()
