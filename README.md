# Microservices python
- para iniciar o aplicativo:
```
pip install env
pip install fastapi uvicorn
pip install pipenv
pipenv shell
uvicorn orders.app:app --reload
```

- para iniciar o kitchen que utiliza o flask
```
 pipenv install flask-smorest
 pip install flask-smorest
 flask run --reload
```

- o orm utilizado é o sqlalchemy e o migration alembic
- para criar a pasta de migrations:
````
alembic init migrations
````
- para gerar as tabelas com base no orm
````
PYTHONPATH=`pwd` alembic revision --autogenerate -m "Initial migration"
````
- para aplicar
````
PYTHONPATH=`pwd` alembic upgrade heads
````