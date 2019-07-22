
from assembly import main2
import csv
import datetime
import socket
if __name__ == "__main__":
    try:
        main2()
        with open('Z:\\Users\\Dang\\track.csv', 'a') as csvFile:
            csvFile.write(socket.gethostname() + ','+ str(datetime.datetime.now()) + '\n')
    except Exception as e:
        print(e)
    exit = input('Press any keys to exit')