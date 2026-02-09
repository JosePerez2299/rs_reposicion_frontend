
from utils.api_client import get_products

def product_filter(box):
    box.subheader("Productos")
    
    opciones = get_products()

    if opciones:
        seleccionados = box.multiselect(
            "Busca por ID o nombre:",
            options=opciones,
            format_func=lambda x: f"{x['name']}",
            default=[]
        )
        
        if seleccionados:
            ids_seleccionados = [item["product_id"] for item in seleccionados]
            
            return ids_seleccionados
        
        return []