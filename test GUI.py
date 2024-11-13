import sys
import sqlite3
import win32print
import win32api
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QComboBox, QCheckBox, QDialog, QFormLayout, QDialogButtonBox, QDateEdit, QCompleter, QMessageBox
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIntValidator, QPainter, QFont
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog


def create_tables():
    conn = sqlite3.connect('management.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Customer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        address TEXT,
        debt INTEGER,
        notes TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        stock INTEGER
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Invoice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        total INTEGER,
        debt_pre INTEGER,
        date TEXT,
        status TEXT,
        received_amount INTEGER,
        payment_date TEXT,
        notes TEXT,
        FOREIGN KEY(customer_id) REFERENCES Customer(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS InvoiceProduct (
        invoice_id INTEGER,
        product_name TEXT,
        quantity INTEGER,
        price INTEGER,
        total INTEGER,
        FOREIGN KEY(invoice_id) REFERENCES Invoice(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Supplier (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        address TEXT,
        phone TEXT,
        bank_account TEXT,
        bank_name TEXT
    )''')

    conn.commit()
    conn.close()


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customer Management App")
        self.setGeometry(100, 100, 830, 800)

        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.create_supplier_tab()
        self.create_customer_tab()
        self.create_product_tab()
        self.create_invoice_tab()
        self.create_manage_invoice_tab()
        self.create_print_invoice_tab()

        self.setLayout(layout)

    def create_supplier_tab(self):
        self.supplier_tab = QWidget()
        self.tabs.addTab(self.supplier_tab, "Nhà cung cấp")

        layout = QVBoxLayout()

        self.supplier_company_name = QLineEdit()
        self.supplier_company_name.setPlaceholderText("Tên công ty (*)")
        layout.addWidget(QLabel("Tên công ty"))
        layout.addWidget(self.supplier_company_name)

        self.supplier_address = QLineEdit()
        self.supplier_address.setPlaceholderText("Địa chỉ (*)")
        layout.addWidget(QLabel("Địa chỉ"))
        layout.addWidget(self.supplier_address)

        self.supplier_phone = QLineEdit()
        self.supplier_phone.setPlaceholderText("Số điện thoại (*)")
        layout.addWidget(QLabel("Số điện thoại"))
        layout.addWidget(self.supplier_phone)

        self.supplier_bank_account = QLineEdit()
        self.supplier_bank_account.setPlaceholderText("Số tài khoản (*)")
        layout.addWidget(QLabel("Số tài khoản"))
        layout.addWidget(self.supplier_bank_account)

        self.supplier_bank_name = QLineEdit()
        self.supplier_bank_name.setPlaceholderText("Tên ngân hàng (*)")
        layout.addWidget(QLabel("Tên ngân hàng"))
        layout.addWidget(self.supplier_bank_name)

        save_supplier_btn = QPushButton("Lưu thông tin Nhà cung cấp")
        save_supplier_btn.clicked.connect(self.save_supplier_info)
        layout.addWidget(save_supplier_btn)

        self.supplier_message_label = QLabel("")
        layout.addWidget(self.supplier_message_label)

        self.supplier_tab.setLayout(layout)
        self.load_supplier_info() 
    
    def save_supplier_info(self):
        if self.supplier_company_name.text() == '' or self.supplier_address.text() == '' or self.supplier_phone.text() == '' or self.supplier_bank_account.text() == '' or self.supplier_bank_name.text() == '':
            self.supplier_message_label.setText("Nhập đầy đủ các thông tin có dấu (*)")
            return
        elif len(self.supplier_phone.text()) < 10:
            self.supplier_message_label.setText("Vui lòng kiểm tra lại số điện thoại")
            return
        """Lưu hoặc cập nhật thông tin nhà cung cấp."""
        company_name = self.supplier_company_name.text()
        address = self.supplier_address.text()
        phone = self.supplier_phone.text()
        bank_account = self.supplier_bank_account.text()
        bank_name = self.supplier_bank_name.text()

        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()

        # Kiểm tra xem đã có nhà cung cấp trong cơ sở dữ liệu hay chưa
        cursor.execute("SELECT id FROM Supplier ORDER BY id DESC LIMIT 1")
        supplier = cursor.fetchone()

        if supplier:
            # Cập nhật thông tin nhà cung cấp nếu đã tồn tại
            cursor.execute("""
                UPDATE Supplier
                SET company_name = ?, address = ?, phone = ?, bank_account = ?, bank_name = ?
                WHERE id = ?
            """, (company_name, address, phone, bank_account, bank_name, supplier[0]))
            self.supplier_message_label.setText("Cập nhật thông tin nhà cung cấp thành công!")
        else:
            # Nếu không có nhà cung cấp nào, thêm một nhà cung cấp mới
            cursor.execute("""
                INSERT INTO Supplier (company_name, address, phone, bank_account, bank_name)
                VALUES (?, ?, ?, ?, ?)
            """, (company_name, address, phone, bank_account, bank_name))
            self.supplier_message_label.setText("Thêm thông tin nhà cung cấp thành công!")

        conn.commit()
        conn.close()

        self.load_supplier_info()  # Tải lại thông tin sau khi lưu hoặc cập nhật

    
    def load_supplier_info(self):
        """Tải thông tin nhà cung cấp mới nhất từ cơ sở dữ liệu."""
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()

        # Lấy thông tin nhà cung cấp gần nhất (theo ID)
        cursor.execute("SELECT company_name, address, phone, bank_account, bank_name FROM Supplier ORDER BY id DESC LIMIT 1")
        supplier = cursor.fetchone()
        conn.close()

        # Kiểm tra và hiển thị thông tin nếu có nhà cung cấp
        if supplier:
            self.supplier_company_name.setText(supplier[0])
            self.supplier_address.setText(supplier[1])
            self.supplier_phone.setText(supplier[2])
            self.supplier_bank_account.setText(supplier[3])
            self.supplier_bank_name.setText(supplier[4])

        
    def create_print_invoice_tab(self):
        self.print_invoice_tab = QWidget()
        self.tabs.addTab(self.print_invoice_tab, "In Hóa đơn")

        layout = QVBoxLayout()

        # Thêm combobox để chọn máy in
        self.printer_combobox = QComboBox()
        printers = self.list_printers()  # Gọi hàm list_printers để lấy danh sách máy in
        self.printer_combobox.addItems(printers)  # Thêm các máy in vào combobox
        layout.addWidget(QLabel("Chọn máy in:"))
        layout.addWidget(self.printer_combobox)

        # Thêm phần nhập ID     hóa đơn để tìm
        self.invoice_id_input = QLineEdit()
        self.invoice_id_input.setPlaceholderText("Nhập ID hóa đơn để tìm kiếm")
        layout.addWidget(QLabel("Tìm hóa đơn theo ID:"))
        layout.addWidget(self.invoice_id_input)

        # Thêm phần chọn ngày để tìm hóa đơn
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())  # Mặc định là ngày hôm nay
        layout.addWidget(QLabel("Tìm hóa đơn theo ngày:"))
        layout.addWidget(self.date_edit)

        # Nút tìm hóa đơn
        self.search_button = QPushButton("Tìm hóa đơn")
        self.search_button.clicked.connect(self.search_invoices)  # Kết nối tới hàm tìm kiếm
        layout.addWidget(self.search_button)

        # Bảng hiển thị kết quả hóa đơn
        self.print_invoice_table = QTableWidget()  # Khai báo bảng dữ liệu
        self.print_invoice_table.setColumnCount(5)
        self.print_invoice_table.setHorizontalHeaderLabels(["Chọn", "ID Hóa đơn", "Tên Khách hàng", "Ngày", "Tổng tiền"])
        self.print_invoice_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Khóa bảng không cho chỉnh sửa
        layout.addWidget(self.print_invoice_table)

        # Nút in hóa đơn
        self.print_button = QPushButton("In hóa đơn")
        self.print_button.clicked.connect(self.on_print_button_clicked)
        layout.addWidget(self.print_button)

        # Nút preview hóa đơn
        self.preview_button = QPushButton("Xem trước hóa đơn")
        self.preview_button.clicked.connect(self.preview_invoice)
        layout.addWidget(self.preview_button)

        self.print_invoice_tab.setLayout(layout)
    
    def search_invoices(self):
        """Tìm kiếm hóa đơn theo ID hoặc ngày đã chọn."""
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()

        # Kiểm tra nếu nhập ID hóa đơn
        invoice_id = self.invoice_id_input.text()
        if invoice_id != '' and invoice_id.isdigit():
            cursor.execute("""
                SELECT id, customer_id, date, total FROM Invoice
                WHERE id = ?
            """, (invoice_id,))
        else:
            # Nếu không nhập ID thì tìm theo ngày
            selected_date = self.date_edit.date().toString("yyyy-MM-dd")
            cursor.execute("""
                SELECT id, customer_id, date, total FROM Invoice
                WHERE date = ?
            """, (selected_date,))

        invoices = cursor.fetchall()
        conn.close()

        # Hiển thị kết quả trong bảng
        self.print_invoice_table.setRowCount(0)
        for invoice in invoices:
            row_number = self.print_invoice_table.rowCount()
            self.print_invoice_table.insertRow(row_number)

            checkbox_item = QCheckBox()
            self.print_invoice_table.setCellWidget(row_number, 0, checkbox_item)

            invoice_id_item = QTableWidgetItem(str(invoice[0]))
            customer_name = self.get_customer_name(invoice[1])  # Hàm để lấy tên khách hàng theo ID
            customer_name_item = QTableWidgetItem(customer_name)
            date_item = QTableWidgetItem(invoice[2])
            total_item = QTableWidgetItem(f"{invoice[3]:,}")

            self.print_invoice_table.setItem(row_number, 1, invoice_id_item)
            self.print_invoice_table.setItem(row_number, 2, customer_name_item)
            self.print_invoice_table.setItem(row_number, 3, date_item)
            self.print_invoice_table.setItem(row_number, 4, total_item)
    
    def on_print_button_clicked(self):
        selected_invoices = self.get_selected_invoices_for_print()  # Lấy các hóa đơn được chọn để in
        for invoice_data in selected_invoices:
            self.print_invoice(invoice_data)

    def get_selected_invoices(self):
        """Lấy các hóa đơn được chọn từ bảng để in."""
        selected_invoices = []
        for row in range(self.invoice_table.rowCount()):
            checkbox_item = self.invoice_table.cellWidget(row, 0)
            if checkbox_item.isChecked():
                invoice_id = int(self.invoice_table.item(row, 1).text())
                selected_invoices.append(self.get_invoice_data(invoice_id))  # Lấy dữ liệu hóa đơn
        return selected_invoices  
    
    def get_selected_invoices_for_print(self):
        """Lấy danh sách các hóa đơn được chọn để in."""
        selected_invoices = []
        for row in range(self.print_invoice_table.rowCount()):
            checkbox_item = self.print_invoice_table.cellWidget(row, 0)
            if checkbox_item.isChecked():
                invoice_id = self.print_invoice_table.item(row, 1).text()
                selected_invoices.append(self.fetch_invoice_data(invoice_id))
        return selected_invoices
   
    def get_invoice_data(self, invoice_id):
        """Lấy dữ liệu hóa đơn từ cơ sở dữ liệu theo ID hóa đơn."""
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Invoice.id, Customer.name, Invoice.date, Invoice.total, Customer.address, Customer.debt, Invoice.notes, InvoiceProduct.
            FROM Invoice
            JOIN Customer ON Invoice.customer_id = Customer.id
            JOIN InvoiceProduct ON Invoice.id = InvoiceProduct.invoice_id
            WHERE Invoice.id = ?
        """, (invoice_id,))
        invoice_data = cursor.fetchone()
        print(invoice_data)
        conn.close()
        return invoice_data


    def get_customer_name(self, customer_id):
        """Hàm để lấy tên khách hàng từ ID."""
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Customer WHERE id = ?", (customer_id,))
        customer_name = cursor.fetchone()[0]
        conn.close()
        return customer_name
    
    def list_printers(self):
        """Liệt kê tất cả các máy in được kết nối với hệ thống."""
        printers = []
        try:
            # Sử dụng win32print để lấy danh sách các máy in
            for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL):
                printers.append(printer[2])  # Lấy tên máy in (phần tử thứ 3 trong tuple)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lấy danh sách máy in: {str(e)}")
        return printers

    def load_invoices_for_print(self):
        """Load danh sách hóa đơn để hiển thị trong bảng chọn in."""
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, customer_id, total, date, notes FROM Invoice")
        invoices = cursor.fetchall()
        conn.close()

        self.print_invoice_table.setRowCount(0)
        for invoice in invoices:
            row_number = self.print_invoice_table.rowCount()
            self.print_invoice_table.insertRow(row_number)

            # Checkbox chọn hóa đơn
            checkbox_item = QCheckBox()
            self.print_invoice_table.setCellWidget(row_number, 0, checkbox_item)

            for column_number, data in enumerate(invoice):
                if isinstance(data, int):
                    self.print_invoice_table.setItem(row_number, column_number + 1, QTableWidgetItem(f"{data:,}"))
                else:
                    self.print_invoice_table.setItem(row_number, column_number + 1, QTableWidgetItem(str(data)))

    def preview_invoice(self):
        """Hiển thị cửa sổ popup xem trước hóa đơn."""
        selected_invoices = self.get_selected_invoices_for_print()
        supplier = self.get_supplier_info()

        if not selected_invoices:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ít nhất một hóa đơn để xem trước.")
            return

        # Giả lập nội dung hóa đơn cho xem trước
        for invoice in selected_invoices:
            dialog = QDialog(self)
            dialog.setWindowTitle("Xem trước hóa đơn")
            dialog.setFixedSize(548, 800)

            layout = QVBoxLayout(dialog)

            # Thông tin nhà cung cấp (hiển thị góc trái trên cùng)
            supplier_info = QLabel(f"Công ty {supplier['company_name']}\nĐịa chỉ: {supplier['address']}\nSĐT: {supplier['phone']}\nSTK: {supplier['bank_account']}\nNgân hàng: {supplier['bank_name']}")
            layout.addWidget(supplier_info)

            # Thông tin hóa đơn căn giữa
            invoice_info = QLabel(f"Hóa đơn giao hàng\nSố hóa đơn: {invoice['id']}\nNgày: {invoice['date']}")
            invoice_info.setAlignment(Qt.AlignCenter)
            layout.addWidget(invoice_info)

            # Thông tin khách hàng căn trái
            customer_info = QLabel(f"Khách hàng: {invoice['customer_name']}\nĐịa chỉ: {invoice['customer_address']}")
            layout.addWidget(customer_info)

            # Bảng hiển thị các sản phẩm trong hóa đơn
            product_table = QTableWidget()
            product_table.setColumnCount(4)
            product_table.setHorizontalHeaderLabels(["Tên sản phẩm", "Số lượng", "Đơn giá", "Thành tiền"])
            product_table.setRowCount(len(invoice['products']))
            for row, product in enumerate(invoice['products']):
                product_table.setItem(row, 0, QTableWidgetItem(product['name']))
                product_table.setItem(row, 1, QTableWidgetItem(f"{product['quantity']:,}"))
                product_table.setItem(row, 2, QTableWidgetItem(f"{product['price']:,}"))  # Sửa lỗi ở đây
                product_table.setItem(row, 3, QTableWidgetItem(f"{product['total']:,}"))
            layout.addWidget(product_table)

            # Tổng tiền, nợ cũ và tổng cộng
            summary_info = QLabel(f"Tổng tiền hàng: {invoice['total_price']:,}\nNợ cũ: {invoice['old_debt']:,}\nTổng cộng: {invoice['total_due']:,}")
            layout.addWidget(summary_info)

            # Phần ghi chú và chỗ ký tên
            notes_and_signature = QLabel(f"Ghi chú: {invoice['notes']}\n\n\nNgười giao hàng: __________________\t\tNgười nhận hàng: __________________")
            layout.addWidget(notes_and_signature)

            dialog.exec_()
    
    def fetch_invoice_data(self, invoice_id):
        """Lấy dữ liệu hóa đơn từ cơ sở dữ liệu."""
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()

        # Lấy thông tin hóa đơn
        cursor.execute("""
            SELECT Invoice.id, Customer.name, Invoice.date, Invoice.total, Customer.address, Invoice.debt_pre, Invoice.notes
            FROM Invoice
            JOIN Customer ON Invoice.customer_id = Customer.id
            WHERE Invoice.id = ?
        """, (invoice_id,))
        invoice = cursor.fetchone()

        # Lấy thông tin các sản phẩm trong hóa đơn
        cursor.execute("""
            SELECT product_name, quantity, price, total 
            FROM InvoiceProduct 
            WHERE invoice_id = ?
        """, (invoice_id,))
        products = cursor.fetchall()

        # Lấy thông tin nhà cung cấp
        cursor.execute("SELECT company_name, address, phone, bank_account, bank_name FROM Supplier ORDER BY id DESC LIMIT 1")
        supplier = cursor.fetchone()

        conn.close()

        
        return {
            "id": invoice[0],
            "customer_name": invoice[1],
            "date": invoice[2],
            "total_price": invoice[3],
            "customer_address": invoice[4],
            "old_debt": invoice[5],
            "notes": invoice[6],
            "products": [{"name": p[0], "quantity": p[1], "price": p[2], "total": p[3]} for p in products],
            "supplier_name": supplier[0],
            "supplier_address": supplier[1],
            "supplier_phone": supplier[2],
            "supplier_bank_account": supplier[3],
            "supplier_bank_name": supplier[4],
            "total_due": int(invoice[3]) + int(invoice[5]),
        }
        # return {
        #     "id": invoice[0],
        #     "customer_name": invoice[1],
        #     "customer_address": invoice[4],
        #     "products": [{"name": p[0], "quantity": p[1], "price": p[3], "total": p[2]} for p in products],
        #     "total_price": total_price,  # Tổng tiền của hóa đơn
        #     "old_debt": old_debt,  # Số nợ cũ của khách hàng
        #     "total_due": total_due,  # Tổng cộng
        #     "notes": invoice[6],
        #     "date": invoice[2],  # Ngày hóa đơn
        # }


    def check_printer_status(printer_name):
        """Kiểm tra trạng thái máy in."""
        printers = win32print.EnumPrinters(2)
        for printer in printers:
            if printer[2] == printer_name:
                status = win32print.GetPrinter(printer[0], 2)['Status']
                if status == 0:  # Trạng thái 0 là "Ready"
                    return True
                else:
                    return False
        return False

    def get_supplier_info(self):
        """Lấy thông tin nhà cung cấp từ bảng Supplier."""
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT company_name, address, phone, bank_account, bank_name FROM Supplier ORDER BY id DESC LIMIT 1")
        supplier = cursor.fetchone()
        conn.close()

        if supplier:
            return {
                "company_name": supplier[0],
                "address": supplier[1],
                "phone": supplier[2],
                "bank_account": supplier[3],
                "bank_name": supplier[4]
            }
        else:
            return {
                "company_name": "Chưa có thông tin",
                "address": "Chưa có địa chỉ",
                "phone": "Chưa có số điện thoại",
                "bank_account": "Chưa có số tài khoản",
                "bank_name": "Chưa có tên ngân hàng"
            }

    def print_invoice(self, invoice_data):
        """Thực hiện in hóa đơn với thông tin nhà cung cấp."""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPaperSize(QPrinter.A6)  # Đặt kích thước giấy A5
        printer.setOrientation(QPrinter.Portrait)  # Đặt hướng giấy

        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)

            try:

                # Font cho tiêu đề
                title_font = QFont("Arial", 15, QFont.Bold)
                text_font = QFont("Arial", 10)

                painter.setFont(text_font)
                x = 100
                y = 300
                line_height = 200

                # Thông tin nhà cung cấp
                painter.drawText(x, y, f"Nhà cung cấp: {invoice_data['supplier_name']}")
                y += 100
                painter.drawText(x, y, f"Địa chỉ: {invoice_data['supplier_address']}")
                y += 100
                painter.drawText(x, y, f"Số điện thoại: {invoice_data['supplier_phone']}")
                y += 100
                painter.drawText(x, y, f"Số tài khoản: {invoice_data['supplier_bank_account']} tại {invoice_data['supplier_bank_name']}")
                y += line_height
                painter.drawText(x, y, f"-" * 110)
                y += line_height


                # Thông tin hóa đơn
                painter.setFont(title_font)
                painter.drawText(x + 900, y, "HÓA ĐƠN GIAO HÀNG")
                y += 100
                painter.setFont(text_font)
                painter.drawText(x + 1250, y, f"Ngày: {invoice_data['date']}")
                y += 150
                painter.drawText(x, y, f"Khách hàng: {invoice_data['customer_name']}")
                y += 100
                painter.drawText(x, y, f"Địa chỉ: {invoice_data['customer_address']}")
                y += line_height

                # Thông tin các sản phẩm
                painter.drawText(x, y, f"-" * 110)
                y += 100
                painter.drawText(x, y, "Đơn Hàng:")
                y += line_height

                for product in invoice_data['products']:
                    painter.drawText(x, y, f"{product['name']} - SL: {product['quantity']} - Đơn giá: {product['price']:,} - Thành tiền: {product['total']:,}")
                    y += line_height
                
                painter.drawText(x, y, f"-" * 110)
                y += line_height

                # Tổng tiền và các thông tin khác
                painter.drawText(x, y, f"Tổng tiền hàng: {invoice_data['total_price']:,}")
                y += line_height
                painter.drawText(x, y, f"Nợ cũ: {invoice_data['old_debt']:,}")
                y += line_height
                painter.drawText(x, y, f"Tổng cộng: {invoice_data['total_price'] + invoice_data['old_debt']:,}")
                y += line_height

                # Ghi chú
                painter.drawText(x, y, f"Ghi chú: {invoice_data['notes']}")
                y += line_height * 3

                # Chỗ ký tên
                painter.drawText(x, y, "Người giao hàng: ________________\tNgười nhận hàng: ________________")
                # if not painter.begin(printer):
                #     QMessageBox.warning(self, "Lỗi", "Kiểm tra lại máy in.")
                #     return  # Không thể bắt đầu in

            finally:
                print('END')
                painter.end()  # Kết thúc in
   
    def refresh_all_data(self):
        """Làm mới tất cả các bảng dữ liệu sau khi có thay đổi."""
        self.load_customers()
        self.load_products()
        self.load_invoices()
        self.load_products_combobox()  # Làm mới danh sách sản phẩm trong combobox khi có thay đổi

    def create_customer_tab(self):
        self.customer_tab = QWidget()
        self.tabs.addTab(self.customer_tab, "Quản lý Khách hàng")

        layout = QVBoxLayout()

        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Tên khách hàng (*)")
        self.customer_name.textChanged.connect(self.search_customers)
        layout.addWidget(self.customer_name)

        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Số điện thoại (*)")
        layout.addWidget(self.customer_phone)

        self.customer_address = QLineEdit()
        self.customer_address.setPlaceholderText("Địa chỉ (*)")
        layout.addWidget(self.customer_address)

        self.customer_debt = QLineEdit()
        self.customer_debt.setPlaceholderText("Tiền nợ (*)")
        self.customer_debt.setValidator(QIntValidator())
        layout.addWidget(self.customer_debt)

        self.customer_notes = QLineEdit()
        self.customer_notes.setPlaceholderText("Ghi chú")
        layout.addWidget(self.customer_notes)

        add_customer_btn = QPushButton("Thêm Khách hàng")
        layout.addWidget(add_customer_btn)
        self.customer_message_label = QLabel("")
        layout.addWidget(self.customer_message_label)

        add_customer_btn.clicked.connect(self.add_customer)

        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(6)
        self.customer_table.setHorizontalHeaderLabels(["Chọn", "Tên", "SĐT", "Địa chỉ", "Tiền nợ", "Ghi chú"])
        self.customer_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Khóa bảng không cho chỉnh sửa
        layout.addWidget(self.customer_table)

        delete_selected_btn = QPushButton("Xóa khách hàng được chọn")
        delete_selected_btn.clicked.connect(self.delete_selected_customers)
        layout.addWidget(delete_selected_btn)

        self.customer_tab.setLayout(layout)
        self.load_customers()

    def search_customers(self):
        search_text = self.customer_name.text().lower()
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, address, debt, notes FROM Customer WHERE name LIKE ?", ('%' + search_text + '%',))
        customers = cursor.fetchall()
        conn.close()

        self.customer_table.setRowCount(0)
        for row_data in customers:
            row_number = self.customer_table.rowCount()
            self.customer_table.insertRow(row_number)

            checkbox_item = QCheckBox()
            self.customer_table.setCellWidget(row_number, 0, checkbox_item)

            for column_number, data in enumerate(row_data[1:], start=1):  # Bỏ qua ID (column 0)
                if isinstance(data, int):
                    self.customer_table.setItem(row_number, column_number, QTableWidgetItem(f"{data:,}"))
                else:
                    self.customer_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def load_customers(self):
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, address, debt, notes FROM Customer")
        customers = cursor.fetchall()
        conn.close()

        self.customer_table.setRowCount(0)
        for row_data in customers:
            row_number = self.customer_table.rowCount()
            self.customer_table.insertRow(row_number)

            checkbox_item = QCheckBox()
            self.customer_table.setCellWidget(row_number, 0, checkbox_item)

            for column_number, data in enumerate(row_data[1:], start=1):  # Bỏ qua ID (column 0)
                if isinstance(data, int):
                    self.customer_table.setItem(row_number, column_number, QTableWidgetItem(f"{data:,}"))
                else:
                    self.customer_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def add_customer(self):
        if self.customer_name.text() == '' or self.customer_phone.text() == '' or self.customer_address.text() == '' or self.customer_debt.text() == '':
            self.customer_message_label.setText("Hãy nhập đầy đủ các thông tin có dấu (*)")
            return
        name = self.customer_name.text()
        phone = self.customer_phone.text()
        address = self.customer_address.text()
        debt = int(self.customer_debt.text().replace(",", ""))  # Xóa dấu phẩy khi lưu vào cơ sở dữ liệu
        notes = self.customer_notes.text()

        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Customer (name, phone, address, debt, notes) VALUES (?, ?, ?, ?, ?)",
                       (name, phone, address, debt, notes))
        conn.commit()
        conn.close()

        self.customer_message_label.setText("Thêm khách hàng thành công")
        self.refresh_all_data()
        self.clear_customer_inputs()

    def delete_selected_customers(self):
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()

        for i in range(self.customer_table.rowCount()):
            checkbox_item = self.customer_table.cellWidget(i, 0)
            if checkbox_item.isChecked():
                customer_name = self.customer_table.item(i, 1).text()
                cursor.execute("DELETE FROM Customer WHERE name = ?", (customer_name,))

        conn.commit()
        conn.close()
        self.refresh_all_data()

    def clear_customer_inputs(self):
        self.customer_name.clear()
        self.customer_phone.clear()
        self.customer_address.clear()
        self.customer_debt.clear()
        self.customer_notes.clear()

    def create_product_tab(self):
        self.product_tab = QWidget()
        self.tabs.addTab(self.product_tab, "Quản lý Sản phẩm")

        layout = QVBoxLayout()

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Tên sản phẩm")
        layout.addWidget(self.product_name)

        self.product_price = QLineEdit()
        self.product_price.setPlaceholderText("Giá sản phẩm")
        self.product_price.setValidator(QIntValidator())
        layout.addWidget(self.product_price)

        self.product_stock = QLineEdit()
        self.product_stock.setPlaceholderText("Số lượng tồn kho")
        self.product_stock.setValidator(QIntValidator())
        layout.addWidget(self.product_stock)

        add_product_btn = QPushButton("Thêm Sản phẩm")
        layout.addWidget(add_product_btn)
        self.product_message_label = QLabel("")
        layout.addWidget(self.product_message_label)

        add_product_btn.clicked.connect(self.add_or_update_product)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)
        self.product_table.setHorizontalHeaderLabels(["Chọn", "Tên", "Giá", "Số lượng tồn"])
        self.product_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Khóa bảng không cho chỉnh sửa
        self.product_table.cellDoubleClicked.connect(self.show_edit_product_dialog)  # Thêm chức năng click đôi
        layout.addWidget(self.product_table)

        delete_selected_btn = QPushButton("Xóa sản phẩm được chọn")
        delete_selected_btn.clicked.connect(self.delete_selected_products)
        layout.addWidget(delete_selected_btn)

        self.product_tab.setLayout(layout)
        self.load_products()

    def load_products(self):
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM Product")
        products = cursor.fetchall()
        conn.close()

        self.product_table.setRowCount(0)
        for row_data in products:
            row_number = self.product_table.rowCount()
            self.product_table.insertRow(row_number)

            checkbox_item = QCheckBox()
            self.product_table.setCellWidget(row_number, 0, checkbox_item)

            for column_number, data in enumerate(row_data[1:], start=1):  # Bỏ qua ID (column 0)
                if isinstance(data, int):
                    self.product_table.setItem(row_number, column_number, QTableWidgetItem(f"{data:,}"))
                else:
                    self.product_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

# Trong hàm add_or_update_product (Thêm hoặc cập nhật sản phẩm)
    def add_or_update_product(self):
        if self.product_name.text() == '' or self.product_price.text() == '' or self.product_stock.text() == '':
            # thêm
            self.product_message_label.setText("Hãy nhập đầy đủ thông tin")
            return
        name = self.product_name.text()
        price = int(self.product_price.text().replace(",", ""))  # Xóa dấu phẩy khi lưu vào cơ sở dữ liệu
        stock = int(self.product_stock.text().replace(",", ""))  # Xóa dấu phẩy khi lưu vào cơ sở dữ liệu

        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Product WHERE name = ?", (name,))
        existing_product = cursor.fetchone()

        if existing_product:
            cursor.execute("UPDATE Product SET price = ?, stock = ? WHERE name = ?", (price, stock, name))
            self.product_message_label.setText("Cập nhật sản phẩm thành công")
        else:
            cursor.execute("INSERT INTO Product (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
            self.product_message_label.setText("Thêm sản phẩm thành công")

        conn.commit()
        conn.close()

        self.refresh_all_data()  # Làm mới dữ liệu sau khi thêm hoặc cập nhật sản phẩm
        self.clear_product_inputs()

    # Trong hàm delete_selected_products (Xóa sản phẩm)
    def delete_selected_products(self):
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
    
        for i in range(self.product_table.rowCount()):
            checkbox_item = self.product_table.cellWidget(i, 0)
            if checkbox_item.isChecked():
                product_name = self.product_table.item(i, 1).text()
                cursor.execute("DELETE FROM Product WHERE name = ?", (product_name,))
    
        conn.commit()
        conn.close()
        self.refresh_all_data()  # Làm mới dữ liệu sau khi xóa sản phẩm

    def show_edit_product_dialog(self, row, column):
        product_name = self.product_table.item(row, 1).text()

        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT price, stock FROM Product WHERE name = ?", (product_name,))
        product_data = cursor.fetchone()
        conn.close()

        if product_data:
            price, stock = product_data

            dialog = QDialog(self)
            dialog.setWindowTitle("Chỉnh sửa sản phẩm")

            form_layout = QFormLayout(dialog)

            form_layout.addRow("Tên sản phẩm:", QLabel(product_name))

            self.edit_price_input = QLineEdit()
            self.edit_price_input.setValidator(QIntValidator())
            self.edit_price_input.setText(f"{price:,}")
            form_layout.addRow("Giá sản phẩm:", self.edit_price_input)

            self.edit_stock_input = QLineEdit()
            self.edit_stock_input.setValidator(QIntValidator())
            self.edit_stock_input.setText(f"{stock:,}")
            form_layout.addRow("Số lượng tồn kho:", self.edit_stock_input)

            update_button = QPushButton("Cập nhật")
            update_button.clicked.connect(lambda: self.update_product(product_name, dialog))
            form_layout.addWidget(update_button)

            delete_button = QPushButton("Xóa sản phẩm")
            delete_button.clicked.connect(lambda: self.delete_product(product_name, dialog))
            form_layout.addWidget(delete_button)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)
            form_layout.addWidget(button_box)

            dialog.exec_()

    def update_product(self, product_name, dialog):
        price = int(self.edit_price_input.text().replace(",", ""))
        stock = int(self.edit_stock_input.text().replace(",", ""))

        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE Product SET price = ?, stock = ? WHERE name = ?", (price, stock, product_name))
        conn.commit()
        conn.close()

        dialog.accept()
        self.refresh_all_data()

    def delete_product(self, product_name, dialog):
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Product WHERE name = ?", (product_name,))
        conn.commit()
        conn.close()

        dialog.accept()
        self.refresh_all_data()

    def clear_product_inputs(self):
        self.product_name.clear()
        self.product_price.clear()
        self.product_stock.clear()

    def create_invoice_tab(self):
        self.invoice_tab = QWidget()
        self.tabs.addTab(self.invoice_tab, "Tạo Hóa đơn")

        layout = QVBoxLayout()

        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Nhập tên khách hàng")
        self.customer_search.textChanged.connect(self.search_customers_for_invoice)
        layout.addWidget(self.customer_search)

        self.customer_info_label = QLabel("Thông tin khách hàng:")
        layout.addWidget(self.customer_info_label)

        self.product_combobox = QComboBox()  # Khởi tạo ở đây cho tab hóa đơn
        self.load_products_combobox()
        self.product_combobox.currentIndexChanged.connect(self.update_product_info)
        layout.addWidget(self.product_combobox)

        refresh_data_btn = QPushButton("Làm mới")
        layout.addWidget(refresh_data_btn)
        refresh_data_btn.clicked.connect(self.update_product_info)

        self.product_price_label = QLabel("Giá: ")
        layout.addWidget(self.product_price_label)

        self.product_stock_label = QLabel("Tồn kho: ")
        layout.addWidget(self.product_stock_label)

        self.invoice_quantity = QLineEdit()
        self.invoice_quantity.setPlaceholderText("Số lượng")
        self.invoice_quantity.setValidator(QIntValidator())
        layout.addWidget(self.invoice_quantity)

        add_product_to_invoice_btn = QPushButton("Thêm Sản phẩm vào Hóa đơn")
        layout.addWidget(add_product_to_invoice_btn)
        self.invoice_message_label = QLabel("")
        layout.addWidget(self.invoice_message_label)

        add_product_to_invoice_btn.clicked.connect(self.add_product_to_invoice)

        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(5)
        self.invoice_table.setHorizontalHeaderLabels(["Chọn", "Tên Sản phẩm", "Số lượng", "Giá", "Tổng tiền"])
        self.invoice_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Khóa bảng không cho chỉnh sửa
        layout.addWidget(self.invoice_table)

        delete_product_btn = QPushButton("Xóa sản phẩm đã thêm")
        layout.addWidget(delete_product_btn)
        delete_product_btn.clicked.connect(self.delete_selected_invoice_products)

        complete_invoice_btn = QPushButton("Hoàn tất Hóa đơn")
        layout.addWidget(complete_invoice_btn)
        self.invoice_message_label_complete = QLabel("")
        layout.addWidget(self.invoice_message_label_complete)

        complete_invoice_btn.clicked.connect(self.complete_invoice)

        self.total_price_label = QLabel("Tổng tiền: 0")
        layout.addWidget(self.total_price_label)

        self.total_debt_label = QLabel("Tiền nợ mới của khách hàng: 0")
        layout.addWidget(self.total_debt_label)

        self.invoice_tab.setLayout(layout)
        self.invoice_products = []

    def search_customers_for_invoice(self):
        """Cập nhật gợi ý tên khách hàng và tự động điền thông tin khi chọn."""
        search_text = self.customer_search.text().lower()
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()

        # Tìm kiếm tất cả các khách hàng theo tên
        cursor.execute("SELECT * FROM Customer WHERE name LIKE ?", ('%' + search_text + '%',))
        customers = cursor.fetchall()  # Lấy tất cả các tên khách hàng khớp
        self.customers_for_invoice = customers
        conn.close()

        # Lấy danh sách tên khách hàng để hiển thị trong QCompleter
        customer_names = [customer[1] for customer in customers]

        completer = QCompleter(customer_names, self)  # Tạo completer với danh sách tên khách hàng
        completer.setCaseSensitivity(Qt.CaseInsensitive)  # Không phân biệt hoa thường
        completer.setCompletionMode(QCompleter.PopupCompletion)  # Hiển thị danh sách dạng popup
        self.customer_search.setCompleter(completer)

        # Kết nối sự kiện khi giá trị trong ô nhập thay đổi
        self.customer_search.textChanged.connect(lambda: self.check_and_fill_customer_info(customer_names))

    def check_and_fill_customer_info(self, customer_names):
        """Kiểm tra nếu tên trong ô nhập trùng với danh sách gợi ý, thì tự động điền thông tin khách hàng."""
        current_text = self.customer_search.text()
        if current_text == '':
            self.customer_info_label.setText(f"Thông tin khách hàng: ")
            return

        if current_text in customer_names:
            self.fill_customer_info_from_text(current_text)

    def fill_customer_info_from_text(self, selected_name):
        """Tìm và điền thông tin chi tiết của khách hàng khi giá trị ô nhập khớp với tên gợi ý."""
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
    
        # Tìm kiếm thông tin chi tiết khách hàng theo tên đã chọn
        cursor.execute("SELECT name, phone, address, debt, notes FROM Customer WHERE name = ?", (selected_name,))
        customer = cursor.fetchone()  # Lấy thông tin khách hàng duy nhất
        conn.close()
    
        if customer:
            self.customer_info_label.setText(f"Thông tin khách hàng: {customer[0]}, SĐT: {customer[1]}, Địa chỉ: {customer[2]}, Nợ: {customer[3]:,}, Ghi chú: {customer[4]}")
        else:
            self.customer_info_label.setText("Không tìm thấy thông tin khách hàng.")    
    
    def load_products_combobox(self):
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, stock FROM Product")
        self.products = cursor.fetchall()
        conn.close()

        self.product_combobox.clear()  # Sử dụng self.product_combobox đã được khởi tạo
        for product in self.products:
            self.product_combobox.addItem(product[0], product)

    def update_product_info(self):
        product = self.product_combobox.currentData()
        if product:
            self.product_price_label.setText(f"Giá: {product[1]:,}")
            self.product_stock_label.setText(f"Tồn kho: {product[2]:,}")

    def add_product_to_invoice(self):
        product = self.product_combobox.currentData()
        quantity = int(self.invoice_quantity.text())

        total_quantity_in_invoice = sum(item[1] for item in self.invoice_products if item[0] == product[0])

        if total_quantity_in_invoice + quantity > product[2]:
            self.invoice_message_label.setText(f"Số lượng tồn kho không đủ. Tồn kho hiện tại: {product[2]:,}")
            return

        for item in self.invoice_products:
            if item[0] == product[0]:
                item[1] += quantity
                item[3] = item[1] * product[1]
                self.load_invoice_products()
                self.update_total_price()
                self.update_stock_after_add(product[0], quantity)
                return

        total_price = quantity * product[1]
        self.invoice_products.append([product[0], quantity, product[1], total_price])
        self.load_invoice_products()
        self.update_total_price()
        self.update_stock_after_add(product[0], quantity)

        # Làm mới dữ liệu trong tab hóa đơn sau khi thêm sản phẩm
        self.load_invoices()

    def load_invoice_products(self):
        self.invoice_table.setRowCount(0)
        for product in self.invoice_products:
            row_number = self.invoice_table.rowCount()
            self.invoice_table.insertRow(row_number)

            checkbox_item = QCheckBox()
            self.invoice_table.setCellWidget(row_number, 0, checkbox_item)

            for column_number, data in enumerate(product):
                if isinstance(data, int):
                    self.invoice_table.setItem(row_number, column_number + 1, QTableWidgetItem(f"{data:,}"))
                else:
                    self.invoice_table.setItem(row_number, column_number + 1, QTableWidgetItem(str(data)))

    def delete_selected_invoice_products(self):
        selected_products = []
        for i in range(self.invoice_table.rowCount()):
            checkbox_item = self.invoice_table.cellWidget(i, 0)
            if checkbox_item.isChecked():
                selected_products.append(i)

        for row in reversed(selected_products):
            product_name = self.invoice_table.item(row, 1).text()
            quantity = int(self.invoice_table.item(row, 2).text().replace(",", ""))
            self.update_stock_after_delete(product_name, quantity)
            self.invoice_products.pop(row)

        self.load_invoice_products()
        self.update_total_price()

    def update_total_price(self):
        total_price = sum([product[3] for product in self.invoice_products])
        self.total_price_label.setText(f"Tổng tiền: {total_price:,}")
        if self.customers_for_invoice:
            current_debt = self.customers_for_invoice[0][4]
            new_debt = current_debt + total_price
            self.total_debt_label.setText(f"Tiền nợ mới của khách hàng: {new_debt:,}")

    def update_stock_after_add(self, product_name, quantity):
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE Product SET stock = stock - ? WHERE name = ?", (quantity, product_name))
        conn.commit()
        conn.close()
        self.load_products_combobox()  # Cập nhật lại tồn kho trong combobox
        self.load_products()  # Làm mới sản phẩm trong tab sản phẩm và hóa đơn

    def update_stock_after_delete(self, product_name, quantity):
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE Product SET stock = stock + ? WHERE name = ?", (quantity, product_name))
        conn.commit()
        conn.close()
        self.load_products_combobox()  # Cập nhật lại tồn kho trong combobox
        self.load_products()

    def complete_invoice(self):
        """Hoàn tất hóa đơn và làm sạch dữ liệu trong tab sau khi thêm hóa đơn thành công"""

        if not self.customers_for_invoice:
            self.invoice_message_label_complete.setText("Vui lòng chọn khách hàng trước khi hoàn tất hóa đơn.")
            return

        customer = self.customers_for_invoice[0]
        total = sum([product[3] for product in self.invoice_products])

        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()

        # Thêm hóa đơn vào cơ sở dữ liệu
        cursor.execute("INSERT INTO Invoice (customer_id, total, debt_pre, date, status, received_amount, payment_date, notes) VALUES (?, ?, ?, date('now'), ?, ?, ?, ?)", 
                       (customer[0], total, customer[4], "đang được giao", 0, "", customer[5]))
        invoice_id = cursor.lastrowid

        # Thêm từng sản phẩm vào cơ sở dữ liệu liên kết với hóa đơn
        for product in self.invoice_products:
            cursor.execute("SELECT id FROM Product WHERE name = ?", (product[0],))
            product_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO InvoiceProduct (invoice_id, product_name, quantity, price, total) VALUES (?, ?, ?, ?, ?)", 
                           (invoice_id, product[0], product[1], product[2], product[3]),)

        # Cập nhật nợ cho khách hàng
        new_debt = customer[4] + total
        cursor.execute("UPDATE Customer SET debt = ? WHERE id = ?", (new_debt, customer[0]))

        conn.commit()
        conn.close()

        # Hiển thị thông báo thành công
        self.invoice_message_label_complete.setText("Hóa đơn hoàn tất thành công!")

        # Làm sạch dữ liệu sau khi hoàn tất hóa đơn
        self.clear_invoice_data()

        # Làm mới bảng hóa đơn và sản phẩm sau khi thêm hóa đơn
        self.load_invoices()
        self.refresh_all_data()

    def clear_invoice_data(self):
        """Xóa tất cả dữ liệu trong tab thêm hóa đơn sau khi hóa đơn được hoàn tất"""
        self.customer_search.clear()  # Xóa tên khách hàng
        self.customer_info_label.setText("Thông tin khách hàng:")  # Đặt lại thông tin khách hàng
        self.invoice_products = []  # Xóa danh sách sản phẩm trong hóa đơn
        self.load_invoice_products()  # Làm mới bảng sản phẩm đã thêm
        self.invoice_quantity.clear()  # Xóa số lượng sản phẩm nhập vào
        self.product_combobox.setCurrentIndex(0)  # Đặt lại combobox sản phẩm về lựa chọn đầu tiên
        self.total_price_label.setText("Tổng tiền: 0")  # Đặt lại tổng tiền về 0
        self.total_debt_label.setText("Tiền nợ mới của khách hàng: 0")  # Đặt lại tổng nợ về 0
        self.invoice_message_label_complete.setText("")  # Xóa thông báo cũ

    def create_manage_invoice_tab(self):
        self.manage_invoice_tab = QWidget()
        self.tabs.addTab(self.manage_invoice_tab, "Quản lý Hóa đơn")

        layout = QVBoxLayout()

        # Thêm ô nhập để tìm kiếm hóa đơn theo ID
        self.invoice_search_input = QLineEdit()
        self.invoice_search_input.setPlaceholderText("Nhập ID hóa đơn để tìm kiếm")
        self.invoice_search_input.textChanged.connect(self.search_invoices_by_id)  # Gọi hàm tìm kiếm khi nhập
        layout.addWidget(self.invoice_search_input)

        self.invoice_list_table = QTableWidget()
        self.invoice_list_table.setColumnCount(5)
        self.invoice_list_table.setHorizontalHeaderLabels(["ID Hóa đơn", "Tên Khách hàng", "Tổng tiền", "Trạng thái", "Ngày tạo"])
        self.invoice_list_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Khóa bảng không cho chỉnh sửa
        self.invoice_list_table.cellDoubleClicked.connect(self.show_invoice_popup)  # Kích hoạt khi nhấp đúp
        layout.addWidget(self.invoice_list_table)

        self.manage_invoice_tab.setLayout(layout)
        self.load_invoices()

    def search_invoices_by_id(self):
        """Tìm kiếm hóa đơn theo ID được nhập trong ô tìm kiếm."""
        search_text = self.invoice_search_input.text()
    
        if search_text.isdigit():  # Kiểm tra nếu giá trị là số
            conn = sqlite3.connect('management.db')
            cursor = conn.cursor()
    
            # Tìm kiếm các hóa đơn có ID bắt đầu bằng giá trị được nhập
            cursor.execute("""
                SELECT Invoice.id, Customer.name, Invoice.total, Invoice.status, Invoice.date
                FROM Invoice
                JOIN Customer ON Invoice.customer_id = Customer.id
                WHERE Invoice.id LIKE ?
                ORDER BY Invoice.id DESC
            """, (search_text + '%',))  # Sử dụng LIKE để tìm kiếm các hóa đơn có ID phù hợp
            invoices = cursor.fetchall()
            conn.close()
    
            # Hiển thị các hóa đơn đã tìm thấy trong bảng
            self.invoice_list_table.setRowCount(0)  # Xóa bảng hiện tại
            for row_data in invoices:
                row_number = self.invoice_list_table.rowCount()
                self.invoice_list_table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    if isinstance(data, int):
                        self.invoice_list_table.setItem(row_number, column_number, QTableWidgetItem(f"{data:,}"))
                    else:
                        self.invoice_list_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        else:
            self.load_invoices()  # Nếu không có dữ liệu nhập, tải lại toàn bộ hóa đơn    
    
    def load_invoices(self):
        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()

        cursor.execute("SELECT Invoice.id, Customer.name, Invoice.total, Invoice.status, Invoice.date FROM Invoice JOIN Customer ON Invoice.customer_id = Customer.id ORDER BY Invoice.id DESC")
        invoices = cursor.fetchall()
        self.invoice_list_table.setRowCount(0)
        for row_data in invoices:
            row_number = self.invoice_list_table.rowCount()
            self.invoice_list_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                if isinstance(data, int):
                    self.invoice_list_table.setItem(row_number, column_number, QTableWidgetItem(f"{data:,}"))
                else:
                    self.invoice_list_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        conn.close()

    def show_invoice_popup(self, row, column): 
        invoice_id_item = self.invoice_list_table.item(row, 0)  # Cột ID hóa đơn
        if invoice_id_item:
            invoice_id = int(invoice_id_item.text())

            conn = sqlite3.connect('management.db')
            cursor = conn.cursor()

            # Lấy thông tin hóa đơn và khách hàng
            cursor.execute("""
                SELECT Customer.name, Invoice.total, Invoice.status, Invoice.notes, Invoice.payment_date, Invoice.received_amount, Customer.notes, Invoice.debt_pre
                FROM Invoice
                JOIN Customer ON Invoice.customer_id = Customer.id
                WHERE Invoice.id = ?
            """, (invoice_id,))
            invoice_data = cursor.fetchone()

            # Lấy thông tin sản phẩm trong hóa đơn
            cursor.execute("""
                SELECT InvoiceProduct.product_name, InvoiceProduct.quantity, InvoiceProduct.total, InvoiceProduct.price
                FROM InvoiceProduct
                WHERE InvoiceProduct.invoice_id = ?
            """, (invoice_id,))
            product_data = cursor.fetchall()
            conn.close()

            dialog = QDialog(self)
            dialog.setWindowTitle("Chi tiết hóa đơn")
            dialog.setFixedSize(670, 800)  # Thiết lập kích thước cố định

            form_layout = QFormLayout(dialog)

            form_layout.addRow("Khách hàng:", QLabel(invoice_data[0]))
            form_layout.addRow("Tổng tiền hóa đơn:", QLabel(f"{invoice_data[1]:,}"))
            form_layout.addRow("Nợ cũ:", QLabel(f"{invoice_data[7]:,}"))
            form_layout.addRow("Tổng tiền:", QLabel(f"{invoice_data[7] + invoice_data[1]:,}"))
            form_layout.addRow("Trạng thái:", QLabel(invoice_data[2]))
            form_layout.addRow("Ghi chú:", QLabel(invoice_data[3]))  # Ghi chú hóa đơn chỉ hiển thị, không sửa
            form_layout.addRow("Ngày thanh toán:", QLabel(invoice_data[4] if invoice_data[4] else "Chưa thanh toán"))

            # Hiển thị sản phẩm trong bảng với các cột đầy đủ
            product_table = QTableWidget()
            product_table.setColumnCount(4)
            product_table.setHorizontalHeaderLabels(["Tên sản phẩm", "Số lượng", "Giá", "Tổng tiền"])
            product_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Không cho chỉnh sửa
            product_table.setRowCount(len(product_data))


            for row, product in enumerate(product_data):
                product_table.setItem(row, 0, QTableWidgetItem(product[0]))  # Tên sản phẩm
                product_table.setItem(row, 1, QTableWidgetItem(f"{product[1]:,}"))  # Số lượng
                product_table.setItem(row, 2, QTableWidgetItem(f"{product[3]:,}"))  # Giá
                product_table.setItem(row, 3, QTableWidgetItem(f"{product[2]:,}"))  # Tổng tiền

            form_layout.addRow("Sản phẩm:", product_table)

            # Khởi tạo QLineEdit để nhập số tiền đã nhận
            self.received_amount_input = QLineEdit()  # Đảm bảo biến được khởi tạo trước khi dùng
            self.received_amount_input.setValidator(QIntValidator())
            self.received_amount_input.setText(str(invoice_data[5]))  # Lấy số tiền đã nhận từ Invoice
            form_layout.addRow("Số tiền đã nhận:", self.received_amount_input)

            # Lấy ghi chú của khách hàng hiện tại từ Customer và hiển thị trong ô để chỉnh sửa
            self.invoice_notes_input = QLineEdit()
            self.invoice_notes_input.setText(invoice_data[6])  # Ghi chú của khách hàng (cột thứ 6 trong query)
            form_layout.addRow("Ghi chú mới:", self.invoice_notes_input)

            # Cập nhật trạng thái
            self.invoice_status_combobox = QComboBox()
            self.invoice_status_combobox.addItems(["đang được giao", "đã thanh toán", "chưa thanh toán"])
            self.invoice_status_combobox.setCurrentText(invoice_data[2])
            form_layout.addRow("Trạng thái hóa đơn:", self.invoice_status_combobox)

            # Chọn ngày thanh toán
            self.payment_date_edit = QDateEdit()
            self.payment_date_edit.setCalendarPopup(True)
            self.payment_date_edit.setDisplayFormat("yyyy-MM-dd")
            if invoice_data[4]:
                self.payment_date_edit.setDate(QDate.fromString(invoice_data[4], "yyyy-MM-dd"))
            else:
                self.payment_date_edit.setDate(QDate.currentDate())
            form_layout.addRow("Ngày thanh toán:", self.payment_date_edit)

            # Nút cập nhật
            update_button = QPushButton("Cập nhật")
            update_button.clicked.connect(lambda: self.update_invoice_status(invoice_id))
            form_layout.addWidget(update_button)

            # Thêm thông báo cập nhật thành công
            self.update_message_label = QLabel("")
            form_layout.addRow(self.update_message_label)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)
            button_box.accepted.connect(self.refresh_all_data)  # Làm mới dữ liệu khi tắt popup
            form_layout.addWidget(button_box)

            dialog.exec_()

    def update_invoice_status(self, invoice_id):
        """Cập nhật số tiền đã nhận, trạng thái và ngày thanh toán của hóa đơn. Cập nhật ghi chú của khách hàng."""

        # Nhận giá trị từ các input
        new_received_amount = int(self.received_amount_input.text())
        status = self.invoice_status_combobox.currentText()
        payment_date = self.payment_date_edit.date().toString("yyyy-MM-dd")
        customer_note = self.invoice_notes_input.text()  # Ghi chú mới của khách hàng

        conn = sqlite3.connect('management.db')
        cursor = conn.cursor()

        # Lấy số tiền đã nhận trước đó từ hóa đơn để trừ đúng cách
        cursor.execute("SELECT received_amount FROM Invoice WHERE id = ?", (invoice_id,))
        previous_received_amount = cursor.fetchone()[0]  # Số tiền đã nhận trước đây

        # Lấy số nợ hiện tại của khách hàng
        cursor.execute("SELECT Customer.id, Customer.debt FROM Customer JOIN Invoice ON Invoice.customer_id = Customer.id WHERE Invoice.id = ?", (invoice_id,))
        customer_id, current_debt = cursor.fetchone()

        # Tính lại số nợ trước khi cập nhật
        updated_debt = current_debt + previous_received_amount - new_received_amount  # Trừ số tiền nhận trước đó, cộng số tiền nhận mới

        # Cập nhật số tiền đã nhận, trạng thái và ngày thanh toán trong bảng hóa đơn (không thay đổi ghi chú hóa đơn)
        cursor.execute("""
            UPDATE Invoice 
            SET received_amount = ?, status = ?, payment_date = ?
            WHERE id = ?
        """, (new_received_amount, status, payment_date, invoice_id))
        conn.commit()

        # Cập nhật ghi chú và nợ của khách hàng (ghi chú của khách hàng được cập nhật)
        cursor.execute("""
            UPDATE Customer 
            SET debt = ?, notes = ?
            WHERE id = ?
        """, (updated_debt, customer_note, customer_id))

        conn.commit()
        conn.close()

        # Hiển thị thông báo cập nhật thành công
        self.update_message_label.setText("Cập nhật thành công!")

        # Làm mới dữ liệu sau khi cập nhật
        self.load_invoices()
        self.refresh_all_data()

if __name__ == '__main__':
    create_tables()

    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
