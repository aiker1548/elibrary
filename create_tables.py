from sqlalchemy import create_engine
from database_setup import Base, Book, Author

# Подключение к базе данных
engine = create_engine('sqlite:///books-collections.db', connect_args={'check_same_thread': False})

# Создание всех таблиц, определённых в Base
Base.metadata.create_all(engine)

print("Таблицы успешно созданы!")