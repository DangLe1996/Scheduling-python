from assembly import  assembly_scheduling, groups


def main():
    assembly_scheduling.read_data_assembly('a_input.csv','14/02/2019')
    groups.capacity_input('capacity.csv')
   
if __name__ == '__main__':
    main()
