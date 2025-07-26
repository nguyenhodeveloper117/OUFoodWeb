from datetime import timedelta
from flask import redirect, request
from flask_admin import Admin, expose, AdminIndexView, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from app import app, db, decorators
from sqlalchemy import func
from models import *

# Trang chủ admin
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    @decorators.logged_in_customer
    def index(self):
        return self.render('admin/index.html')

# Login chỉ cho ADMIN
class AuthenticatedAdminView(ModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')

# View có xác thực chung
class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')

# Logout admin
class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

# View thống kê
class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        restaurant_id = request.args.get('restaurant_id', type=int)
        from_date_str = request.args.get('from_date')
        to_date_str = request.args.get('to_date')

        today = datetime.today()
        default_from_date = today - timedelta(days=6)

        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else default_from_date
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else today

        # Lấy danh sách nhà hàng
        restaurants = Restaurant.query.all()
        if restaurant_id is None and restaurants:
            restaurant_id = restaurants[0].id

        # Truy vấn doanh thu theo ngày
        revenue_stats = db.session.query(
            func.date(Payment.created_date).label('date'),
            func.sum(Payment.total).label('total_revenue')
        ).join(Order).join(Restaurant) \
         .filter(
            Payment.status == PaymentStatus.PAID,
            Restaurant.id == restaurant_id,
            Payment.created_date >= from_date,
            Payment.created_date <= to_date
         ).group_by(func.date(Payment.created_date)) \
         .order_by(func.date(Payment.created_date)) \
         .all()

        labels = [r.date.strftime('%Y-%m-%d') for r in revenue_stats]
        values = [float(r.total_revenue) for r in revenue_stats]

        # Truy vấn số lượng đơn hàng
        order_count = db.session.query(func.count(Order.id)) \
            .join(Restaurant) \
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.created_date >= from_date,
                Order.created_date <= to_date
            ).scalar()

        return self.render('admin/stats.html',
                           labels=labels,
                           values=values,
                           restaurants=restaurants,
                           selected_restaurant=restaurant_id,
                           from_date=from_date.strftime('%Y-%m-%d'),
                           to_date=to_date.strftime('%Y-%m-%d'),
                           order_count=order_count)

# ====== CUSTOM ADMIN VIEWS WITH SEARCH, FILTER, SORT ======
class UserAdminView(AuthenticatedAdminView):
    column_list = ['id', 'name', 'username', 'password', 'email', 'phone', 'address', 'avatar', 'role', 'created_date', 'updated_date']
    column_searchable_list = ['id', 'name', 'username', 'email', 'phone']
    column_filters = ['role']
    column_sortable_list = ['id', 'name', 'username', 'email', 'phone', 'role', 'created_date', 'updated_date']

class CuisineAdminView(AuthenticatedAdminView):
    column_list = ['id', 'name', 'price', 'image', 'description', 'status', 'count', 'cuisine_type', 'food_type', 'beverage_type', 'created_date', 'updated_date']
    form_columns = ['name', 'price', 'image', 'description', 'status', 'count',
                    'cuisine_type', 'food_type', 'beverage_type']
    column_searchable_list = ['id', 'name', 'description']
    column_filters = ['status', 'food_type', 'beverage_type', 'cuisine_type_id']
    column_sortable_list = ['id', 'name', 'price', 'count', 'cuisine_type_id', 'created_date', 'updated_date']

class CuisineTypeAdminView(AuthenticatedAdminView):
    column_list = ['id', 'name', 'restaurant', 'created_date', 'updated_date']
    form_columns = ['name', 'restaurant', 'created_date', 'updated_date']
    column_searchable_list = ['id', 'name']
    column_sortable_list = ['id', 'name', 'created_date', 'updated_date']

class RestaurantAdminView(AuthenticatedAdminView):
    column_list = ['id', 'user', 'location', 'type', 'name', 'introduce', 'image', 'created_date', 'updated_date']
    form_columns = ['user', 'location', 'type', 'name', 'introduce', 'image', 'created_date', 'updated_date']
    column_searchable_list = ['id', 'name', 'location', 'type']
    column_sortable_list = ['id', 'name', 'type', 'location', 'created_date', 'updated_date']

class ReviewAdminView(AuthenticatedAdminView):
    column_list = ['id', 'content', 'rate', 'date', 'user', 'restaurant', 'created_date', 'updated_date']
    form_columns = ['content', 'rate', 'date', 'user', 'restaurant', 'created_date', 'updated_date']
    column_searchable_list = ['id', 'content']
    column_filters = ['rate', 'user_id', 'restaurant_id']
    column_sortable_list = ['id', 'rate', 'date', 'created_date', 'updated_date']

class OrderAdminView(AuthenticatedAdminView):
    column_list = ['id', 'status', 'user', 'restaurant', 'created_date', 'updated_date']
    form_columns = ['status', 'user', 'restaurant', 'created_date', 'updated_date']
    column_searchable_list = ['id', 'user_id']
    column_filters = ['status', 'user_id']
    column_sortable_list = ['id', 'status', 'user_id', 'created_date', 'updated_date']

class OrderDetailAdminView(AuthenticatedAdminView):
    column_list = ['id', 'quantity', 'note', 'cuisine', 'order', 'created_date', 'updated_date']
    form_columns = ['quantity', 'note', 'cuisine', 'order', 'created_date', 'updated_date']
    column_searchable_list = ['id', 'note']
    column_filters = ['cuisine_id', 'order_id']
    column_sortable_list = ['id', 'quantity', 'cuisine_id', 'order_id', 'created_date', 'updated_date']

class PaymentAdminView(AuthenticatedAdminView):
    column_list = ['id', 'total', 'status', 'order', 'created_date', 'updated_date']
    form_columns = ['total', 'status', 'order', 'created_date', 'updated_date']
    column_searchable_list = ['id', 'order_id']
    column_filters = ['status']
    column_sortable_list = ['id', 'total', 'order_id', 'created_date', 'updated_date']

# ====== KHỞI TẠO ADMIN ======
admin = Admin(app=app, name='OUFood Admin', template_mode='bootstrap4', index_view=MyAdminIndexView())

# Thêm các view
admin.add_view(UserAdminView(User, db.session, name="Người dùng"))
admin.add_view(RestaurantAdminView(Restaurant, db.session, name="Nhà hàng"))
admin.add_view(CuisineTypeAdminView(CuisineType, db.session, name="Loại món ăn"))
admin.add_view(CuisineAdminView(Cuisine, db.session, name="Món ăn"))
admin.add_view(ReviewAdminView(Review, db.session, name="Đánh giá"))
admin.add_view(OrderAdminView(Order, db.session, name="Đơn hàng"))
admin.add_view(OrderDetailAdminView(OrderDetail, db.session, name="Chi tiết đơn hàng"))
admin.add_view(PaymentAdminView(Payment, db.session, name="Thanh toán"))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
