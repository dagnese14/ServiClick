from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

Builder.load_string('''
<ProductManagerPopup>:
    id: product_manager
    title: 'Gestión de Productos'
    size_hint: 0.9, 0.9
    auto_dismiss: False
    db_manager: None
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        # Formulario para agregar productos
        Label:
            text: 'Agregar Nuevo Producto'
            font_size: '20sp'
            size_hint_y: None
            height: 40
        
        GridLayout:
            cols: 2
            spacing: 5
            size_hint_y: None
            height: 150
            
            Label:
                text: 'Nombre del Producto:'
            TextInput:
                id: product_name_input
                multiline: False
            
            Label:
                text: 'Precio (USD):'
            TextInput:
                id: price_usd_input
                multiline: False
                input_filter: 'float'
            
            Label:
                text: 'Inventario Inicial:'
            TextInput:
                id: stock_input
                multiline: False
                input_filter: 'int'
            
            Label:
                text: 'Tipo (producto/bebida/promocion):'
            TextInput:
                id: type_input
                multiline: False

        BoxLayout:
            size_hint_y: None
            height: 40
            Button:
                text: 'Guardar Producto'
                on_release: root.save_product()
            Button:
                text: 'Cerrar'
                on_release: root.dismiss()

        Label:
            text: 'Inventario Existente'
            font_size: '20sp'
            size_hint_y: None
            height: 40
            
        ScrollView:
            GridLayout:
                id: inventory_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                
    def on_open(self):
        self.load_inventory()

    def load_inventory(self):
        self.ids.inventory_grid.clear_widgets()
        products = self.db_manager.get_products()
        for prod in products:
            box = BoxLayout(size_hint_y=None, height=44, spacing=5)
            box.add_widget(Label(text=f"{prod[1]} - Stock: {prod[3]}"))
            
            add_stock_input = TextInput(multiline=False, input_filter='int', hint_text='Cantidad')
            add_stock_btn = Button(text='Añadir')
            add_stock_btn.bind(on_release=lambda *args, p_id=prod[0], s_input=add_stock_input: self.add_stock_to_product(p_id, s_input))

            box.add_widget(add_stock_input)
            box.add_widget(add_stock_btn)
            self.ids.inventory_grid.add_widget(box)

    def add_stock_to_product(self, product_id, stock_input):
        try:
            stock_to_add = int(stock_input.text)
            self.db_manager.add_product_stock(product_id, stock_to_add)
            stock_input.text = ''
            self.load_inventory()
        except ValueError:
            pass # Ignorar si no es un número

    def save_product(self):
        name = self.ids.product_name_input.text
        price_usd_str = self.ids.price_usd_input.text
        stock_str = self.ids.stock_input.text
        prod_type = self.ids.type_input.text
        
        if not name or not price_usd_str or not stock_str or not prod_type:
            return
        
        try:
            price_usd = float(price_usd_str)
            stock = int(stock_str)
            self.db_manager.add_product(name, price_usd, stock, prod_type)
            self.ids.product_name_input.text = ''
            self.ids.price_usd_input.text = ''
            self.ids.stock_input.text = ''
            self.ids.type_input.text = ''
            self.load_inventory()
        except ValueError:
            pass