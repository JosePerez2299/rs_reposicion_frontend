import api.stores as stores

def store_filter(box):
    
    opciones = stores.get_stores()

    if opciones:
        seleccionados = box.multiselect(
            "Tiendas",
            options=opciones,
            format_func=lambda x: f"{x['store_id']} - {x['name']}",
            default=[],
            help="Selecciona ninguna o más tiendas",
            placeholder="Desplegar tiendas"
        )
        
        if seleccionados:
            ids_seleccionados = [item["store_id"] for item in seleccionados]
            
            return ids_seleccionados
        
        return []