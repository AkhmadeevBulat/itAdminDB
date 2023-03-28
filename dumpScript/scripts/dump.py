import os
import datetime


class Variables:
    def __init__(self, dbServer: str, port: int, dbDataBases: list,
                 charset: str, dbUser: str, dbPassword: str):
        self.dbServer = dbServer
        self.port = port
        self.dbDataBases = dbDataBases
        self.charset = charset
        self.dbUser = dbUser
        self.dbPassword = dbPassword
        self.dbDataBases_str = str()
        self.conversion()

    def conversion(self):
        for i in self.dbDataBases:
            self.dbDataBases_str += f' {str(i)}'


def checkingDateTime(days: int):
    for directory in os.listdir():
        dateDump = directory.split(' ')[0]  # Дата
        timeDump = directory.split(' ')[1]  # Время
        # Получаю дату и время нормального формата, как того и требует библиотека datetime
        pathTime = datetime.datetime(year=int(dateDump.split('_')[2]), month=int(dateDump.split('_')[1]),
                                     day=int(dateDump.split('_')[0]), hour=int(timeDump.split('_')[0]),
                                     minute=int(timeDump.split('_')[1]))

        # Получаю разницу во времени
        differenceTime = datetime.datetime.today() - datetime.timedelta(days=days)

        # Удаляю папку если прошло n кол-во дней
        if pathTime < differenceTime:
            os.rmdir(f'{directory}')
        else:
            continue


def createFolder(name):  # Создать папку если его нет
    if not os.path.exists(name):
        os.mkdir(name)
    return name


def main():
    # Проверка, есть ли файл settings.py, если нет - создать ее
    if not os.path.isfile('settings.py'):
        with open('settings.py', 'w', encoding='utf-8') as file:
            file.write('dbServer = None\nport = None\ndbDataBases = []\ncharset = None\ndbUser = None\n'
                       'dbPassword = None\nexpirationDate = None')
            file.close()
        print('Создан файл настроек. Пожалуйста введите в нем данные!')
        exit()

    import settings

    # Проверка на целостность данных в settings.py
    if settings.port is None or settings.dbUser is None or settings.dbServer is None:
        print('Создан файл настроек. Пожалуйста введите в нем данные!')
        exit()

    # Задаем необходимые значения от файла settings.py
    variables = Variables(settings.dbServer, settings.port, settings.dbDataBases,
                          settings.charset, settings.dbUser, settings.dbPassword)

    # Проверка, есть ли папка, если нет - создать эту папку
    if not os.path.isdir('../dump'):
        os.mkdir('../dump')

    # Переход в папку с dump'ами
    os.chdir('../dump/')

    newTime = datetime.datetime.today()  # Получаю дату и время

    # Проверка папок dump на срок годности в n дней
    checkingDateTime(settings.expirationDate)

    # Создаю папку с именем даты и времени, а также возвращаю имя папки
    namePath = createFolder(newTime.strftime('%d_%m_%Y %H_%M'))

    # Переход к этой папке
    os.chdir(namePath)

    # Создаю dump базы данных
    os.system(f'mysqldump -h {variables.dbServer} -P {variables.port} -u {variables.dbUser} '
              f'--password={variables.dbPassword} -B{variables.dbDataBases_str} > dump.sql')


if __name__ == '__main__':
    main()
