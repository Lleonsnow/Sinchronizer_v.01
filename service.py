from headers_params_links_errors import errors
from typing import Set, Tuple, Optional
from functools import reduce
from time import sleep
import os


class Checker:
    def __init__(self, local, virtual, file_log, token, timer, logger):
        self.logger = logger
        self.params = {1: local,
                       2: virtual,
                       3: file_log,
                       4: token,
                       5: timer}

    def validate(self):
        if not os.path.exists(self.params[1]):
            self.logger.error('[-] Путь к локальной директории должен быть строкой вида'
                              ' X:\\[название папки]\\... либо не указан\\не существует')
            return False

        else:
            self.logger.info('[+] Путь к локальной директории корректный')
            sleep(0.8)

        if not self.params[2]:
            self.logger.error('[-] Путь к директории на облачном хранилище должен быть строкой вида'
                              ' directory... либо не указан')
            return False

        else:
            self.logger.info('[+] Путь к виртуальной директории корректный')
            sleep(0.8)

        if not self.params[3] and not os.path.exists(self.params[3]):
            self.logger.error('[-] Путь к файлу лога отсутствует или не существует')
            return False

        else:
            self.logger.info('[+] Путь к файлу лога корректен')
            sleep(0.8)

        if not self.params[4]:
            self.logger.error('[-] Токен приложения отсутствует')
            return False

        else:
            self.logger.info('[+] Значение "токен" присутствует')
            sleep(0.8)

        if not self.params[5]:
            self.logger.error('[-] Период для синхронизации должен быть целым числом в секундах [10] либо не указан')
            return False

        else:
            self.logger.info('[+] Период синхронизации указан\n')
            sleep(0.8)

        return True


def collect_files(dir_local) -> Tuple[Set[Tuple[int, str]], Set[str]]:
    names = [file for file in os.listdir(dir_local)]
    time_change = [os.stat(dir_local + item).st_mtime for item in os.listdir(dir_local)]
    files = set(zip(names, time_change))

    return files, set(names)


def search_difference(new, old) -> Optional[Tuple[Set[str], Set[str], Set[str]]]:
    difference_all: Set = set()

    difference_new = new[1].difference(old[1])
    difference_old = old[1].difference(new[1])

    difference_all.update(difference_new)
    difference_all.update(difference_old)

    intersection_files = new[0].symmetric_difference(old[0])
    result = [*reduce(lambda x, y: x + (y[:1] if y[0] not in difference_all else ()), intersection_files, ())]
    update = set(result)

    return difference_new, difference_old, update


def error_handler(logger, status_code: int) -> None:
    if status_code == 401:
        logger.error('[-] ' + errors[401])

    elif status_code == 409:
        logger.error('[-] ' + errors[409])

    elif status_code in [403, 507]:
        logger.error('[-] ' + errors[(403, 507)])

    elif status_code == 413:
        logger.error('[-] ' + errors[413])

    elif status_code in [423, 503]:
        logger.error('[-] ' + errors[423, 503])
