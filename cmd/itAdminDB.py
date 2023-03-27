import os
from time import sleep
from classes import LDAPUserVerification, SQLManager
from functions import developer, inputEndExit, inputContinue, readFile, clear, beautifulTable, parse_string
import pymysql.err


def main():
    # 1 Этап: Показать кто тут батька!
    print(developer() + '\n')
    sleep(1)

    # 2 Этап: Чтение файла
    # Проверка, есть ли такой файл. Если нет, создать его.
    if not os.path.isfile('settings.ini'):
        with open('settings.ini', 'w') as file:
            file.write('[PARAMETERS]\n\n; IP-адрес сервера\nAD_SERVER=\n\n'
                       '; Логин и пароль пользователя AD для подключения к AD. Ему не нужны ни какие права.\n'
                       'AD_USER=\nAD_PASSWORD=\n\n; Папка, где будет производится поиск\nPATH=\n\n'
                       '; Группа, с которым будет производится сравнения и давать доступ\nAD_ADMIN_GROUP=\n\n'
                       '; IP-адрес сервера базы данных\nDB_SERVER=\n\n; Порт базы данных\nPORT=\n\n; Имя базы данных\n'
                       'DB_DATABASE=\n\n; Кодировка базы данных\nCHARSET=\n\n'
                       '; Логин и пароль пользователя базы данных\n'
                       'DB_USER=\nDB_PASSWORD=\n\n')
            file.close()
        print('Создан файл настроек. Пожалуйста введите в нем данные!')
        inputEndExit()
    configFile = readFile()

    # 3 Этап: Проверка пользователя, который запустил программу, в Active Directory (LDAP)
    verificationLDAP = LDAPUserVerification(configFile=configFile)
    print(f'Вы зашли под пользователем: [{verificationLDAP.getNameLocalUser()}]')
    if verificationLDAP.checkConnectionServer():
        print('Подключение к серверу AD: присутствует')
    else:
        print('Подключение к серверу AD: отсутствует')
        inputEndExit()
    if verificationLDAP.checkAccessFolder():
        print(f'Доступ к папке [{verificationLDAP.getPath()}]: присутствует')
    else:
        print(f'Доступ к папке [{verificationLDAP.getPath()}]: отсутствует')
        inputEndExit()
    if verificationLDAP.userExistenceAD():
        print(f'Пользователь [{verificationLDAP.getNameLocalUser()}] в AD: существует')
    else:
        print(f'Пользователь [{verificationLDAP.getNameLocalUser()}] в AD: не существует')
        inputEndExit()
    if verificationLDAP.rightToUSe():
        print(f'Пользователю [{verificationLDAP.getNameLocalUser()}] разрешено использовать функции программы')
    else:
        print(f'Пользователю [{verificationLDAP.getNameLocalUser()}] запрещено использовать функции программы')
        inputEndExit()
    sleep(2)

    # 4 Этап: Проверка доступа к базе данных
    sqlManager = SQLManager(configFile=configFile)
    try:
        sqlManager.checkConnectionServer()
        print('Подключение к базе данных SQL: присутствует')
        sleep(2)
    except pymysql.err.OperationalError:
        print(f'Отсутствует подключение к базе данных (Неверный ip-адрес [{sqlManager.getDBServer()}], '
              f'порт [{sqlManager.getPort()}] или имя базы [{sqlManager.getDBDataBase()}])')
        inputEndExit()
    except RuntimeError:
        print('Отсутствует подключение к базе данных (Неверный логин или пароль)')
        inputEndExit()
    except AttributeError:
        print(f'Отсутствует подключение к базе данных. Неверная кодировка [{sqlManager.getCharset()}]')
        inputEndExit()

    # 5 Этап: Запуск менеджера SQL
    while True:
        try:
            clear()
            choice = input('0 - Завершить работу программы;\n'
                           '1 - Просмотр таблиц;\n'
                           '2 - Поиск по таблице;\n'
                           '3 - Изменение в таблице;\n'
                           'Выберете действие: ')
            match choice:
                case '0':  # 0 - Завершить работу программы
                    inputEndExit()
                case '1':  # 1 - Просмотр таблиц
                    while True:
                        clear()  # Чистка терминала
                        print('\n__Таблицы для вывода данных__\n')
                        print(beautifulTable(sqlManager.getTables()))  # Вывести красиво список таблиц
                        try:
                            choiceTable = input('Выберете таблицу (Чтобы выйти из режима просмотр таблиц [ ^C ]): ')
                            if not sqlManager.checkTable(choiceTable):  # Проверка таблицы на наличие
                                print(f'Ошибка: Возможно такой таблицы не существует [{choiceTable}]')
                                inputContinue()
                                continue
                            print(beautifulTable(sqlManager.tableOutput(choiceTable)))  # Вывести красиво данные таблицы
                        except KeyboardInterrupt:
                            break
                        inputContinue()
                case '2':  # 2 - Поиск по таблице
                    while True:
                        clear()  # Чистка терминала
                        try:
                            print('\n__Таблицы для поиска данных__\n')
                            print(beautifulTable(sqlManager.getTables()))  # Вывести красиво список таблиц
                            choiceTable = input('Выберете таблицу (Чтобы выйти из режима поиска по таблице [ ^C ]): ')

                            if not sqlManager.checkTable(choiceTable):  # Проверка таблицы на наличие
                                print(f'Ошибка: Возможно такой таблицы не существует [{choiceTable}]')
                                inputContinue()
                                continue

                            while True:
                                try:
                                    print('\nПо каким полям будет производиться поиск?')
                                    for field in sqlManager.fieldsTable(choiceTable):
                                        print(field.get('Field'), ' | ', end='')
                                    print()
                                    choiceField = input('Выберете поля (Пример №1: ID | Пример №2: ID, Hostname): ')
                                    choiceSearch = input('Что ищем: ')
                                    try:
                                        print(beautifulTable(sqlManager.searchInTable(choiceTable,
                                                                                      choiceField, choiceSearch)))
                                    except pymysql.err.OperationalError:
                                        print(f'Было введено не правильное поле [{choiceField}]')
                                        inputContinue()
                                        continue
                                except KeyboardInterrupt:
                                    break
                        except KeyboardInterrupt:
                            break
                        inputContinue()
                case '3':  # 3 - Изменение в таблице
                    while True:
                        clear()
                        print('\n__Таблица для изменения__\n')
                        print(beautifulTable(sqlManager.getTables()))
                        try:
                            choiceTable = input('Выберете таблицу (Чтобы выйти из режима изменения таблицы [ ^C ]): ')
                            if not sqlManager.checkTable(choiceTable):  # Проверка таблицы на наличие
                                print(f'Ошибка: Возможно такой таблицы не существует [{choiceTable}]')
                                inputContinue()
                                continue
                            while True:
                                try:
                                    clear()
                                    choiceChange = input('1 - Добавить строку;\n'
                                                         '2 - Изменить строку;\n'
                                                         '3 - Удалить строку.\n'
                                                         f'Выберете действие по изменению таблицы [{choiceTable}]: ')
                                    try:
                                        match choiceChange:
                                            case '1':  # 1 - Добавить строку
                                                while True:
                                                    clear()
                                                    print('\n___Добавление строки___\n')
                                                    tupleField = {}
                                                    for field in sqlManager.fieldsTable(choiceTable):
                                                        if field.get('Extra') == 'auto_increment':
                                                            continue
                                                        tupleField[field.get('Field')] = ''
                                                    while True:
                                                        for i in tupleField:
                                                            j = input(f'Введите значение для поле [{i}]: ')
                                                            tupleField[i] = parse_string(j)
                                                        print(beautifulTable(tupleField))
                                                        choiceBool = input('\nВсе правильно? (y/n): ')
                                                        match choiceBool.lower():
                                                            case 'n':
                                                                continue
                                                            case 'y':
                                                                concat = ''
                                                                value = ''
                                                                for i in tupleField:
                                                                    concat += f'{i}, '
                                                                    value += f'"{tupleField.get(i)}", '
                                                                concat = concat[:-2]
                                                                value = value[:-2]
                                                                sqlManager.addLine(choiceTable, concat, value)
                                                                sqlManager.commitChange()
                                                                print('Добавлено!')
                                            case '2':  # 2 - Изменить строку
                                                print(beautifulTable(sqlManager.tableOutput(choiceTable)))
                                                choiceField = input('Выбрать строку по полю: ')
                                                choiceSearch = input(f'Значение поля [{choiceField}]: ')
                                                print(beautifulTable(sqlManager.searchInTable(choiceTable,
                                                                                              choiceField, choiceSearch)))
                                                choiceBool = input('\nЭта строка? (y/n): ')
                                                match choiceBool.lower():
                                                    case 'n':
                                                        continue
                                                    case 'y':
                                                        tupleField = {}
                                                        for field in sqlManager.fieldsTable(choiceTable):
                                                            if field.get('Extra') == 'auto_increment':
                                                                continue
                                                            tupleField[field.get('Field')] = ''
                                                        for values in sqlManager.searchInTable(choiceTable,
                                                                                               choiceField, choiceSearch):
                                                            for value in values:
                                                                if value in tupleField:
                                                                    tupleField[value] = values.get(value)
                                                        while True:
                                                            for i in tupleField:
                                                                j = input(f'Введите значение для поле [{i}] (Для прежнего значения'
                                                                          f' [{values.get(i)}] нажмите Enter): ')
                                                                if j != '':
                                                                    k = parse_string(j)
                                                                    tupleField[i] = k
                                                                else:
                                                                    tupleField[i] = values.get(i)
                                                            print(beautifulTable(tupleField))
                                                            choiceBool = input('\nВсе правильно? (y/n): ')
                                                            match choiceBool:
                                                                case 'n':
                                                                    continue
                                                                case 'y':
                                                                    change = ''
                                                                    for i in tupleField:
                                                                        change += f'{i} = "{tupleField.get(i)}", '
                                                                    change = change[:-2]
                                                                    print(change)
                                                                    sqlManager.changeLine(choiceTable, change,
                                                                                          f'{choiceField} = "{choiceSearch}"')
                                                                    sqlManager.commitChange()
                                                                    print('Изменено!')
                                            case '3':  # 3 - Удалить строку
                                                print(beautifulTable(sqlManager.tableOutput(choiceTable)))
                                                choiceField = input('Выбрать строку по полю: ')
                                                choiceSearch = input(f'Значение поля [{choiceField}]: ')
                                                print(beautifulTable(sqlManager.searchInTable(choiceTable,
                                                                                              choiceField, choiceSearch)))
                                                choiceBool = input('\nУдалить эту строку? (y/n): ')
                                                match choiceBool.lower():
                                                    case 'n':
                                                        continue
                                                    case 'y':
                                                        sqlManager.deleteLine(choiceTable,
                                                                              f'{choiceField} = "{choiceSearch}"')
                                                        sqlManager.commitChange()
                                                        print('Удалено!')
                                    except KeyboardInterrupt:
                                        continue
                                except KeyboardInterrupt:
                                    break
                        except KeyboardInterrupt:
                            break
                        inputContinue()
        except pymysql.err.OperationalError as err:
            print('Удаленный хост принудительно разорвал существующее подключение. Пробую восстановить подключение.')
            try:
                sqlManager.checkConnectionServer()
                print('Подключение к базе данных SQL: присутствует')
                sleep(2)
            except pymysql.err.OperationalError:
                print(f'Отсутствует подключение к базе данных (Неверный ip-адрес [{sqlManager.getDBServer()}], '
                      f'порт [{sqlManager.getPort()}] или имя базы [{sqlManager.getDBDataBase()}])')
                inputEndExit()
            except RuntimeError:
                print('Отсутствует подключение к базе данных (Неверный логин или пароль)')
                inputEndExit()
            except AttributeError:
                print(f'Отсутствует подключение к базе данных. Неверная кодировка [{sqlManager.getCharset()}]')
                inputEndExit()
        except Exception as err:
            print(f'Не предвиденная ошибка, пожалуйста покажите разработчику: {err}')
            inputEndExit()
        except KeyboardInterrupt:
            exit()


if __name__ == '__main__':
    main()
