import hashlib

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum
from datetime import datetime
from webapp import db, app


class BaseModel(db.Model):
    __abstract__ = True
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ENUMS
class Role(RoleEnum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    MANAGER = "MANAGER"


class OrderStatus(RoleEnum):
    NEWORDER = "NEWORDER"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"


class PaymentStatus(RoleEnum):
    UNPAID = "UNPAID"
    PAID = "PAID"


class FoodType(RoleEnum):
    APPETIZER = "APPETIZER"
    MAIN = "MAIN"
    DESERT = "DESERT"


class BeverageType(RoleEnum):
    SOFTDRINK = "SOFTDRINK"
    DRINKINGWATER = "DRINKINGWATER"
    COFFEE = "COFFEE"
    JUICE = "JUICE"


# MODELS
class User(BaseModel, UserMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20), nullable=False, unique=True)
    address = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=False, )
    role = Column(Enum(Role), default=Role.CUSTOMER)

    reviews = relationship('Review', backref='user', lazy=True)
    orders = relationship('Order', backref='user', lazy=True)


class Review(BaseModel):
    id = Column(Integer, primary_key=True)
    content = Column(String(255), nullable=False)
    rate = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)


class Order(BaseModel):
    id = Column(Integer, primary_key=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.NEWORDER)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    order_details = relationship('OrderDetail', backref='order', lazy=True)
    payment = relationship('Payment', backref='order', uselist=False)


class OrderDetail(BaseModel):
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, default=1)
    note = Column(String(255))

    cuisine_id = Column(Integer, ForeignKey('cuisine.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)


class Payment(BaseModel):
    id = Column(Integer, primary_key=True)
    total = Column(Float, default=0)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID)

    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)


class CuisineType(BaseModel):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    cuisines = relationship('Cuisine', backref='cuisine_type', lazy=True)


class Cuisine(BaseModel):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String(255))
    description = Column(String(255))
    status = Column(Boolean, default=True)
    count = Column(Integer, default=0)

    cuisine_type_id = Column(Integer, ForeignKey('cuisine_type.id'), nullable=False)
    food_type = Column(Enum(FoodType))
    beverage_type = Column(Enum(BeverageType))

    order_details = relationship('OrderDetail', backref='cuisine', lazy=True)


class Restaurant(BaseModel):
    id = Column(Integer, primary_key=True)
    location = Column(String(255))
    type = Column(String(100))
    name = Column(String(100))
    introduce = Column(String(255))

    reviews = relationship('Review', backref='restaurant', lazy=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Tạo user admin
        admin = User(
            name='Admin',
            username='admin',
            password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
            email='admin@example.com',
            phone='0909000000',
            address='123 Admin St',
            avatar='https://via.placeholder.com/150',
            role=Role.ADMIN
        )
        db.session.add(admin)

        # Tạo restaurant
        res1 = Restaurant(name='Bún Bò Huế', type='Quán ăn', location='TP.HCM', introduce='Đặc sản Huế ngon')
        res2 = Restaurant(name='Cơm Tấm Ba Ghiền', type='Nhà hàng', location='Quận 3', introduce='Cơm tấm nổi tiếng')
        db.session.add_all([res1, res2])

        # Tạo cuisine type
        ct1 = CuisineType(name='Món chính')
        ct2 = CuisineType(name='Đồ uống')
        db.session.add_all([ct1, ct2])
        db.session.flush()  # để lấy id

        # Tạo cuisine
        c1 = Cuisine(
            name='Bún Bò',
            price=45000,
            image='https://example.com/bunbo.jpg',
            description='Đậm vị Huế',
            count=10,
            cuisine_type_id=ct1.id,
            food_type=FoodType.MAIN
        )
        c2 = Cuisine(
            name='Trà Đào',
            price=15000,
            image='https://example.com/tradao.jpg',
            description='Mát lạnh',
            count=20,
            cuisine_type_id=ct2.id,
            beverage_type=BeverageType.JUICE
        )
        db.session.add_all([c1, c2])
        db.session.flush()

        # Tạo review
        r1 = Review(content='Ngon tuyệt!', rate=5, user_id=admin.id, restaurant_id=res1.id)
        r2 = Review(content='Ổn, giá hợp lý', rate=4, user_id=admin.id, restaurant_id=res2.id)
        db.session.add_all([r1, r2])

        # Tạo đơn hàng + chi tiết
        order = Order(user_id=admin.id, created_date=datetime.now(), status=OrderStatus.PROCESSING)
        db.session.add(order)
        db.session.flush()

        detail1 = OrderDetail(order_id=order.id, cuisine_id=c1.id, quantity=2, note='Ít cay')
        detail2 = OrderDetail(order_id=order.id, cuisine_id=c2.id, quantity=1, note='Ít đá')
        db.session.add_all([detail1, detail2])

        # Tạo thanh toán
        payment = Payment(order_id=order.id, total=105000, status=PaymentStatus.PAID)
        db.session.add(payment)

        db.session.commit()
        print("Đã tạo dữ liệu mẫu thành công!")
