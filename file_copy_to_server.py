import os
import json
import ftplib
import threading


# Класс для копирования файлов с ПК на FTP-сервер.
class FileCopyFTP:
    def __init__(self, thead_count=os.cpu_count()*5):
        self.__host = ''
        self.__port = 21
        self.__username = ''
        self.__password = ''
        self.__paths = []
        self.__thead_count = thead_count

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
            conn = ftplib.FTP()
            conn.connect(self.__host, self.__port)
        # Обработка исключения, если соединение не прошло.
        except ftplib.all_errors as err:
            print(err)
            exit(1)
        # Если соединение установлено.
        else:
            try:
                # Авторизация пользователя.
                conn.login(self.__username, self.__password)
            # Обработка исключения, если логин или пароль не верный.
            except ftplib.error_perm as err:
                print(err)
                exit(1)
            else:
                return conn

    # Метод для копирования файла на ftp-сервер.
    def copy_file_to_server(self, conn, source_path, ftp_path):
        try:
            # Открываем файл копируемого на чтение в бинарном режиме.
            with open(source_path, 'rb') as source_file:
                # Отправляем файл на ftp-сервер.
                conn.storbinary('STOR ' + ftp_path, source_file)
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

    # Метод для закрытия соединения с ftp-сервером.
    def quit_server(self, conn):
        try:
            # Закрываем соединение.
            conn.quit()
        except ftplib.all_errors as err:
            print(err)
        except AttributeError:
            print('Сервер не подключен.')

    # Метод для копирования определенного количества файлов.
    def thread_copy_files(self, paths_gap):
        # Для каждого потока подключаемся к ftp-серверу.
        conn = self.connect_server()
        # Копируем часть файлов на ftp-сервер
        for file in paths_gap:
            self.copy_file_to_server(conn, file['source_path'],
                                     file['ftp_path'])
        # Закрываем соединение.
        self.quit_server(conn)

    # Метод для перебора всех файлов.
    def threads_start(self):
        # Создаем список потоков.
        threads_list = []
        # Начальная позиция списка.
        bgn = 0
        # Примерное количество файлов в потоке.
        paths_div = len(self.__paths) // self.__thead_count
        paths_mod = len(self.__paths) % self.__thead_count
        # Разбиваем список файлов на количество потоков.
        for i in range(self.__thead_count):
            if paths_mod:
                end = bgn + paths_div + 1
                paths_mod -= 1
            else:
                end = bgn + paths_div
            # Инициализируем поток, отправляем промежуток файлов.
            thread_temp = threading.Thread(target=self.thread_copy_files,
                                           args=(self.__paths[bgn: end],))
            # Добавляем поток в список
            threads_list.append(thread_temp)
            # Запускаем поток
            thread_temp.start()
            bgn = end
            # Если достигнут конец списка, то прекратить создание потоков.
            if bgn >= len(self.__paths):
                break

        # Дожидаемся конца всех потоков.
        for thread_temp in threads_list:
            thread_temp.join()

    # Вывод информации хоста, порта и пользователя.
    def __str__(self):
        show = '{0:>10}: {1}'.format('host', self.__host)
        show += '\n{0:>10}: {1}'.format('port', self.__port)
        show += '\n{0:>10}: {1}'.format('username', self.__username)
        return show


if __name__ == '__main__':
    FILE_COPY_FTP = FileCopyFTP()
    # Читаем конфигурационный файл формата json.
    FILE_COPY_FTP.read_json_file()
    # Устанавливаем соединение с ftp-сервером.
    # Запускаем потоки для копирования файлов на ftp-сервер.
    FILE_COPY_FTP.threads_start()
