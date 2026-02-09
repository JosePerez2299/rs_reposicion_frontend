
from utils.api_client import get_stores

def store_filter(box):
    box.subheader("Tiendas")
    
    opciones = get_stores()

    if opciones:
        seleccionados = box.multiselect(
            "Busca por ID o nombre:",
            options=opciones,
            format_func=lambda x: f"{x['store_id']} - {x['name']}",
            default=[]
        )
        
        if seleccionados:
            ids_seleccionados = [item["store_id"] for item in seleccionados]
            
            return ids_seleccionados
        
        return []