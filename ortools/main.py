from assembly import  *
from machining import *

def main():
    option = int(input('Please enter 1 for assembly and 2 for machining: '))
    today = input('Please enter the date in term of DD.MM.YYYY: ')
    if option == 1:
        case = int(input ('Please enter 1 for case 1 and 4 for case 4: '))
        file = input('Please enter input file with .xlsx extension: ')
        if case == 1:
             schedule_case_1(file,today,'Production Meeting')  
        elif case == 4: 
             schedule_case_4(file,today,'Production Meeting')
        else:
            print('Wrong option, please restart the program')
    elif option == 2:
        file = input('Please enter input file with .xlsx extension: ')
        generate_machine_schedule(file, today)
    else:
        print('Wrong option, please restart the program')
if __name__ == '__main__':
    main()











