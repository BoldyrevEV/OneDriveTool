import argparse
import os
import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer

client_secret = ''
client_id = ''
redirect_uri = 'http://localhost:8000/'
scopes = ['onedrive.readwrite']


class OneDriveTool:
    """Класс создания консольной утилиты для oneDrive"""

    def __init__(self, client_secret, client_id, redirect_uri, scopes):
        """Конструктор

        :param client_secret: Пароль или открытый ключ
        :param client_id: Код приложения
        :param redirect_uri: URL-адреса перенаправления
        :param scopes: Область аутентификации
        """
        self.client_secret = client_secret
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scopes = scopes

        parser = self.create_parser()
        namespace = parser.parse_args()

        client = onedrivesdk.get_default_client(client_id=self.client_id, scopes=self.scopes)
        auth_url = client.auth_provider.get_auth_url(self.redirect_uri)
        code = GetAuthCodeServer.get_auth_code(auth_url, self.redirect_uri)
        client.auth_provider.authenticate(code, self.redirect_uri, self.client_secret)

        if namespace.command == "put":
            self.put_file(namespace.dst_path, namespace.src_path, client)

        if namespace.command == "get":
            self.get_file(namespace.dst_path, namespace.src_path, client)

    def create_parser(self):
        """Метод создания парсера

        :return: экземпляр класса ArgumentParser
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('command', nargs='?')
        parser.add_argument('src_path', nargs='?')
        parser.add_argument('dst_path', nargs='?')
        return parser

    def put_file(self, dst_path, src_path, client):
        """Медот загрузки файла в oneDrive на основе полученных данных:

        :param dst_path: путь, где лежит загружаемый файл
        :param src_path: имя загружаемого файла (с расширением)
        :param client: обьект с client_id и scopes
        """
        fileName = os.path.splitext(src_path)
        for folder in os.listdir(dst_path):
            if src_path == folder:
                returned_item = client.item(drive='me', id='root').children[src_path].upload(
                    "./" + fileName[0] + fileName[1])
                break

    def get_file(self, dst_path, src_path, client):
        """Метод скачивания файла из oneDrive на основе полученных данных:

        :param dst_path: путь, куда необходимо скачать файл
        :param src_path: имя загружаемого файла (с расширением)
        :param client: обьект с client_id и scopes
        """
        fileName = os.path.splitext(src_path)
        items = client.item(drive='me', id='root').children.request().get()
        for folder in items:
            if src_path == folder.name:
                root_folder = client.item(drive='me', id='root').children.get()
                client.item(drive='me', id=folder.id).download(dst_path + fileName[0] + fileName[1])
                break


tool = OneDriveTool(client_secret, client_id, redirect_uri, scopes)
