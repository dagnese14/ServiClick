from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout as KivyBoxLayout
from kivy.uix.radiobutton import RadioButton
from kivy.uix.textinput import TextInput
from database import DatabaseManager
from product_manager import ProductManagerPopup
from sale_manager import SaleManager
from customer_manager import CustomerManagerPopup
from kivy.uix.spinner import Spinner

# Cargar el archivo .kv
Builder.load_file('kivy_pos.kv')

class ProductButton(Button):
    product_data = ObjectProperty(None)

class PaymentPopup(Popup):
    payment_amount_usd = ObjectProperty(None)
    payment_amount_bs = ObjectProperty(None)
    payment_method = StringProperty('Efectivo')
    change_label = ObjectProperty(None)
    clients_list = ListProperty([])
    selected_client_id = ObjectProperty(None)
    
class ReportsPopup(Popup):
    pass

class MainLayout(BoxLayout):
    db = ObjectProperty(None)
    exchange_rate = StringProperty("N/A")
    products = ListProperty([])
    clients = ListProperty([])
    
    sale_manager = ObjectProperty(None)
    cart_items = ListProperty([])
    total_usd = StringProperty('$ 0.00')
    total_bs = StringProperty('Bs. 0.00')
    
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.db = DatabaseManager()
        self.sale_manager = SaleManager()
        self.load_initial_data()
        
    def load_initial_data(self):
        rate = self.db.get_exchange_rate()
        if rate:
            self.exchange_rate = f"{rate:.2f}"
        else:
            self.exchange_rate = "Tasa no establecida"
            
        self.products = self.db.get_products()
        self.clients = self.db.get_clients()
        
        self.ids.product_grid.clear_widgets()
        for prod in self.products:
            btn = ProductButton(text=prod[1], product_data=prod)
            btn.bind(on_release=self.on_product_press)
            self.ids.product_grid.add_widget(btn)

    def on_product_press(self, instance):
        product_data = instance.product_data
        subproducts = self.db.get_subproducts(product_data[0])
        
        if subproducts:
            self.show_subproduct_popup(product_data, subproducts)
        else:
            self.add_item_to_cart(product_data)
            self.update_cart_display()

    def show_subproduct_popup(self, product_data, subproducts):
        box = KivyBoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text=f"Seleccione tipo de {product_data[1]}", size_hint_y=None, height=40))
        
        for sub in subproducts:
            btn = Button(text=f"{sub[2]} (+${sub[3]:.2f})")
            btn.bind(on_release=lambda *args, prod=product_data, sub=sub: self.add_item_and_dismiss(prod, sub))
            box.add_widget(btn)

        popup = Popup(title='Seleccionar Subproducto', content=box, size_hint=(0.7, 0.7))
        self.current_popup = popup
        popup.open()
        
    def add_item_and_dismiss(self, product_data, subproduct_data):
        self.sale_manager.add_item(product_data, subproduct_data)
        self.update_cart_display()
        self.current_popup.dismiss()

    def add_item_to_cart(self, product_data):
        self.sale_manager.add_item(product_data)
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_items = self.sale_manager.get_cart_items_display()
        rate = float(self.exchange_rate) if self.exchange_rate != "Tasa no establecida" else 0
        self.sale_manager.update_totals(rate)
        self.total_usd = f'$ {self.sale_manager.total_usd:.2f}'
        self.total_bs = f'Bs. {self.sale_manager.total_bs:.2f}'
    
    def open_payment_popup(self):
        if not self.sale_manager.cart:
            return
        
        self.payment_popup = PaymentPopup()
        self.payment_popup.total_usd = self.sale_manager.total_usd
        self.payment_popup.total_bs = self.sale_manager.total_bs
        
        self.clients = self.db.get_clients() # Recargar la lista de clientes
        self.payment_popup.clients_list = [f"{c[1]} ({c[2]})" for c in self.clients]
        self.payment_popup.clients_list.insert(0, 'Sin Cliente')
        
        self.payment_popup.bind(on_dismiss=self.on_payment_popup_dismiss)
        self.payment_popup.open()
        
    def on_payment_popup_dismiss(self, instance):
        if instance.paid:
            self.process_payment(
                instance.total_usd,
                instance.payment_method,
                instance.selected_client_id
            )

    def process_payment(self, total_usd, payment_method, client_id):
        sale_id = self.db.record_sale(total_usd, payment_method, client_id)
        
        for item in self.sale_manager.cart:
            product_data = self.db.get_product_by_id(item['product_id'])
            if product_data:
                current_stock = product_data[3]
                self.db.add_sale_item(
                    sale_id,
                    item['product_name'],
                    item['subproduct_name'],
                    item['quantity'],
                    item['price_usd']
                )
                # Descontar del inventario
                self.db.add_product_stock(item['product_id'], -item['quantity'])
            else:
                print(f"Advertencia: Producto con ID {item['product_id']} no encontrado.")

        print(f"Venta #{sale_id} registrada con éxito.")

        self.sale_manager.clear_cart()
        self.load_initial_data() # Recargar datos para ver cambios en el stock
        self.update_cart_display()

    def open_reports_popup(self):
        popup = ReportsPopup(db_manager=self.db)
        popup.open()

    def open_customer_manager(self):
        popup = CustomerManagerPopup(db_manager=self.db)
        popup.bind(on_dismiss=lambda *args: self.load_initial_data()) # Recargar clientes al cerrar
        popup.open()
        
    def cancel_sale(self):
        self.sale_manager.clear_cart()
        self.update_cart_display()
        
    def show_product_manager(self):
        popup = ProductManagerPopup(db_manager=self.db)
        popup.bind(on_dismiss=lambda *args: self.load_initial_data())
        popup.open()
        
    def on_stop(self):
        self.db.close()

class FastFoodPOSApp(App):
    def build(self):
        return MainLayout()
    
    def get_parent_app(self):
        return self

if __name__ == '__main__':
    # ... código de Builder.load_string ...
    Builder.load_string('''
<PaymentPopup>:
    # ... (código existente del popup de pago) ...

<ReportsPopup>:
    title: 'Reportes de Ventas'
    size_hint: 0.9, 0.9
    db_manager: None
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        Label:
            text: 'Generar Reporte por Fecha'
            font_size: '20sp'
        
        GridLayout:
            cols: 2
            spacing: 5
            
            Label:
                text: 'Fecha de Inicio (YYYY-MM-DD):'
            TextInput:
                id: start_date_input
                multiline: False
            
            Label:
                text: 'Fecha de Fin (YYYY-MM-DD):'
            TextInput:
                id: end_date_input
                multiline: False
        
        Button:
            text: 'Generar Reporte'
            on_release: root.generate_report()
            
        ScrollView:
            GridLayout:
                cols: 1
                id: reports_grid
                size_hint_y: None
                height: self.minimum_height
                
        Button:
            text: 'Cerrar'
            on_release: root.dismiss()
            size_hint_y: None
            height: 40

    def generate_report(self):
        start_date = self.ids.start_date_input.text
        end_date = self.ids.end_date_input.text
        
        if not start_date or not end_date:
            self.ids.reports_grid.clear_widgets()
            self.ids.reports_grid.add_widget(Label(text="Error: Ingrese ambas fechas.", color=(1,0,0,1)))
            return

        # Limpiar el grid para nuevos reportes
        self.ids.reports_grid.clear_widgets()

        # Generar Reporte General
        sales_data = self.db_manager.get_sales_report(start_date, end_date)
        total_usd = sum(sale[2] for sale in sales_data)
        
        self.ids.reports_grid.add_widget(Label(text="--- Resumen General ---", font_size='18sp'))
        self.ids.reports_grid.add_widget(Label(text=f"Total de Ventas: ${total_usd:.2f}"))
        self.ids.reports_grid.add_widget(Label(text=f"Cantidad de Transacciones: {len(sales_data)}"))
        self.ids.reports_grid.add_widget(Label(text="")) # Espaciador

        # Generar Reporte por Producto
        product_summary = self.db_manager.get_sales_by_product_summary(start_date, end_date)
        if product_summary:
            self.ids.reports_grid.add_widget(Label(text="--- Ventas por Producto ---", font_size='18sp'))
            for product in product_summary:
                name, quantity, total = product
                self.ids.reports_grid.add_widget(Label(text=f"{name}: {quantity} unidades - ${total:.2f}"))
            self.ids.reports_grid.add_widget(Label(text="")) # Espaciador
        
        # Generar Reporte por Método de Pago
        payment_summary = self.db_manager.get_sales_by_payment_method(start_date, end_date)
        if payment_summary:
            self.ids.reports_grid.add_widget(Label(text="--- Ventas por Método de Pago ---", font_size='18sp'))
            for payment in payment_summary:
                method, total = payment
                self.ids.reports_grid.add_widget(Label(text=f"{method}: ${total:.2f}"))
            self.ids.reports_grid.add_widget(Label(text="")) # Espaciador
''')
    FastFoodPOSApp().run()