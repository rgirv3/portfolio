from listBrain import List
import os
import platform

listService = List()


def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def menu_list():
    while True:
        print('FaxIn Calling Party Reject tool V1.3:')
        print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
        print('1. View lists by Customer Number (Start here)')
        print('')
        print('2. Add to an existing list')
        print('3. Delete number(s) from a list')
        print('')
        print('4. Create list')
        print('5. Delete list')
        print('')
        print('6. Apply list changes to EAS')
        print('')
        print('Q. Quit')
        print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
        choice = input('Please enter number for requested action: ').upper()
        if choice == 'Q':
            exit()
        elif choice == '1':
            clear()
            listService.getCustList()
            clear()
        elif choice == '2':
            clear()
            listService.addEntries()
            clear()
        elif choice == '3':
            clear()
            listService.checkDelete('number')
            clear()
        elif choice == '4':
            clear()
            listService.createList()
            clear()
        elif choice == '5':
            clear()
            listService.checkDelete('list')
            clear()
        elif choice == '6':
            clear()
            print('FaxIn Calling Party Reject tool V1.1:')
            print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
            print('1. Apply list to entire customer account')
            print('2. Apply list to single inbound profile')
            print('3. Apply list to single inbound number')
            print('')
            print('4. Remove list from entire customer account')
            print('5. Remove list from single inbound profile')
            print('6. Remove list from single inbound number')
            print()
            print('Q. Return to previous menu')
            print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
            choice = input('Please enter number for requested action: ').upper()
            clear()
            if choice == 'Q':
                pass
            else:
                listService.command(choice)
                clear()


menu_list()
