from assembly import  assembly_scheduling, groups


def main():
    qualified_orders = {}
    #qualified_orders = assembly_scheduling.read_data_assembly('a_input.csv','14/02/2019')
    file = input('Please enter the file name in xlsx: ')
    today = input('Please enter the date in term of DD.MM.YYYY: ')
    assembly_scheduling.read_data_excel(file, today)
    groups.capacity_input('capacity.csv')
    assembly_scheduling.assign_date_before(groups,'output.csv')
    #for index, list in qualified_orders.items():
    #    if index < 7:
    #        assembly_scheduling.schedule(list, groups)
if __name__ == '__main__':
    main()
