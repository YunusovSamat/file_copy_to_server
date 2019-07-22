import json
import ftplib


class FileCopyFTP:
    def __init__(self):
        self.__ftp = ''
        self.__username = ''
        self.__password = ''
        self.__paths = list()

    def read_json_file(self, path='config.json'):
        try:
            with open(path, "r") as file:
                config_data = json.load(file)
                self.__ftp = config_data['ftp']
                self.__username = config_data['username']
                self.__password = config_data['password']
                self.__paths = config_data['paths']

        except FileNotFoundError:
            print('Файл не найден')
            exit(1)
        except IsADirectoryError:
            print('Это не файл, а папка')
        except OSError:
            print('Ошибка открытия файла')

    def connect_server(self):
        try:
            self.__conn = ftplib.FTP(self.__ftp, self.__username,
                                     self.__password)
        except ftplib.all_errors as err:
            print(err)
            exit(1)
        else:
            self.__conn.login()

    def copy_to_server(self):
        for f in self.__paths:
            try:
                with open(f['source_path'], 'rb') as source_file:
                    self.__conn.storbinary('STOR ' + f['ftp_path'],
                                           source_file)
            except FileNotFoundError:
                print('Файл не найден')
                exit(1)
            except IsADirectoryError:
                print('Это не файл, а папка')
            except OSError:
                print('Ошибка открытия файла')
            else:
                print('Файл', f['source_path'], 'успешно скопирован.')

    def __str__(self):
        show = 'ftp: ' + self.__ftp
        show += '\nusername: ' + self.__username

        return show

    def __del__(self):
        self.__conn.close()


if __name__ == '__main__':
    file_copy_ftp = FileCopyFTP()
    file_copy_ftp.read_json_file()
    file_copy_ftp.connect_server()
    file_copy_ftp.copy_to_server()
