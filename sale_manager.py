class SaleManager:
    """Clase para gestionar el carrito de compra y la venta actual."""

    def __init__(self):
        self.cart = []
        self.total_usd = 0
        self.total_bs = 0

    def add_item(self, product_data, subproduct_data=None):
        """Agrega un producto o subproducto al carrito."""
        item = {
            'product_id': product_data[0],
            'product_name': product_data[1],
            'price_usd': product_data[2],
            'quantity': 1,
            'subproduct_name': None,
            'price_variation': 0
        }
        
        if subproduct_data:
            item['subproduct_name'] = subproduct_data[2]
            item['price_usd'] += subproduct_data[3]
            item['price_variation'] = subproduct_data[3]
            
        self.cart.append(item)
        self.update_totals()

    def update_totals(self, exchange_rate):
        """Recalcula los totales del carrito."""
        self.total_usd = sum(item['price_usd'] * item['quantity'] for item in self.cart)
        self.total_bs = self.total_usd * exchange_rate

    def clear_cart(self):
        """Limpia el carrito de compra."""
        self.cart = []
        self.total_usd = 0
        self.total_bs = 0

    def get_cart_items_display(self):
        """Retorna una lista de strings para mostrar en la interfaz."""
        display_list = []
        for item in self.cart:
            name = f"{item['product_name']}"
            if item['subproduct_name']:
                name += f" ({item['subproduct_name']})"
            display_list.append(f"{name} x{item['quantity']} - ${item['price_usd']:.2f}")
        return display_list