import configparser
from sys import platform
from os import system
from prettytable import PrettyTable


def parse_string(string: str) -> str:  # Каждые n символов перенос строки
    new_string = ""

    for letter_index in range(len(string)):

        if letter_index % 33 == 0 and letter_index != 0:
            new_string += f"{string[letter_index]}\n"
        else:
            new_string += string[letter_index]

    return new_string


def beautifulTable(table) -> PrettyTable:
    myTable = None
    listFields = []
    listValues = []

    if isinstance(table, list):
        for i in table:
            if not myTable:
                for j in i:
                    listFields.append(j)
                myTable = PrettyTable(listFields)
            for y in i.values():
                listValues.append(y)
            myTable.add_row(listValues)
            listValues.clear()
        return myTable
    elif isinstance(table, dict):
        if not myTable:
            for j in table:
                listFields.append(j)
            myTable = PrettyTable(listFields)
        for y in table.values():
            listValues.append(y)
        myTable.add_row(listValues)
        listValues.clear()
        return myTable


def clear():
    if platform == 'linux' or platform == 'linux2':
        system('clear')
    elif platform == 'darwin':
        system('clear')
    elif platform == 'win32':
        system('cls')


def developer():  # Чтобы IT отдел всегда знал, кто создал этот код!
    return 'Разработчик: Ахмадеев Булат Наилевич'


def inputContinue():
    _ = input('\nНажмите Enter...')


def inputEndExit():
    _ = input('\nНажмите Enter...')
    exit()


def readFile():  # Чтение файла конфигурации
    configFile = configparser.ConfigParser()
    configFile.read('settings.ini', encoding='UTF-8')
    return configFile
