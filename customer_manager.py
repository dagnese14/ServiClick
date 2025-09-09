from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

Builder.load_string('''
<CustomerManagerPopup>:
    title: 'Gestor de Clientes'
    size_hint: 0.9, 0.9
    db_manager: None
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        GridLayout:
            cols: 2
            size_hint_y: None
            height: 100
            spacing: 5
            
            Label:
                text: 'Nombre:'
            TextInput:
                id: customer_name_input
                multiline: False
            
            Label:
                text: 'Teléfono:'
            TextInput:
                id: customer_phone_input
                multiline: False
                input_filter: 'int'
            
            Button:
                text: 'Agregar Cliente'
                on_release: root.add_customer()
            
            Button:
                text: 'Refrescar Lista'
                on_release: root.load_customers()
                
        ScrollView:
            GridLayout:
                id: customer_list_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                
        Button:
            text: 'Cerrar'
            on_release: root.dismiss()
            size_hint_y: None
            height: 40

''')

class CustomerManagerPopup(Popup):
    db_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CustomerManagerPopup, self).__init__(**kwargs)
        self.bind(on_open=self.load_customers)

    def load_customers(self):
        self.ids.customer_list_grid.clear_widgets()
        customers = self.db_manager.get_customers()
        for customer in customers:
            customer_id, name, phone = customer
            box = BoxLayout(size_hint_y=None, height=44)
            box.add_widget(Label(text=f'ID: {customer_id} | {name} | Tel: {phone}'))
            self.ids.customer_list_grid.add_widget(box)

    def add_customer(self):
        name = self.ids.customer_name_input.text
        phone = self.ids.customer_phone_input.text
        if name and phone:
            self.db_manager.add_customer(name, phone)
            self.ids.customer_name_input.text = ''
            self.ids.customer_phone_input.text = ''
            self.load_customers()
        else:
            self.ids.customer_name_input.text = "Error: Ambos campos son requeridos."