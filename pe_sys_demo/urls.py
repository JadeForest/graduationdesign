"""mydemo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.shortcuts import render

from .views import user, staff, item, event, record, account, admin

urlpatterns = [
    path('debug/', account.debug),

    # 登录
    path("login/", account.LoginView.as_view()),
    path("logout/", account.logout),

    # 管理员用户相关
    path("admin/", admin.admin_pg),
    path("admin/list/", admin.AdminListView.as_view()),
    path("admin/list/add/", admin.AddAdminView.as_view()),
    path("admin/list/edit/", admin.EditAdminView.as_view()),
    path("admin/list/detail/", admin.GetAdminDetail.as_view()),
    path("admin/list/del/", account.DelAccountView.as_view()),

    # 体检用户相关
    path("user/<int:uid>/", user.user_pg),
    path("user/<int:uid>/edit/", user.UserInfoEdit.as_view()),
    path("user/<int:uid>/events/", user.UserEventList.as_view()),
    path("user/<int:uid>/pwd/", account.changepwd),
    path("user/<int:uid>/pwd/submit/", account.changepwd_submit),
    # 体检用户管理
    path("user/list/", user.UserListView.as_view()),
    path("user/list/users_upload/", user.upload_page),
    path("user/list/add/", user.AddUserView.as_view()),
    path("user/list/edit/", user.EditUserView.as_view()),
    path("user/list/detail/", user.GetUserDetail.as_view()),
    path("user/list/del/", account.DelAccountView.as_view()),
    path("user/list/reset/", user.reset_pwd),

    # 医务人员用户相关
    path("staff/<int:uid>/", staff.staff_pg),
    path("staff/<int:uid>/edit/", staff.StaffInfoEdit.as_view()),
    path("staff/<int:uid>/pwd/", account.changepwd),
    path("staff/<int:uid>/pwd/submit/", account.changepwd_submit),
    # 医务人员管理
    path("staff/list/", staff.StaffListView.as_view()),
    path("staff/list/add/", staff.AddStaffView.as_view()),
    path("staff/list/edit/", staff.EditStaffView.as_view()),
    path("staff/list/detail/", staff.GetStaffDetail.as_view()),
    path("staff/list/del/", account.DelAccountView.as_view()),
    path("staff/list/reset/", staff.reset_pwd),

    # 体检项目管理
    path("item/", item.ItemListView.as_view()),
    path("item/add/", item.AddItemView.as_view()),
    path("item/edit/", item.EditItemView.as_view()),
    path("item/detail/", item.ItemDetail.as_view()),
    path("item/del/", item.DelItemView.as_view()),
    # 体检类别管理
    path("itype/", item.ItypeListView.as_view()),
    path("itype/add/", item.AddItypeView.as_view()),
    path("itype/edit/", item.EditItypeView.as_view()),
    path("itype/detail/", item.ItypeDetail.as_view()),
    path("itype/del/", item.DelItypeView.as_view()),
    # 诊断结果管理
    path("diag/", item.DiagListView.as_view()),
    path("diag/add/", item.AddDiagView.as_view()),
    path("diag/edit/", item.EditDiagView.as_view()),
    path("diag/detail/", item.DiagDetail.as_view()),
    path("diag/del/", item.DelDiagView.as_view()),

    # 体检时间管理
    path("event/", event.EventListView.as_view()),
    path("event/add/", event.AddEventView.as_view()),
    path("event/del/", event.DelEventView.as_view()),
    path("event/lock/", event.lock_event),
    path("event/arc/", event.archive_event),
    path("event/detail/", event.EventDetail.as_view()),
    path("event/edit/", event.EditEventView.as_view()),

    # 体检人员安排管理
    path("event/<int:eid>/arr/", event.ArrListView.as_view()),
    path("event/<int:eid>/rec_table/", event.RecTableView.as_view()),
    path("event/<int:eid>/arr/choose/", event.ArrChooseView.as_view()),
    # path("event/<int:eid>/arr/choose_group/", event.arr_choose_group),
    path("event/<int:eid>/arr/choose/all/", event.ArrChooseAll.as_view()),
    path("event/<int:eid>/arr/choose/clear/", event.arr_choose_confirm),
    path("event/<int:eid>/arr/choose/submit/", event.arr_choose_confirm),
    path("event/<int:eid>/arr/choose/get_exist/", event.arr_choose_getexist),
    
    # 体检结果录入
    path("rec/input/", record.rec_input), # 从事件列表进入，跳转到这里
    path("rec/input/submit/", record.rec_submit), 
    path("rec/input/get_user/", record.get_uid), 
    path("rec/input/get_rec/", record.get_rec), 
    # 体检结果审核
    path("rec/review/", record.rec_review), # 从事件列表进入，跳转到这里
    path("rec/review/submit/", record.rec_review_submit), 
    path("rec/review/get_user/", record.get_uid), 
    # 体检结果查询
    path("rec/", record.record),
    path("rec/by_item/", record.RecordByItem.as_view()),
    path("rec/by_user/", user.UserListView.as_view())

]