from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Product

# Подключение к БД (те же данные, что в alembic.ini)
DATABASE_URL = "postgresql://postgres:Adler272@localhost:5432/TRSP_KR4"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Добавляем две записи
product1 = Product(title="Ноутбук", price=50000, count=10)
product2 = Product(title="Мышь", price=1500, count=50)

session.add_all([product1, product2])
session.commit()

print("✅ Добавлено 2 продукта")
session.close()