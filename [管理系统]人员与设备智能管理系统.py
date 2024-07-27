import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import csv
import time
import os

class PersonnelManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("智能人员管理系统")

        # 初始化用户数据
        self.users = [
            {"工号": "1", "密码": "1", "姓名": "刘亦菲", "性别": "女", "出生日期": "1987/9/9", "入职时间": "2012/1/1", "就职部门": "船舶管理", "职位级别": "11", "权限设置": "4", "状态": "空闲"},
            {"工号": "2", "密码": "2", "姓名": "杨幂", "性别": "女", "出生日期": "1986/9/12", "入职时间": "2014/4/1", "就职部门": "系统管理", "职位级别": "9", "权限设置": "5", "状态": "空闲"},
        ]

        # 初始化设备数据
        self.users2 = [
            {"设备编号": "10086", "设备类型": "手机", "生产厂家": "Apple", "额定功率": "1000W", "安装时间": "2024/7/20", "安装位置": "家里"},
            {"设备编号": "10000", "设备类型": "手机", "生产厂家": "XiaoMI", "额定功率": "7000W", "安装时间": "2023/8/16", "安装位置": "公司"},
        ]

        # 初始化基础资源
        self.users3 = [
            {"设备编号": "0001", "叶片参数": "3叶", "齿轮参数": "45 r/min", "发电机参数": "1000W"},
            {"设备编号": "0002", "叶片参数": "3叶", "齿轮参数": "60 r/min", "发电机参数": "2400W"},
            {"设备编号": "0003", "叶片参数": "3叶", "齿轮参数": "80 r/min", "发电机参数": "6000W"},
        ]

        self.weather_data = []
        self.declaration_data = []
        self.operation_data = []

        # 创建 Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True)

        # 创建页面
        self.frames = {}
        for title in ['人员信息管理', '设备信息管理', '气象信息管理', '设备运行管理', '维修活动管理', '基础资源管理', '设备信息']:
            frame = tk.Frame(self.notebook, width=800, height=400)
            frame.pack(fill='both', expand=True)
            self.notebook.add(frame, text=title)
            self.frames[title] = frame

        # 创建各页面的内容
        self.create_personnel_widgets()
        self.create_info()
        self.create_basic()
        self.create_log()
        self.create_weather_page()
        self.create_declaration_page()
        self.create_operation_page()

        # 实时时间显示
        self.update_time()

    def create_personnel_widgets(self):
        frame = self.frames['人员信息管理']
        # 工号
        tk.Label(frame, text="工号").grid(row=0, column=0, padx=10, pady=5)
        self.entry_id = tk.Entry(frame)
        self.entry_id.grid(row=0, column=1, padx=10, pady=5)

        # 密码
        tk.Label(frame, text="密码").grid(row=1, column=0, padx=10, pady=5)
        self.entry_password = tk.Entry(frame, show='*')
        self.entry_password.grid(row=1, column=1, padx=10, pady=5)

        # 姓名
        tk.Label(frame, text="姓名").grid(row=2, column=0, padx=10, pady=5)
        self.entry_name = tk.Entry(frame)
        self.entry_name.grid(row=2, column=1, padx=10, pady=5)

        # 性别
        tk.Label(frame, text="性别").grid(row=3, column=0, padx=10, pady=5)
        self.combo_gender = ttk.Combobox(frame, values=["男", "女"])
        self.combo_gender.grid(row=3, column=1, padx=10, pady=5)

        # 出生日期
        tk.Label(frame, text="出生日期").grid(row=4, column=0, padx=10, pady=5)
        self.entry_birth_date = tk.Entry(frame)
        self.entry_birth_date.grid(row=4, column=1, padx=10, pady=5)

        # 入职时间
        tk.Label(frame, text="入职时间").grid(row=5, column=0, padx=10, pady=5)
        self.entry_join_date = tk.Entry(frame)
        self.entry_join_date.grid(row=5, column=1, padx=10, pady=5)

        # 就职部门
        tk.Label(frame, text="就职部门").grid(row=6, column=0, padx=10, pady=5)
        self.entry_department = tk.Entry(frame)
        self.entry_department.grid(row=6, column=1, padx=10, pady=5)

        # 职位级别
        tk.Label(frame, text="职位级别").grid(row=7, column=0, padx=10, pady=5)
        self.entry_position_level = tk.Entry(frame)
        self.entry_position_level.grid(row=7, column=1, padx=10, pady=5)

        # 权限设置
        tk.Label(frame, text="权限设置").grid(row=8, column=0, padx=10, pady=5)
        self.entry_permission = tk.Entry(frame)
        self.entry_permission.grid(row=8, column=1, padx=10, pady=5)

        # 按钮
        self.btn_add = tk.Button(frame, text="新增", command=self.add_user)
        self.btn_add.grid(row=9, column=0, padx=10, pady=5)

        self.btn_update = tk.Button(frame, text="修改", command=self.update_user)
        self.btn_update.grid(row=9, column=1, padx=10, pady=5)

        self.btn_delete = tk.Button(frame, text="删除", command=self.delete_user)
        self.btn_delete.grid(row=9, column=2, padx=10, pady=5)

        # 人员信息列表
        columns = ["工号", "姓名", "性别", "出生日期", "入职时间", "就职部门", "职位级别", "权限设置", "状态"]
        self.tree_personnel = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree_personnel.heading(col, text=col)
        self.tree_personnel.grid(row=10, column=0, columnspan=3, padx=10, pady=10)

        self.load_users()

    def load_users(self):
        for user in self.users:
            self.tree_personnel.insert("", "end", values=tuple(user.values()))

    def add_user(self):
        new_user = {
            "工号": self.entry_id.get(),
            "密码": self.entry_password.get(),
            "姓名": self.entry_name.get(),
            "性别": self.combo_gender.get(),
            "出生日期": self.entry_birth_date.get(),
            "入职时间": self.entry_join_date.get(),
            "就职部门": self.entry_department.get(),
            "职位级别": self.entry_position_level.get(),
            "权限设置": self.entry_permission.get(),
            "状态": "空闲"
        }
        self.users.append(new_user)
        self.tree_personnel.insert("", "end", values=tuple(new_user.values()))
        messagebox.showinfo("提示", "新增用户成功！")

    def update_user(self):
        selected_item = self.tree_personnel.selection()[0]
        index = self.tree_personnel.index(selected_item)
        self.users[index] = {
            "工号": self.entry_id.get(),
            "密码": self.entry_password.get(),
            "姓名": self.entry_name.get(),
            "性别": self.combo_gender.get(),
            "出生日期": self.entry_birth_date.get(),
            "入职时间": self.entry_join_date.get(),
            "就职部门": self.entry_department.get(),
            "职位级别": self.entry_position_level.get(),
            "权限设置": self.entry_permission.get(),
            "状态": "空闲"
        }
        self.tree_personnel.item(selected_item, values=tuple(self.users[index].values()))
        messagebox.showinfo("提示", "用户信息更新成功！")

    def delete_user(self):
        selected_item = self.tree_personnel.selection()[0]
        index = self.tree_personnel.index(selected_item)
        self.users.pop(index)
        self.tree_personnel.delete(selected_item)
        messagebox.showinfo("提示", "用户删除成功！")

    def create_info(self):
        frame = self.frames['设备信息管理']
        # 设备编号
        tk.Label(frame, text="设备编号").grid(row=0, column=0, padx=10, pady=5)
        self.entry_number = tk.Entry(frame)
        self.entry_number.grid(row=0, column=1, padx=10, pady=5)

        # 设备类型
        tk.Label(frame, text="设备类型").grid(row=1, column=0, padx=10, pady=5)
        self.entry_type = tk.Entry(frame)
        self.entry_type.grid(row=1, column=1, padx=10, pady=5)

        # 生产厂家
        tk.Label(frame, text="生产厂家").grid(row=2, column=0, padx=10, pady=5)
        self.chang = tk.Entry(frame)
        self.chang.grid(row=2, column=1, padx=10, pady=5)

        # 额定功率
        tk.Label(frame, text="额定功率").grid(row=3, column=0, padx=10, pady=5)
        self.W = ttk.Combobox(frame, values=["100瓦以下", "100瓦-500瓦", "500-1000瓦", "1000瓦以上"])
        self.W.grid(row=3, column=1, padx=10, pady=5)

        # 安装时间
        tk.Label(frame, text="安装时间").grid(row=4, column=0, padx=10, pady=5)
        self.entry_install_date = tk.Entry(frame)
        self.entry_install_date.grid(row=4, column=1, padx=10, pady=5)

        # 安装位置
        tk.Label(frame, text="安装位置").grid(row=5, column=0, padx=10, pady=5)
        self.GPS = tk.Entry(frame)
        self.GPS.grid(row=5, column=1, padx=10, pady=5)

        # 按钮
        self.btn_add = tk.Button(frame, text="新增", command=self.add_user2)
        self.btn_add.grid(row=9, column=0, padx=10, pady=5)

        self.btn_update = tk.Button(frame, text="修改", command=self.update_user2)
        self.btn_update.grid(row=9, column=1, padx=10, pady=5)

        self.btn_delete = tk.Button(frame, text="删除", command=self.delete_user2)
        self.btn_delete.grid(row=9, column=2, padx=10, pady=5)

        # 设备信息列表
        columns2 = ["设备编号", "设备类型", "生产厂家", "额定功率", "安装时间", "安装位置"]
        self.tree_device = ttk.Treeview(frame, columns=columns2, show="headings")
        for col in columns2:
            self.tree_device.heading(col, text=col)
        self.tree_device.grid(row=10, column=0, columnspan=3, padx=10, pady=10)

        self.load_users2()

    def load_users2(self):
        for user2 in self.users2:
            self.tree_device.insert("", "end", values=tuple(user2.values()))

    def add_user2(self):
        new_user2 = {
            "设备编号": self.entry_number.get(),
            "设备类型": self.entry_type.get(),
            "生产厂家": self.chang.get(),
            "额定功率": self.W.get(),
            "安装时间": self.entry_install_date.get(),
            "安装位置": self.GPS.get()
        }
        self.users2.append(new_user2)
        self.tree_device.insert("", "end", values=tuple(new_user2.values()))
        messagebox.showinfo("提示", "新增设备成功！")

    def update_user2(self):
        selected_item = self.tree_device.selection()[0]
        index = self.tree_device.index(selected_item)
        self.users2[index] = {
            "设备编号": self.entry_number.get(),
            "设备类型": self.entry_type.get(),
            "生产厂家": self.chang.get(),
            "额定功率": self.W.get(),
            "安装时间": self.entry_install_date.get(),
            "安装位置": self.GPS.get()
        }
        self.tree_device.item(selected_item, values=tuple(self.users2[index].values()))
        messagebox.showinfo("提示", "设备信息更新成功！")

    def delete_user2(self):
        selected_item = self.tree_device.selection()[0]
        index = self.tree_device.index(selected_item)
        self.users2.pop(index)
        self.tree_device.delete(selected_item)
        messagebox.showinfo("提示", "删除成功！")

    def create_basic(self):
        frame = self.frames['基础资源管理']
        # 设备编号
        tk.Label(frame, text="设备编号").grid(row=0, column=0, padx=10, pady=5)
        self.entry_basic_number = tk.Entry(frame)
        self.entry_basic_number.grid(row=0, column=1, padx=10, pady=5)

        # 叶片参数
        tk.Label(frame, text="叶片参数").grid(row=1, column=0, padx=10, pady=5)
        self.entry_blade = tk.Entry(frame)
        self.entry_blade.grid(row=1, column=1, padx=10, pady=5)

        # 齿轮参数
        tk.Label(frame, text="齿轮参数").grid(row=2, column=0, padx=10, pady=5)
        self.entry_gear = tk.Entry(frame)
        self.entry_gear.grid(row=2, column=1, padx=10, pady=5)

        # 发电机参数
        tk.Label(frame, text="发电机参数").grid(row=3, column=0, padx=10, pady=5)
        self.entry_generator = tk.Entry(frame)
        self.entry_generator.grid(row=3, column=1, padx=10, pady=5)

        # 按钮
        self.btn_add_basic = tk.Button(frame, text="新增", command=self.add_user3)
        self.btn_add_basic.grid(row=9, column=0, padx=10, pady=5)

        self.btn_update_basic = tk.Button(frame, text="修改", command=self.update_user3)
        self.btn_update_basic.grid(row=9, column=1, padx=10, pady=5)

        self.btn_delete_basic = tk.Button(frame, text="删除", command=self.delete_user3)
        self.btn_delete_basic.grid(row=9, column=2, padx=10, pady=5)

        # 设备信息列表
        columns3 = ["设备编号", "叶片参数", "齿轮参数", "发电机参数"]
        self.tree_basic = ttk.Treeview(frame, columns=columns3, show="headings")
        for col in columns3:
            self.tree_basic.heading(col, text=col)
        self.tree_basic.grid(row=10, column=0, columnspan=3, padx=10, pady=10)

        self.load_users3()

    def load_users3(self):
        for user3 in self.users3:
            self.tree_basic.insert("", "end", values=tuple(user3.values()))

    def add_user3(self):
        new_user3 = {
            "设备编号": self.entry_basic_number.get(),
            "叶片参数": self.entry_blade.get(),
            "齿轮参数": self.entry_gear.get(),
            "发电机参数": self.entry_generator.get()
        }
        self.users3.append(new_user3)
        self.tree_basic.insert("", "end", values=tuple(new_user3.values()))
        messagebox.showinfo("提示", "新增设备成功！")

    def update_user3(self):
        selected_item = self.tree_basic.selection()[0]
        index = self.tree_basic.index(selected_item)
        self.users3[index] = {
            "设备编号": self.entry_basic_number.get(),
            "叶片参数": self.entry_blade.get(),
            "齿轮参数": self.entry_gear.get(),
            "发电机参数": self.entry_generator.get()
        }
        self.tree_basic.item(selected_item, values=tuple(self.users3[index].values()))
        messagebox.showinfo("提示", "设备信息更新成功！")

    def delete_user3(self):
        selected_item = self.tree_basic.selection()[0]
        index = self.tree_basic.index(selected_item)
        self.users3.pop(index)
        self.tree_basic.delete(selected_item)
        messagebox.showinfo("提示", "删除成功！")

    def create_weather_page(self):
        frame = self.frames['气象信息管理']

        # 实时时间显示
        self.time_label_weather = tk.Label(frame, text="", font=("Arial", 12))
        self.time_label_weather.grid(row=0, column=0, columnspan=6, padx=10, pady=5)

        # 输入区域
        tk.Label(frame, text="日期").grid(row=1, column=0, padx=10, pady=5)
        self.entry_date = tk.Entry(frame)
        self.entry_date.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(frame, text="温度").grid(row=2, column=0, padx=10, pady=5)
        self.entry_temperature = tk.Entry(frame)
        self.entry_temperature.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(frame, text="湿度").grid(row=3, column=0, padx=10, pady=5)
        self.entry_humidity = tk.Entry(frame)
        self.entry_humidity.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(frame, text="风速").grid(row=4, column=0, padx=10, pady=5)
        self.entry_wind_speed = tk.Entry(frame)
        self.entry_wind_speed.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(frame, text="天气状况").grid(row=5, column=0, padx=10, pady=5)
        self.entry_weather_condition = tk.Entry(frame)
        self.entry_weather_condition.grid(row=5, column=1, padx=10, pady=5)

        # 按钮区域
        self.btn_add_weather = tk.Button(frame, text="新增", command=self.add_weather)
        self.btn_add_weather.grid(row=6, column=0, padx=10, pady=5)

        self.btn_update_weather = tk.Button(frame, text="修改", command=self.update_weather)
        self.btn_update_weather.grid(row=6, column=1, padx=10, pady=5)

        self.btn_delete_weather = tk.Button(frame, text="删除", command=self.delete_weather)
        self.btn_delete_weather.grid(row=6, column=2, padx=10, pady=5)

        self.btn_search_weather = tk.Button(frame, text="搜索", command=self.search_weather)
        self.btn_search_weather.grid(row=6, column=3, padx=10, pady=5)

        self.btn_import_weather = tk.Button(frame, text="导入", command=self.import_weather)
        self.btn_import_weather.grid(row=6, column=4, padx=10, pady=5)

        self.btn_export_weather = tk.Button(frame, text="导出", command=self.export_weather)
        self.btn_export_weather.grid(row=6, column=5, padx=10, pady=5)

        # 显示区域
        columns = ["日期", "温度", "湿度", "风速", "天气状况"]
        self.tree_weather = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree_weather.heading(col, text=col)
        self.tree_weather.grid(row=7, column=0, columnspan=6, padx=10, pady=10)

        self.load_weather_data()

    def load_weather_data(self):
        for weather in self.weather_data:
            self.tree_weather.insert("", "end", values=tuple(weather.values()))

    def add_weather(self):
        new_weather = {
            "日期": self.entry_date.get(),
            "温度": self.entry_temperature.get(),
            "湿度": self.entry_humidity.get(),
            "风速": self.entry_wind_speed.get(),
            "天气状况": self.entry_weather_condition.get()
        }
        self.weather_data.append(new_weather)
        self.tree_weather.insert("", "end", values=tuple(new_weather.values()))
        messagebox.showinfo("提示", "新增气象信息成功！")

    def update_weather(self):
        selected_item = self.tree_weather.selection()[0]
        index = self.tree_weather.index(selected_item)
        self.weather_data[index] = {
            "日期": self.entry_date.get(),
            "温度": self.entry_temperature.get(),
            "湿度": self.entry_humidity.get(),
            "风速": self.entry_wind_speed.get(),
            "天气状况": self.entry_weather_condition.get()
        }
        self.tree_weather.item(selected_item, values=tuple(self.weather_data[index].values()))
        messagebox.showinfo("提示", "气象信息更新成功！")

    def delete_weather(self):
        selected_item = self.tree_weather.selection()[0]
        index = self.tree_weather.index(selected_item)
        self.weather_data.pop(index)
        self.tree_weather.delete(selected_item)
        messagebox.showinfo("提示", "删除成功！")

    def search_weather(self):
        search_date = self.entry_date.get()
        matching_data = [weather for weather in self.weather_data if weather["日期"] == search_date]
        self.tree_weather.delete(*self.tree_weather.get_children())
        for weather in matching_data:
            self.tree_weather.insert("", "end", values=tuple(weather.values()))
        if not matching_data:
            messagebox.showinfo("提示", "没有找到匹配的气象信息")

    def import_weather(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.weather_data = list(reader)
                self.tree_weather.delete(*self.tree_weather.get_children())
                self.load_weather_data()
                messagebox.showinfo("提示", "导入成功！")

    def export_weather(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["日期", "温度", "湿度", "风速", "天气状况"])
                writer.writeheader()
                writer.writerows(self.weather_data)
                messagebox.showinfo("提示", "导出成功！")

    def create_declaration_page(self):
        frame = self.frames['设备信息']

        # 实时时间显示
        self.time_label_declaration = tk.Label(frame, text="", font=("Arial", 12))
        self.time_label_declaration.grid(row=0, column=0, columnspan=6, padx=10, pady=5)

        # 输入区域
        tk.Label(frame, text="设备编号").grid(row=1, column=0, padx=10, pady=5)
        self.entry_device_id = tk.Entry(frame)
        self.entry_device_id.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(frame, text="设备名称").grid(row=2, column=0, padx=10, pady=5)
        self.entry_device_name = tk.Entry(frame)
        self.entry_device_name.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(frame, text="声明日期").grid(row=3, column=0, padx=10, pady=5)
        self.entry_declaration_date = tk.Entry(frame)
        self.entry_declaration_date.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(frame, text="状态").grid(row=4, column=0, padx=10, pady=5)
        self.entry_status = tk.Entry(frame)
        self.entry_status.grid(row=4, column=1, padx=10, pady=5)

        # 按钮区域
        self.btn_add_declaration = tk.Button(frame, text="新增", command=self.add_declaration)
        self.btn_add_declaration.grid(row=5, column=0, padx=10, pady=5)

        self.btn_update_declaration = tk.Button(frame, text="修改", command=self.update_declaration)
        self.btn_update_declaration.grid(row=5, column=1, padx=10, pady=5)

        self.btn_delete_declaration = tk.Button(frame, text="删除", command=self.delete_declaration)
        self.btn_delete_declaration.grid(row=5, column=2, padx=10, pady=5)

        self.btn_search_declaration = tk.Button(frame, text="搜索", command=self.search_declaration)
        self.btn_search_declaration.grid(row=5, column=3, padx=10, pady=5)

        self.btn_import_declaration = tk.Button(frame, text="导入", command=self.import_declaration)
        self.btn_import_declaration.grid(row=5, column=4, padx=10, pady=5)

        self.btn_export_declaration = tk.Button(frame, text="导出", command=self.export_declaration)
        self.btn_export_declaration.grid(row=5, column=5, padx=10, pady=5)

        # 显示区域
        columns = ["设备编号", "设备名称", "声明日期", "状态"]
        self.tree_declaration = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree_declaration.heading(col, text=col)
        self.tree_declaration.grid(row=6, column=0, columnspan=6, padx=10, pady=10)

        self.load_declaration_data()

    def load_declaration_data(self):
        for declaration in self.declaration_data:
            self.tree_declaration.insert("", "end", values=tuple(declaration.values()))

    def add_declaration(self):
        new_declaration = {
            "设备编号": self.entry_device_id.get(),
            "设备名称": self.entry_device_name.get(),
            "声明日期": self.entry_declaration_date.get(),
            "状态": self.entry_status.get()
        }
        self.declaration_data.append(new_declaration)
        self.tree_declaration.insert("", "end", values=tuple(new_declaration.values()))
        messagebox.showinfo("提示", "新增设备声明成功！")

    def update_declaration(self):
        selected_item = self.tree_declaration.selection()[0]
        index = self.tree_declaration.index(selected_item)
        self.declaration_data[index] = {
            "设备编号": self.entry_device_id.get(),
            "设备名称": self.entry_device_name.get(),
            "声明日期": self.entry_declaration_date.get(),
            "状态": self.entry_status.get()
        }
        self.tree_declaration.item(selected_item, values=tuple(self.declaration_data[index].values()))
        messagebox.showinfo("提示", "设备声明更新成功！")

    def delete_declaration(self):
        selected_item = self.tree_declaration.selection()[0]
        index = self.tree_declaration.index(selected_item)
        self.declaration_data.pop(index)
        self.tree_declaration.delete(selected_item)
        messagebox.showinfo("提示", "删除成功！")

    def search_declaration(self):
        search_device_id = self.entry_device_id.get()
        matching_data = [declaration for declaration in self.declaration_data if declaration["设备编号"] == search_device_id]
        self.tree_declaration.delete(*self.tree_declaration.get_children())
        for declaration in matching_data:
            self.tree_declaration.insert("", "end", values=tuple(declaration.values()))
        if not matching_data:
            messagebox.showinfo("提示", "没有找到匹配的设备声明信息")

    def import_declaration(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.declaration_data = list(reader)
                self.tree_declaration.delete(*self.tree_declaration.get_children())
                self.load_declaration_data()
                messagebox.showinfo("提示", "导入成功！")

    def export_declaration(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["设备编号", "设备名称", "声明日期", "状态"])
                writer.writeheader()
                writer.writerows(self.declaration_data)
                messagebox.showinfo("提示", "导出成功！")

    def create_log(self):
        frame = self.frames['维修活动管理']
        # 日志显示区域
        self.log_text = tk.Text(frame, wrap='word', height=15, width=50)
        self.log_text.grid(row=0, column=0, columnspan=3, padx=10, pady=5)

        # 滚动条
        scrollbar = ttk.Scrollbar(frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=3, sticky='ns')

        # 日志输入框
        tk.Label(frame, text="撰写日志").grid(row=1, column=0, padx=10, pady=5)
        self.entry_log = tk.Entry(frame, width=40)
        self.entry_log.grid(row=1, column=1, padx=10, pady=5)

        # 按钮
        self.btn_add_log = tk.Button(frame, text="新增日志", command=self.add_log)
        self.btn_add_log.grid(row=2, column=0, padx=10, pady=5)

        self.btn_read_log = tk.Button(frame, text="读取日志", command=self.read_log)
        self.btn_read_log.grid(row=2, column=1, padx=10, pady=5)

        self.btn_clear_log = tk.Button(frame, text="清空日志", command=self.clear_log)
        self.btn_clear_log.grid(row=2, column=2, padx=10, pady=5)

    def add_log(self):
        log_entry = self.entry_log.get()
        if log_entry:
            with open("logs.txt", "a") as log_file:
                log_file.write(log_entry + "\n")
            self.entry_log.delete(0, tk.END)
            self.log_text.insert(tk.END, log_entry + "\n")
            messagebox.showinfo("提示", "日志添加成功！")
        else:
            messagebox.showwarning("警告", "日志内容不能为空！")

    def read_log(self):
        if os.path.exists("logs.txt"):
            with open("logs.txt", "r") as log_file:
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, log_file.read())
        else:
            messagebox.showwarning("警告", "没有找到日志文件！")

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        if os.path.exists("logs.txt"):
            os.remove("logs.txt")
        messagebox.showinfo("提示", "日志已清空！")

    def create_operation_page(self):
        frame = self.frames['设备运行管理']

        # 实时时间显示
        self.time_label_operation = tk.Label(frame, text="", font=("Arial", 12))
        self.time_label_operation.grid(row=0, column=0, columnspan=6, padx=10, pady=5)

        # 输入区域
        tk.Label(frame, text="设备编号").grid(row=1, column=0, padx=10, pady=5)
        self.entry_device_id_operation = tk.Entry(frame)
        self.entry_device_id_operation.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(frame, text="运行状态").grid(row=2, column=0, padx=10, pady=5)
        self.entry_status_operation = tk.Entry(frame)
        self.entry_status_operation.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(frame, text="运行时间").grid(row=3, column=0, padx=10, pady=5)
        self.entry_runtime_operation = tk.Entry(frame)
        self.entry_runtime_operation.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(frame, text="操作人员").grid(row=4, column=0, padx=10, pady=5)
        self.entry_operator_operation = tk.Entry(frame)
        self.entry_operator_operation.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(frame, text="备注").grid(row=5, column=0, padx=10, pady=5)
        self.entry_remark_operation = tk.Entry(frame)
        self.entry_remark_operation.grid(row=5, column=1, padx=10, pady=5)

        # 按钮区域
        self.btn_add_operation = tk.Button(frame, text="新增", command=self.add_operation)
        self.btn_add_operation.grid(row=6, column=0, padx=10, pady=5)

        self.btn_update_operation = tk.Button(frame, text="修改", command=self.update_operation)
        self.btn_update_operation.grid(row=6, column=1, padx=10, pady=5)

        self.btn_delete_operation = tk.Button(frame, text="删除", command=self.delete_operation)
        self.btn_delete_operation.grid(row=6, column=2, padx=10, pady=5)

        self.btn_search_operation = tk.Button(frame, text="搜索", command=self.search_operation)
        self.btn_search_operation.grid(row=6, column=3, padx=10, pady=5)

        self.btn_import_operation = tk.Button(frame, text="导入", command=self.import_operation)
        self.btn_import_operation.grid(row=6, column=4, padx=10, pady=5)

        self.btn_export_operation = tk.Button(frame, text="导出", command=self.export_operation)
        self.btn_export_operation.grid(row=6, column=5, padx=10, pady=5)

        # 显示区域
        columns = ["设备编号", "运行状态", "运行时间", "操作人员", "备注"]
        self.tree_operation = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree_operation.heading(col, text=col)
        self.tree_operation.grid(row=7, column=0, columnspan=6, padx=10, pady=10)

        self.load_operation_data()

    def load_operation_data(self):
        for operation in self.operation_data:
            self.tree_operation.insert("", "end", values=tuple(operation.values()))

    def add_operation(self):
        new_operation = {
            "设备编号": self.entry_device_id_operation.get(),
            "运行状态": self.entry_status_operation.get(),
            "运行时间": self.entry_runtime_operation.get(),
            "操作人员": self.entry_operator_operation.get(),
            "备注": self.entry_remark_operation.get()
        }
        self.operation_data.append(new_operation)
        self.tree_operation.insert("", "end", values=tuple(new_operation.values()))
        messagebox.showinfo("提示", "新增设备运行信息成功！")

    def update_operation(self):
        selected_item = self.tree_operation.selection()[0]
        index = self.tree_operation.index(selected_item)
        self.operation_data[index] = {
            "设备编号": self.entry_device_id_operation.get(),
            "运行状态": self.entry_status_operation.get(),
            "运行时间": self.entry_runtime_operation.get(),
            "操作人员": self.entry_operator_operation.get(),
            "备注": self.entry_remark_operation.get()
        }
        self.tree_operation.item(selected_item, values=tuple(self.operation_data[index].values()))
        messagebox.showinfo("提示", "设备运行信息更新成功！")

    def delete_operation(self):
        selected_item = self.tree_operation.selection()[0]
        index = self.tree_operation.index(selected_item)
        self.operation_data.pop(index)
        self.tree_operation.delete(selected_item)
        messagebox.showinfo("提示", "删除成功！")

    def search_operation(self):
        search_device_id = self.entry_device_id_operation.get()
        matching_data = [operation for operation in self.operation_data if operation["设备编号"] == search_device_id]
        self.tree_operation.delete(*self.tree_operation.get_children())
        for operation in matching_data:
            self.tree_operation.insert("", "end", values=tuple(operation.values()))
        if not matching_data:
            messagebox.showinfo("提示", "没有找到匹配的设备运行信息")

    def import_operation(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.operation_data = list(reader)
                self.tree_operation.delete(*self.tree_operation.get_children())
                self.load_operation_data()
                messagebox.showinfo("提示", "导入成功！")

    def export_operation(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["设备编号", "运行状态", "运行时间", "操作人员", "备注"])
                writer.writeheader()
                writer.writerows(self.operation_data)
                messagebox.showinfo("提示", "导出成功！")

    def update_time(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.time_label_weather.config(text=f"当前时间: {current_time}")
        self.time_label_declaration.config(text=f"当前时间: {current_time}")
        self.time_label_operation.config(text=f"当前时间: {current_time}")
        self.root.after(1000, self.update_time)

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonnelManagementSystem(root)
    root.mainloop()