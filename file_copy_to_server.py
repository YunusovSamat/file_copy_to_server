import json
import ftplib


# Класс для копирования файлов с ПК на FTP-сервер.
class FileCopyFTP:
    def __init__(self):
        self.__host = ''
        self.__port = 21
        self.__username = ''
        self.__password = ''
        self.__paths = []
        self.__conn = ftplib.FTP()

    # Метод для чтения данных из json файла.
    def read_json_file(self, path='config.json'):
        try:
            # Открываем файл config.json (или другой) на чтение.
            with open(path, "r") as file:
                # Загружаем json данные в словарь.
                config_data = json.load(file)
                # Получаем из словаря информацию о сервере.
                self.__host = config_data['host']
                self.__port = config_data['port']
                # Получаем из словаря информацию о пользователе.
                self.__username = config_data['username']
                self.__password = config_data['password']
                # Получаем из словаря инофрмацию о путях копируемого файла
                # и вставляемого ftp файла.
                self.__paths = config_data['paths']
        # Обработка исключения, если json файл не найден.
        except FileNotFoundError:
            print('Файл не найден')
            exit(1)
        # Обработка исключения, если указана папка, а не файл.
        except IsADirectoryError:
            print('Это не файл, а папка')
        # Обработка исключения, если возникла другая ошибка.
        except OSError:
            print('Ошибка открытия файла')

    # Метод для соединения с сервером и входа.
    def connect_server(self):
        try:
            # Соединение с сервером.
            self.__conn.connect(self.__host, self.__port)
        # Обработка исключения, если соединение не прошло.
        except ftplib.all_errors as err:
            print(err)
            exit(1)
        # Если соединение установлено.
        else:
            print('Соединение с сервером установлено.')
            try:
                # Авторизация пользователя.
                self.__conn.login(self.__username, self.__password)
            # Обработка исключения, если логин или пароль не верный.
            except ftplib.error_perm as err:
                print(err)
                exit(1)
            else:
                print('Вход выполнен.')

    # Метод для копирования файлов на сервер.
    def copy_to_server(self):
        # Перебор всех файлов, которые должны скопироваться на ftp-сервер.
        for file in self.__paths:
            try:
                # Открываем файл копируемого на чтение в бинарном режиме.
                with open(file['source_path'], 'rb') as source_file:
                    # Отправляем файл на ftp-сервер.
                    self.__conn.storbinary('STOR ' + file['ftp_path'],
                                           source_file)
            # Обработка исключения, если копируемый файл не найден.
            except FileNotFoundError:
                print('Файл не найден')
            # Обработка исключения, если указана папка, а не файл.
            except IsADirectoryError:
                print('Это не файл, а папка')
            # Обработка исключения, если возникла другая ошибка файла.
            except OSError:
                print('Ошибка открытия файла')
            # Обработка исключения, если возникла ошбика ftp-сервера.
            except ftplib.error_perm as err:
                print('Ошибка: ', err)
            # Если файл успешно скопирован на ftp-сервер.
            else:
                print('Успешно скопирован файл:', file['source_path'])

    # Вывод информации хоста, порта и пользователя.
    def __str__(self):
        show = '{0:>10}: {1}'.format('host', self.__host)
        show += '\n{0:>10}: {1}'.format('port', self.__port)
        show += '\n{0:>10}: {1}'.format('username', self.__username)
        return show

    # Деструктор для закрытия соединения с ftp-сервером.
    def __del__(self):
        try:
            # Закрываем соединение.
            self.__conn.quit()
        except ftplib.all_errors as err:
            print(err)
        except AttributeError as err:
            print('Сервер не подключен.')


if __name__ == '__main__':
    FILE_COPY_FTP = FileCopyFTP()
    # Читаем конфигурационный файл формата json.
    FILE_COPY_FTP.read_json_file()
    # Устанавливаем соединение с ftp-сервером.
    FILE_COPY_FTP.connect_server()
    # Копируем файлы на ftp-сервер.
    FILE_COPY_FTP.copy_to_server()
