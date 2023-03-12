# Как запустить проект
```mkdir Exchange-clone``` создать пустую папку  
```cd Exchange-clone``` перейти в папку  
```git clone https://github.com/makeevnikita/Exchange.git``` клонировать репозиторий  
```python3 -m venv venv``` создать виртуальное окружение  
```source venv/bin/activate``` активировать виртуальное окружение  
```pip install uvicorn``` установить ASGI-сервер  
```uvicorn Exchange.asgi:application``` запустить приложение  

# Структура проекта  
+cryptosite/  
+--cryptosite/  
+--------asgi.py  
+--------settings.py  
+--------urls.py  
+--------wsgi.py  
+--main/  
+--------migrations/  
+--------templates/    
+--------admin.py  
+--------exceptions.py  
+--------models.py  
+--------services.py  
+--------tests.py  
+--------urls.py  
+--------views.py  
+--media/  
+--------images/  
+---------------coins/  
+--static/  
+--------admin/  
+--------main/  
+---------------css/  
+---------------images/  
+---------------js/  
+--templates/  
db.sqlite3  
manage.py  
