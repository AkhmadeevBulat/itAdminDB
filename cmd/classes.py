import configparser
from ldap3 import Server, Connection, SUBTREE, ALL, NTLM
from os import getlogin
import pymysql.cursors


class VariablesSQLServer:
    def __init__(self, configFile: configparser.ConfigParser):
        self.__dbServer = configFile['PARAMETERS']['DB_SERVER']  # ip-адрес сервера базы данных
        self.__port = configFile['PARAMETERS']['PORT']  # Порт базы данных
        self.__dbUser = configFile['PARAMETERS']['DB_USER']  # Логин пользователя базы данных
        self.__dbPassword = configFile['PARAMETERS']['DB_PASSWORD']  # Пароль пользователя базы данных
        self.__dbDataBase = configFile['PARAMETERS']['DB_DATABASE']  # Имя базы
        self.__charset = configFile['PARAMETERS']['CHARSET']  # Кодировка

    def getDBServer(self):
        return self.__dbServer

    def getPort(self):
        return int(self.__port)

    def getDBUser(self):
        return self.__dbUser

    def getDBPassword(self):
        return self.__dbPassword

    def getDBDataBase(self):
        return self.__dbDataBase

    def getCharset(self):
        return self.__charset


class VariablesLDAPServer:
    def __init__(self, configFile: configparser.ConfigParser):
        self.__adServer = configFile['PARAMETERS']['AD_SERVER']  # ip-адрес сервера
        self.__adUser = configFile['PARAMETERS']['AD_USER']  # Логин пользователя
        self.__adPassword = configFile['PARAMETERS']['AD_PASSWORD']  # Пароль пользователя
        self.__path = configFile['PARAMETERS']['PATH']  # Область поиска
        self.__adAdminGroup = configFile['PARAMETERS']['AD_ADMIN_GROUP']  # Группа,
        # по которому будет доступ к функциям программы

    def getADServer(self):
        return self.__adServer

    def getADUser(self):
        return self.__adUser

    def getADPassword(self):
        return self.__adPassword

    def getPath(self):
        return self.__path

    def getADAdminGroup(self):
        return self.__adAdminGroup


class LDAPUserVerification(VariablesLDAPServer):
    def __init__(self, configFile: configparser.ConfigParser):
        super().__init__(configFile)
        self.__localUser = getlogin()  # Узнать текущего пользователя, который открыл программу
        self.__access = False  # Доступ
        self.__connect = Connection(Server(self.getADServer(), get_info=ALL),
                                    user=self.getADUser(),
                                    password=self.getADPassword(),
                                    authentication=NTLM)  # Подключение к серверу

    def getNameLocalUser(self) -> str:  # Показать пользователю под каким именем он сидит
        return self.__localUser

    def checkConnectionServer(self) -> bool:  # Проверка подключения к серверу
        return self.__connect.bind()

    def checkAccessFolder(self) -> bool:  # Проверка доступа к папке
        return self.__connect.search(self.getPath(), '(objectCategory=person)')

    def userExistenceAD(self) -> bool:  # Проверка, существует ли данный пользователь
        return self.__connect.search(self.getPath(), f'(&(objectCategory=person)(sAMAccountName={self.__localUser}))',
                                     SUBTREE, attributes=['memberOf'])

    def rightToUSe(self) -> bool:  # Проверка, существует ли у него право на использование данной программой
        self.__connect.search(self.getPath(), f'(&(objectCategory=person)(sAMAccountName={self.__localUser}))',
                              SUBTREE, attributes=['memberOf'])
        dataSearchUser = self.__connect.entries[0]  # Сохраняю данные о пользователе, если он существует
        for i in dataSearchUser.entry_attributes_as_dict.get('memberOf'):  # Получаем список всех memberOf
            cnGroup = i.split(',')[0].split('=')[1]  # Получаем только CN группы
            if cnGroup == self.getADAdminGroup():
                self.__access = True  # Разрешаю доступ, если хоть одна группа совпадает
        if not self.__access:
            return False
        else:
            return True


class SQLManager(VariablesSQLServer):
    def __init__(self, configFile: configparser.ConfigParser):
        super().__init__(configFile)
        self.__connect = None  # Соединение к SQL серверу

    def checkConnectionServer(self):  # Проверка доступа к серверу SQL
        self.__connect = pymysql.connect(host=self.getDBServer(),
                                         port=self.getPort(),
                                         user=self.getDBUser(),
                                         password=self.getDBPassword(),
                                         database=self.getDBDataBase(),
                                         charset=self.getCharset(),
                                         cursorclass=pymysql.cursors.DictCursor)

    def commitChange(self):  # Подтвердить изменения
        self.__connect.commit()

    def getTables(self) -> list[dict]:  # Выдай все таблицы
        with self.__connect.cursor() as cursor:
            cursor.execute('show tables;')
            tables = cursor.fetchall()
            return tables

    def checkTable(self, table: str) -> list[dict]:  # Проверь, есть ли такая таблица
        with self.__connect.cursor() as cursor:
            cursor.execute(f'select count(*) from information_schema.tables '
                           f'where table_schema = "{self.getDBDataBase()}" and table_name = "{table}";')
            result = cursor.fetchall()
            return result[0].get('count(*)')

    def tableOutput(self, table: str) -> list[dict]:  # Выдай все данные таблицы
        with self.__connect.cursor() as cursor:
            cursor.execute(f'select * from {table};')
            rows = cursor.fetchall()
            return rows

    def fieldsTable(self, table: str) -> list[dict]:  # Выдай все поля таблицы
        with self.__connect.cursor() as cursor:
            cursor.execute(f'desc {table};')
            fields = cursor.fetchall()
            return fields

    def searchInTable(self, table: str, concat: str, search: str) -> list[dict]:  # Поиск по таблице
        with self.__connect.cursor() as cursor:
            cursor.execute(f'select * from {table} where lower(concat({concat})) like lower("%{search}%");')
            results = cursor.fetchall()
            return results

    def addLine(self, table: str, concat: str, add: str):
        with self.__connect.cursor() as cursor:
            cursor.execute(f'insert into {table} ({concat}) value ({add});')

    def changeLine(self, table: str, change: str, search: str):
        with self.__connect.cursor() as cursor:
            cursor.execute(f'update {table} set {change} where {search};')

    def deleteLine(self, table: str, search: str):
        with self.__connect.cursor() as cursor:
            cursor.execute(f'delete from {table} where {search};')
