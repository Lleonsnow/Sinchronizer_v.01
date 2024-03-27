from requests.exceptions import ConnectionError, ReadTimeout
from typing import Dict, Set, Optional, Tuple, Union, List
import headers_params_links_errors as req_tools
from settings import SiteSettings
from requests import Response
from loguru import logger
from time import sleep
import requests
import service
import sys
import os


class Sinchronizer:
    def __init__(
        self,
        url: str,
        token: str,
        registration_tools,
        dir_virtual: str,
        dir_local: str,
        timer,
    ) -> None:
        self.url = url
        self.auth_headers = registration_tools.auth_headers
        self.dir_check = registration_tools.dir_check
        self.files_params_check = registration_tools.files_params_check
        self.files_params_upload = registration_tools.files_params_upload
        self.files_params_delete = registration_tools.files_params_delete
        self.links = registration_tools.links
        self.errors = registration_tools.errors
        self.timer = timer
        self.dir_virtual = dir_virtual
        self.dir_local = dir_local
        self.token = token

    def isinstance_virtual_dir(self) -> Response:
        while True:
            try:
                response = requests.get(
                    url=self.url + self.links["resources"],
                    headers=self.auth_headers,
                    params=self.dir_check,
                )
            except (ConnectionError, ReadTimeout):
                logger_01.error(
                    "[-] Отсутствует подключение к интернету, ожидаю соединения..."
                )
                sleep(self.timer)
                continue

            return response

    def create_virtual_dir(self) -> bool:
        try:
            response = self.isinstance_virtual_dir()

            if response.status_code not in [200, 201, 202]:
                response = requests.put(
                    url=self.url + self.links["resources"],
                    headers=self.auth_headers,
                    params=self.dir_check,
                )

        except (ConnectionError, ReadTimeout):
            logger_01.error(
                f"[-] Отсутствует подключение к интернету."
                f" Рабочая директория [{self.dir_virtual}] не была создана"
            )
            sleep(0.5)
            logger_01.info("[+] Ожидаю следующего периода синхронизации...")
            return False

        if response.status_code == 201:
            logger_01.info(
                f"[+] Рабочая директория [{self.dir_virtual}] в облачном хранилище успешно создана"
            )
            return True

        logger_01.info(
            f"[-] Рабочая директория [{self.dir_virtual}]"
            f" в облачном хранилище с таким именем уже существует"
        )
        return True

    def create_data(self, current, path) -> Union[bool, Dict[str, Tuple[str, bytes]]]:
        if not os.path.isfile(path + current):
            return False

        elif not os.path.exists(path + current):
            return False

        try:
            with open(self.dir_local + current, "rb") as file:
                f_bytes = file.read()
        except PermissionError:
            logger_01.error(f"[-] У вас нет прав для обработки файла: [{current}]")
            return False

        data = {"file": (current, f_bytes)}

        return data

    def load(self, path: str, files: Union[List, Set]) -> None:
        files: List[str] = list(files)
        old_path: str = self.files_params_upload["path"]
        head: int = 0
        tail: int = len(files)

        if self.isinstance_virtual_dir().status_code not in [200, 201, 202]:
            logger_01.info(
                f"[-] Отсутствует виртуальная директория [{self.dir_virtual}], приступаю к созданию"
            )
            self.create_virtual_dir()

        while head < tail:
            current: str = files[head]
            data = self.create_data(current, path)

            if not data:
                head += 1
                continue

            self.files_params_upload["path"] += f"/{current}"

            try:
                get_upload_link = requests.get(
                    self.url + self.links["resources"] + self.links["upload"],
                    headers=self.auth_headers,
                    params=self.files_params_upload,
                )

                if get_upload_link.status_code in [200, 201, 202]:
                    upload_url = get_upload_link.json()["href"]
                    requests.post(url=upload_url, files=data)
                    logger_01.info(
                        f"[+] Файл [{current}] успешно загружен в облачное хранилище"
                    )

                else:
                    service.error_handler(logger_01, get_upload_link.status_code)

            except (ConnectionError, ReadTimeout):
                self.files_params_upload["path"] = old_path
                logger_01.error(
                    f"[-] Отсутствует подключение к интернету. Файл [{current}] не загружен"
                )
                sleep(0.5)
                logger_01.info("[+] Ожидаю соединения...")
                sleep(self.timer)
                continue

            self.files_params_upload["path"] = old_path
            head += 1

        else:
            logger_01.info(
                "[+] Файлы загружены в облачное хранилище, ожидаю синхронизацию..."
            )

    def reload(self, path: str, files: Set) -> None:
        files: List[str] = list(files)
        old_path: str = self.files_params_upload["path"]
        copy_for_overwrite: Dict[str, str] = self.files_params_upload.copy()
        copy_for_overwrite["overwrite"] = "true"
        head: int = 0
        tail: int = len(files)

        if self.isinstance_virtual_dir().status_code not in [200, 201, 202]:
            logger_01.info(
                f"[-] Отсутствует виртуальная директория [{self.dir_virtual}], приступаю к созданию"
            )
            self.create_virtual_dir()

        while head < tail:
            current = files[head]
            data = self.create_data(current, path)

            if not data:
                head += 1
                continue

            copy_for_overwrite["path"] += f"/{current}"

            try:
                get_upload_link = requests.get(
                    self.url + self.links["resources"] + self.links["upload"],
                    headers=self.auth_headers,
                    params=copy_for_overwrite,
                )

                if get_upload_link.status_code in [200, 201, 202]:
                    upload_url = get_upload_link.json()["href"]
                    requests.post(url=upload_url, files=data)
                    logger_01.info(
                        f"[+] Файл [{current}] успешно перезаписан в облачное хранилище"
                    )

                else:
                    service.error_handler(logger_01, get_upload_link.status_code)

            except (ConnectionError, ReadTimeout):
                copy_for_overwrite["path"] = old_path
                logger_01.error(
                    f"[-] Отсутствует подключение к интернету. Файл [{current}] не перезаписан"
                )
                sleep(0.5)
                logger_01.info("[+] Ожидаю следующего периода синхронизации...")
                sleep(self.timer)
                continue

            copy_for_overwrite["path"] = old_path
            head += 1

        else:
            logger_01.info(
                "[+] Файлы перезаписаны в облачное хранилище, ожидаю синхронизацию..."
            )

    def delete(self, files: Set) -> None:
        files: List[str] = list(files)
        old_path = self.files_params_delete["path"]
        head: int = 0
        tail: int = len(files)

        while head < tail:
            file = files[head]
            self.files_params_delete["path"] += f"/{file}"

            try:
                response = requests.delete(
                    self.url + self.links["resources"],
                    headers=self.auth_headers,
                    params=self.files_params_delete,
                )

                if response.status_code in [200, 202, 204]:
                    logger_01.info(f"[+] Файл [{file}] успешно удален")

                else:
                    service.error_handler(logger_01, response.status_code)

            except (ConnectionError, ReadTimeout):
                self.files_params_delete["path"] = old_path
                logger_01.error(
                    f"[-] Отсутствует подключение к интернету. Файл [{file}] не был удален"
                )
                sleep(0.5)
                logger_01.info("[+] Ожидаю соединения...")
                sleep(self.timer)
                continue

            self.files_params_delete["path"] = old_path
            head += 1

        else:
            logger_01.info(
                "[+] Удаленные файлы удалены из облачного хранилища, ожидаю синхронизацию..."
            )

    def get_info(self) -> Optional[Set[str]]:
        virtual_files: Set[str] = set()
        try:
            response = requests.get(
                url=self.url + self.links["resources"],
                headers=self.auth_headers,
                params=self.files_params_check,
            )
        except ConnectionError:
            logger_01.error(
                "[-] Отсутствует подключение к интернету. Данные не получены"
            )
            sleep(1)
            logger_01.info("[+] Ожидаю следующего периода синхронизации...")
            return

        if response.status_code != 200:
            logger_01.error("[-] Ответ сервера вернулся с ошибкой. Данные не получены")
            return

        files_virtual = response.json()["_embedded"]["items"]
        logger_01.info("[+] Содержимое папки в облачном хранилище:")

        for file in files_virtual:
            if not file["type"] == "dir":
                virtual_files.add(file["name"])
                logger_02.info(file["name"])

        return virtual_files

    def monitor(self) -> None:
        while True:
            logger_01.info(
                f"[+] Программа начинает работу с директорией [{self.dir_local}]"
            )
            response = self.create_virtual_dir()

            if response:
                self.load(self.dir_local, os.listdir(self.dir_local))

                logger_01.info("[+] Первая синхронизация завершена")
                old_changes = service.collect_files(self.dir_local)
                break

            sleep(self.timer)

        self.process_sinchronization(old_changes)

    def process_sinchronization(self, old_changes: Tuple):
        while True:
            sleep(self.timer)
            new_changes = service.collect_files(self.dir_local)
            new, delete, update = service.search_difference(new_changes, old_changes)

            if update:
                logger_01.info(
                    "[+] Обнаружены измененные файлы, перезаписываю в облачное хранилище"
                )
                self.reload(self.dir_local, update)

            if new:
                logger_01.info(
                    "[+] Обнаружены новые файлы, загружаю в облачное хранилище"
                )
                self.load(self.dir_local, new)

            if delete:
                logger_01.info(
                    "[+] Обнаружены удаленные файлы, удаляю в облачном хранилище"
                )
                self.delete(delete)

            if not new and not delete and not update:
                logger_01.info(
                    "[-] Новых файлов или изменений не обнаружено, ожидаю синхронизацию..."
                )

            old_changes = new_changes


if __name__ == "__main__":
    secret = SiteSettings()
    file_log = secret.log_path.get_secret_value()
    logger.remove(handler_id=0)
    logger_01 = logger.bind(name="01")
    logger_02 = logger.bind(name="02")

    logger_01.add(
        sink=sys.stdout,
        level="DEBUG",
        colorize=True,
        format="<b><i>Sinchronizer</i></b>"
        " <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
        " <r><level>{level}</level></r> <b><i>{message}</i></b>",
        filter=lambda record: True if record["extra"]["name"] == "01" else False,
    )

    logger_01.add(
        sink=file_log,
        mode="a+",
        level="DEBUG",
        colorize=True,
        format="Sinchronizer" " {time:YYYY-MM-DD HH:mm:ss.SSS}" " {level} {message}",
        filter=lambda record: True if record["extra"]["name"] == "01" else False,
    )

    logger_02.add(
        sink=sys.stderr,
        level="DEBUG",
        colorize=True,
        format="<b><y>{message}</y></b>",
        filter=lambda record: True if record["extra"]["name"] == "02" else False,
    )

    base_url: str = "https://cloud-api.yandex.net/v1/disk/"
    dir_virtual_path: str = secret.virtual_path.get_secret_value().strip()
    dir_local_path: str = secret.local_path.get_secret_value().strip()
    timeout: str = secret.period.get_secret_value()
    Token: str = secret.TOKEN.get_secret_value().strip()
    validate = service.Checker(
        dir_local_path, dir_virtual_path, file_log, Token, timeout, logger_01
    )
    is_launch = validate.validate()

    if not is_launch:
        sys.exit()

    sinchronizer = Sinchronizer(
        base_url, Token, req_tools, dir_virtual_path, dir_local_path, int(timeout)
    )
    # sinchronizer.get_info()
    sinchronizer.monitor()
