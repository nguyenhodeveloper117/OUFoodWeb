from flask import redirect
from flask_admin import Admin, expose, AdminIndexView, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from app import app, db
from models import *

# Trang chủ admin
class MyAdminIndexView(AdminIndexView):
    @expose('/')
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
        return self.render('admin/stats.html')

# ====== CUSTOM ADMIN VIEWS WITH SEARCH, FILTER, SORT ======
class UserAdminView(AuthenticatedAdminView):
    column_list = ['id', 'name', 'username', 'email', 'phone', 'role']
    column_searchable_list = ['name', 'username', 'email', 'phone']
    column_filters = ['role']
    column_sortable_list = ['id', 'name', 'username']

class CuisineAdminView(AuthenticatedAdminView):
    column_list = ['id', 'name', 'price', 'status', 'count', 'food_type', 'beverage_type', 'cuisine_type']
    column_searchable_list = ['name', 'description']
    column_filters = ['food_type', 'beverage_type', 'status']
    column_sortable_list = ['id', 'price', 'count']

class CuisineTypeAdminView(AuthenticatedAdminView):
    column_list = ['id', 'name']
    column_searchable_list = ['name']
    column_sortable_list = ['id', 'name']

class RestaurantAdminView(AuthenticatedAdminView):
    column_list = ['id', 'name', 'type', 'location']
    column_searchable_list = ['name', 'location']
    column_sortable_list = ['id', 'name']

class ReviewAdminView(AuthenticatedAdminView):
    column_list = ['id', 'content', 'rate', 'user_id', 'restaurant_id']
    column_searchable_list = ['content']
    column_filters = ['rate', 'user_id', 'restaurant_id']
    column_sortable_list = ['id', 'rate']

class OrderAdminView(AuthenticatedAdminView):
    column_list = ['id', 'user_id', 'status', 'created_date']
    column_filters = ['status', 'user_id']
    column_sortable_list = ['id', 'created_date']

class OrderDetailAdminView(AuthenticatedAdminView):
    column_list = ['id', 'order_id', 'cuisine_id', 'quantity', 'note']
    column_filters = ['order_id', 'cuisine_id']
    column_sortable_list = ['id', 'quantity']

class PaymentAdminView(AuthenticatedAdminView):
    column_list = ['id', 'order_id', 'total', 'status']
    column_filters = ['status']
    column_sortable_list = ['id', 'total']

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
