# Приложение Sinchronizer_v.01
## Настройка 
* Чтобы настроить приложение создайте файл `.env` в корневой папке с приложением
* В этом файле нужно прописать `зависимости` от вашей локальной папки к папке в облачном хранилище
---
* Cодержимое файла должно выглядень примерно следующим образом:
* Вносите свои изменения после знака `=` остальное должно остаться `без` изменений
```TOKEN= # ваш токен приложения
LOCAL_PATH=Z:\work_local\   # В этой строке вы указываете путь в локальной папке
VIRTUAL_PATH=Work   # В этой строке вы указываете название папки в облачном хранилище
SINCHRONIZATION_PERIOD=10   # В этой строке вы указываете время в секундах (раз в какое время данные будут обновляться)
LOG_PATH=Z:\work_local\123\log.log   # В этой строке вы указываете путь к локальной папке где будется храниться файл с логом программы
```
## Запуск
* После того как вы создали файл и прописали зависимости можете запустить файл `Start_sinchronizer.bat`
* Если вы все сделали верно программа проверит файл с зависимостями и начнет первую синхронизацию
* Если вы допустили ошибку программа вам об этом сообщит и укажет на параметр, где допущена ошибка
* После того как вы исправили файл настроек перезапустите файл для запуска приложения
