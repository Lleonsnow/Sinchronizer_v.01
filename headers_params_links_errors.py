from typing import Dict
from settings import SiteSettings

secret = SiteSettings()

dir_check: Dict[str, ...] = {
    "path": secret.virtual_path.get_secret_value(),
    "fields": "name, type",
}

auth_headers: Dict[str, ...] = {
    "Authorization": "OAuth " + secret.TOKEN.get_secret_value(),
    "Accept-Language": "ru",
}

files_params_check: Dict[str, ...] = {
    "path": secret.virtual_path.get_secret_value(),
    # 'limit': '100',
    "offset": "0",
    "fields": "_embedded.items.name, _embedded.items.type, _embedded.items.modified",
    # 'media_type': 'text,image',
    "preview_crop": "false",
}

files_params_upload: Dict[str, ...] = {
    "path": secret.virtual_path.get_secret_value(),
    "overwrite": "false",
    "fields": "_embedded.items.name, _embedded.items.type, _embedded.items.modified",
}

files_params_delete: Dict[str, ...] = {
    "path": secret.virtual_path.get_secret_value(),
    "permanently": "true",
}

links: Dict[str, ...] = {
    "upload": "upload",
    "files": "files",
    "resources": "resources/",
    "trash": "trash/resource/",
}


errors: Dict[str, str] = {
    "UNAUTHORIZED": "Пользователь не авторизован, авторизуйтесь для следующей синхронизации",
    "CONFLICT": "Указанный путь не корректный, либо загружаемый файл уже существует в облачном хранилище",
    "FORBIDDEN": "Недостаточно места в облачном хранилище,"
    " либо API недоступно, попробуйте позже",
    "REQUEST_ENTITY_TOO_LARGE": "Загрузка невозможна, превышен максимальный размер файла",
    "LOCKED": "Сервис временно не доступен, ведутся тех. работы",
}
