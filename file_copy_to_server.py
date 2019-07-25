import json
import ftplib
import threading


# Класс для копирования файлов с ПК на FTP-сервер.
class FileCopyFTP:
    def __init__(self):
        self.__host = ''
        self.__port = 21
        self.__username = ''
        self.__password = ''
        self.__paths = []
        self.__conn = ftplib.FTP()
        # Синхронизация доступа.
        self.__lock_thread = threading.Lock()

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

    # Метод для копирования файла на ftp-сервер.
    def copy_file_to_server(self, source_path, ftp_path):
        # Блокировка для других потоков.
        with self.__lock_thread:
            try:
                # Открываем файл копируемого на чтение в бинарном режиме.
                with open(source_path, 'rb') as source_file:
                    # Отправляем файл на ftp-сервер.
                    self.__conn.storbinary('STOR ' + ftp_path,
                                           source_file)
            # Обработка исключения, если копируемый файл не найден.
            except FileNotFoundError:
                print('Файл не найден ', source_path)
            # Обработка исключения, если указана папка, а не файл.
            except IsADirectoryError:
                print('Это не файл, а папка ', source_path)
                # Обработка исключения, если возникла ошбика ftp-сервера.
            except ftplib.error_perm as err:
                print('Ошибка: ', err)
            # Обработка исключения, если возникла другая ошибка файла.
            except OSError as err:
                print('Ошибка:', err)

            # Если файл успешно скопирован на ftp-сервер.
            else:
                print('Успешно скопирован файл:', source_path)

    # Метод для перебора всех файлов.
    def threads_copy_files(self):
        # Список всех потоков
        thread_list = []
        # Перебор всех файлов, которые должны скопироваться на ftp-сервер.
        for file in self.__paths:
            # Инициализируем поток
            thread_temp = threading.Thread(
                target=self.copy_file_to_server,
                name=file['source_path'],
                args=(file['source_path'], file['ftp_path'])
            )
            # Добавляем поток в список
            thread_list.append(thread_temp)
            # Запуск потока
            thread_temp.start()

        # Дожидаемся конца всех потоков
        for thread_temp in thread_list:
            thread_temp.join()

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
    # Запускаем потоки для копирования файлов на ftp-сервер.
    FILE_COPY_FTP.threads_copy_files()
