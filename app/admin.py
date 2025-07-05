from flask import redirect
from flask_admin import Admin, expose, AdminIndexView, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from app import app, db
from models import User, CuisineType, Cuisine, Restaurant, Review, Order, OrderDetail, Payment
from models import Role

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

# Tạo đối tượng admin
admin = Admin(app=app, name='OUFood Admin', template_mode='bootstrap4', index_view=MyAdminIndexView())

# Chỉ dành cho ADMIN truy cập
class AuthenticatedAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')


# login
class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')

# logout
class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


# Thống kê
class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')  # Bạn cần tạo file templates/admin/stats.html

# Thêm model vào admin
admin.add_view(AuthenticatedAdminView(User, db.session, name="Người dùng"))
admin.add_view(AuthenticatedAdminView(Restaurant, db.session, name="Nhà hàng"))
admin.add_view(AuthenticatedAdminView(CuisineType, db.session, name="Loại món ăn"))
admin.add_view(AuthenticatedAdminView(Cuisine, db.session, name="Món ăn"))
admin.add_view(AuthenticatedAdminView(Review, db.session, name="Đánh giá"))
admin.add_view(AuthenticatedAdminView(Order, db.session, name="Đơn hàng"))
admin.add_view(AuthenticatedAdminView(OrderDetail, db.session, name="Chi tiết đơn hàng"))
admin.add_view(AuthenticatedAdminView(Payment, db.session, name="Thanh toán"))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
