import graphviz
import csv
import codecs
import folium
from math import radians, sin, cos, sqrt, atan2

class Grafo:
    def __init__(self):
        self.vertices = {}  # clave: id_entidad, valor: lista de (id_vecino, distancia, tiempo, costo)

    def agregar_vertice(self, entidad):
        if entidad.identificador not in self.vertices:
            self.vertices[entidad.identificador] = []

    def agregar_arista(self, origen, destino, distancia_km, tiempo_horas, costo):
        self.vertices[origen].append((destino, distancia_km, tiempo_horas, costo))
        self.vertices[destino].append((origen, distancia_km, tiempo_horas, costo))  # Si es bidireccional

def puntuar_ruta(entidades, ruta, presupuesto, tiempo_maximo):
    tiempo_total = 0
    costo_total = 0
    score_total = 0

    for id_entidad in ruta:
        entidad = entidades[id_entidad]
        if entidad.tipo == "Turístico":
            tiempo_total += entidad.tiempo_estimado
            costo_total += entidad.precio
            score_total += entidad.calificacion_promedio
        if tiempo_total > tiempo_maximo or costo_total > presupuesto:
            return -1  # Ruta inválida

    return score_total  # A mayor puntuación, mejor

def buscar_mejores_rutas(grafo, entidades, origen, presupuesto, tiempo_maximo, max_rutas=5):
    mejores_rutas = []

    def dfs(ruta_actual, tiempo_acumulado, costo_acumulado, score_acumulado):
        ultimo = ruta_actual[-1]
        if len(ruta_actual) > 1:
            puntuacion = puntuar_ruta(entidades, ruta_actual, presupuesto, tiempo_maximo)
            if puntuacion > 0:
                mejores_rutas.append((puntuacion, list(ruta_actual)))

        if len(mejores_rutas) >= max_rutas:
            return

        for vecino, _, tiempo, costo in grafo.vertices.get(ultimo, []):
            if vecino in ruta_actual:
                continue  # No repetir
            entidad_vecina = entidades[vecino]
            tiempo_total = tiempo_acumulado + tiempo + entidad_vecina.tiempo_estimado
            costo_total = costo_acumulado + costo + entidad_vecina.precio
            if tiempo_total <= tiempo_maximo and costo_total <= presupuesto:
                ruta_actual.append(vecino)
                dfs(ruta_actual, tiempo_total, costo_total, score_acumulado + entidad_vecina.calificacion_promedio)
                ruta_actual.pop()

    dfs([origen], 0, 0, 0)
    mejores_rutas.sort(reverse=True)
    return mejores_rutas[:max_rutas]


def mostrar_ruta_mapa(entidades, ruta):
    m = folium.Map(location=[entidades[ruta[0]].latitud, entidades[ruta[0]].longitud], zoom_start=13)
    for i in range(len(ruta)):
        entidad = entidades[ruta[i]]
        folium.Marker([entidad.latitud, entidad.longitud], tooltip=entidad.nombre).add_to(m)
        if i > 0:
            origen = entidades[ruta[i - 1]]
            destino = entidad
            folium.PolyLine([(origen.latitud, origen.longitud), (destino.latitud, destino.longitud)],
                            color="blue").add_to(m)
    m.save("ruta.html")

class Entidad:
    def __init__(self, identificador, nombre, tipo, latitud, longitud,
                 precio, calificacion_promedio, tiempo_estimado=None):
        self.identificador = identificador
        self.nombre = nombre
        self.tipo = tipo  # "Hospedaje" o "Turístico"
        self.latitud = latitud
        self.longitud = longitud
        self.precio = precio
        self.calificacion_promedio = calificacion_promedio
        self.tiempo_estimado = tiempo_estimado  # Solo para tipo "Turístico"
        self.comentarios = []  # Lista de tuplas: (usuario, calificación, comentario)

    def agregar_comentario(self, usuario, calificacion, comentario):
        self.comentarios.append((usuario, calificacion, comentario))

    def __lt__(self, other):
        return self.identificador < other.identificador

    def __eq__(self, other):
        return self.identificador == other.identificador

    def __str__(self):
        return f"{self.nombre}({self.identificador})"

    def printdatos(self):
        print(self.identificador, self.nombre, self.tipo, self.latitud, self.longitud, self.precio, self.calificacion_promedio, self.tiempo_estimado)

    def obtener_etiqueta(self):
        return (
        f"ID: {self.identificador}\\n"
        f"{self.nombre}\\n"
        f"Tipo: {self.tipo}\\n"
        f"Precio: ${self.precio}\\n"
        f"Calificación: {self.calificacion_promedio}\\n"
        f"{'Tiempo: ' + str(self.tiempo_estimado) + 'h' if self.tipo == 'Turístico' else ''}"
    )


class NodoArbolB:
    def __init__(self, grado, hoja=False):
        self.grado = grado                # Grado mínimo del árbol
        self.hoja = hoja                  # True si el nodo es una hoja
        self.claves = []                  # Lista de claves
        self.hijos = []                   # Lista de hijos

    def recorrer(self):
        """Recorre el nodo e imprime las claves en orden."""
        for i in range(len(self.claves)):
            if not self.hoja:
                self.hijos[i].recorrer()
            print(self.claves[i], end=" ")
        if not self.hoja:
            self.hijos[len(self.claves)].recorrer()

    def recorrer_entidades(self, lista):
        for i in range(len(self.claves)):
            if not self.hoja:
                self.hijos[i].recorrer_entidades(lista)
            lista.append(self.claves[i])
        if not self.hoja:
            self.hijos[len(self.claves)].recorrer_entidades(lista)

    def buscar(self, clave):
        """Busca una clave dentro del nodo (o en sus hijos)."""
        i = 0
        while i < len(self.claves) and clave > self.claves[i]:
            i += 1

        if i < len(self.claves) and self.claves[i] == clave:
            return self

        if self.hoja:
            return None

        return self.hijos[i].buscar(clave)

    def insertar_no_lleno(self, clave):
        """Inserta una clave en un nodo que no está lleno."""
        i = len(self.claves) - 1

        if self.hoja:
            self.claves.append(None)
            while i >= 0 and clave < self.claves[i]:
                self.claves[i + 1] = self.claves[i]
                i -= 1
            self.claves[i + 1] = clave
        else:
            while i >= 0 and clave < self.claves[i]:
                i -= 1
            i += 1

            if len(self.hijos[i].claves) == 2 * self.grado - 1:
                self.dividir_hijo(i)

                if clave > self.claves[i]:
                    i += 1

            self.hijos[i].insertar_no_lleno(clave)

    def dividir_hijo(self, i):
        """Divide el hijo i en dos cuando está lleno."""
        t = self.grado
        y = self.hijos[i]
        z = NodoArbolB(t, y.hoja)

        z.claves = y.claves[t:]  # Copiar la segunda mitad
        y.claves = y.claves[:t - 1]

        if not y.hoja:
            z.hijos = y.hijos[t:]
            y.hijos = y.hijos[:t]

        self.hijos.insert(i + 1, z)
        self.claves.insert(i, y.claves.pop())



class ArbolB:
    def __init__(self, grado):
        self.raiz = NodoArbolB(grado, True)
        self.grado = grado

    def recorrer(self):
        """Imprime todas las claves del árbol en orden."""
        if self.raiz:
            self.raiz.recorrer()
            print()

    def buscar(self, clave):
        """Busca una clave en el árbol. Devuelve (nodo, índice) si lo encuentra, de lo contrario (None, -1)."""
        def _buscar(nodo, clave):
            i = 0
            while i < len(nodo.claves) and clave > nodo.claves[i]:
                i += 1
            if i < len(nodo.claves) and nodo.claves[i] == clave:
                return nodo, i
            if nodo.hoja:
                return None, -1
            return _buscar(nodo.hijos[i], clave)

        return _buscar(self.raiz, clave)

    def insertar(self, clave):
        """Inserta una nueva clave o actualiza si el ID ya existe."""
        nodo_existente, indice = self.buscar(clave)
        print("Resultado buscador: ", indice)
        if nodo_existente:  # Ya existe, no actualizamos, solo alertamos
            #nodoactual = nodo_existente.claves[indice]
            #nodoactual = clave
            #nodo_existente.claves[indice] = nodoactual
            print(f"Entidad con ID {clave.identificador} no puede registrarse nuevamente.")
            return

        raiz = self.raiz
        if len(raiz.claves) == 2 * self.grado - 1:
            nueva_raiz = NodoArbolB(self.grado, False)
            nueva_raiz.hijos.insert(0, raiz)
            nueva_raiz.dividir_hijo(0)

            i = 0
            if clave > nueva_raiz.claves[0]:
                i += 1

            nueva_raiz.hijos[i].insertar_no_lleno(clave)
            self.raiz = nueva_raiz
        else:
            raiz.insertar_no_lleno(clave)

    def generar_dot(self):
        """Genera el código en formato DOT para visualizar con Graphviz."""
        dot = ["digraph ArbolB {", "node [shape=record];"]
        contador = [0]

        def recorrer_nodo(nodo):
            id_actual = f"n{contador[0]}"
            contador[0] += 1

            etiquetas = "|".join(k.obtener_etiqueta() for k in nodo.claves)

            dot.append(f'{id_actual} [label="{{{etiquetas}}}"];')

            hijos_ids = []
            for hijo in nodo.hijos:
                id_hijo = recorrer_nodo(hijo)
                hijos_ids.append(id_hijo)
                dot.append(f"{id_actual} -> {id_hijo};")

            return id_actual

        recorrer_nodo(self.raiz)
        dot.append("}")
        
        for punto in dot: #punto debug para revisión de gráfico generado
            print(punto)

        return "\n".join(dot)


    def exportar_png(self, nombre_archivo="arbol_b"):
        """Genera y guarda el árbol B como imagen PNG."""
        dot_code = self.generar_dot()
        grafico = graphviz.Source(dot_code)
        grafico.format = 'png'
        grafico.render(filename=nombre_archivo, cleanup=True)
        print(f"Imagen generada: {nombre_archivo}.png")

    def exportar_csv(self, nombre_archivo="entidades.csv", delimitador=","):
        entidades = []
        self.raiz.recorrer_entidades(entidades)
        with codecs.open(nombre_archivo, mode="w", encoding="utf-8-sig") as archivo:
            writer = csv.writer(archivo, delimiter=delimitador)
            writer.writerow([
                "ID", "Nombre", "Tipo", "Latitud", "Longitud",
                "Precio", "Calificación", "Tiempo Estimado"
            ])
            for e in entidades:
                writer.writerow([
                    e.identificador, e.nombre, e.tipo,
                    e.latitud, e.longitud, e.precio,
                    e.calificacion_promedio, e.tiempo_estimado or ""
                ])
        print(f"CSV exportado como: {nombre_archivo} (delimitador='{delimitador}')")

    def importar_csv(self, nombre_archivo="entidades.csv", delimitador=";"):
        """Importa entidades desde un archivo CSV y las inserta en el árbol."""
        try:
            with open(nombre_archivo, mode="r", encoding="utf-8-sig") as archivo:
                
                reader = csv.DictReader(archivo, delimiter=delimitador)
                print("Encabezados detectados:", reader.fieldnames)  # 👈 Esto muestra los nombres reales
                for fila in reader:
                    id_entidad = int(fila["ID"])
                    nombre = fila["Nombre"]
                    tipo = fila["Tipo"]
                    latitud = float(fila["Latitud"])
                    longitud = float(fila["Longitud"])
                    precio = float(fila["Precio"])
                    calificacion = float(fila["Calificación"])
                    tiempo_estimado = fila["Tiempo Estimado"]
                    entidad = Entidad(
                        id_entidad,
                        nombre,
                        tipo,
                        latitud,
                        longitud,
                        precio,
                        calificacion,
                        tiempo_estimado
                    )
                    entidad.printdatos()
                    self.insertar(entidad)
            print(f"Importación de '{nombre_archivo}' completada con éxito.")
        except Exception as e:
            print(f"Error al importar CSV: {e}")


def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en kilómetros

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def obtener_entidades_desde_arbol(arbol_b):
    entidades = []
    arbol_b.raiz.recorrer_entidades(entidades)
    return entidades

def agregar_aristas_automaticamente(arbol_b, grafo):
    entidades = obtener_entidades_desde_arbol(arbol_b)
    
    for i in range(len(entidades)):
        for j in range(i + 1, len(entidades)):
            origen = entidades[i]
            destino = entidades[j]

            distancia = calcular_distancia_km(origen.latitud, origen.longitud, destino.latitud, destino.longitud)
            tiempo = distancia / 40  # Suponiendo 40 km/h promedio
            costo = distancia * 2    # Suponiendo $2 por km

            grafo.agregar_arista(origen.identificador, destino.identificador, distancia, tiempo, costo)

if __name__ == "__main__":
    arbol = ArbolB(grado=3)  # Árbol B de orden 3 (máximo 5 claves por nodo)


    entidades = [
        Entidad(10, "Hotel Sol", "Hospedaje", 14.1, -90.5, 100, 4.5),
        Entidad(20, "Museo de Arte", "Turístico", 14.3, -90.7, 0, 4.8, tiempo_estimado=2),
        Entidad(5, "Eco Lodge", "Hospedaje", 14.0, -90.6, 80, 4.2),
        Entidad(6, "Parque Nacional", "Turístico", 14.4, -90.8, 5, 4.7, tiempo_estimado=4),
        Entidad(12, "Café del Lago", "Hospedaje", 14.2, -90.55, 50, 4.0),
        Entidad(30, "Zoológico", "Turístico", 14.5, -90.9, 10, 4.6, tiempo_estimado=3),
        Entidad(7, "Hostal Maya", "Hospedaje", 14.0, -90.52, 60, 4.1),
        Entidad(17, "Ruinas Mayas", "Turístico", 14.6, -91.0, 15, 4.9, tiempo_estimado=5)
    ]

    for entidad in entidades:
        arbol.insertar(entidad)

    print("Recorrido del árbol en orden:")
    arbol.recorrer()

    nodo_existente, indice  = arbol.buscar(Entidad(12, "", "", 0, 0, 0, 0))  # Solo importa el ID
    if nodo_existente:
        print(f"\nEntidad con ID 12 encontrada: {[str(e) for e in nodo_existente.claves]}")
    else:
        print("\nEntidad con ID 12 NO encontrada.")

    arbol.exportar_csv("entidades_original.csv",";")
    arbol.exportar_png("arbol_entidades")
    arbol.importar_csv("entidades - copia.csv",";")
    arbol.exportar_csv("entidades_modificado.csv",";")


    grafo = Grafo()

    # Obtener entidades del árbol B para agregarlas como vértices
    def obtener_entidades_desde_arbol(arbol):
        lista = []
        arbol.raiz.recorrer_entidades(lista)
        return lista

    # Función para agregar aristas de forma automática
    def agregar_aristas_automaticamente(arbol, grafo):
        entidades = obtener_entidades_desde_arbol(arbol)
        for i in range(len(entidades)):
            for j in range(i + 1, len(entidades)):
                origen = entidades[i]
                destino = entidades[j]
                distancia = calcular_distancia(origen.latitud, origen.longitud, destino.latitud, destino.longitud)
                tiempo = distancia / 50  # Por ejemplo, 50 km/h
                costo = 10  # Coste arbitrario o basado en lógica
                grafo.agregar_arista(origen.identificador, destino.identificador, distancia, tiempo, costo)

    # Función para calcular distancia
    def calcular_distancia(lat1, lon1, lat2, lon2):
        R = 6371  # Radio de la Tierra en km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    # Construir el grafo
    for entidad in obtener_entidades_desde_arbol(arbol):
        grafo.agregar_vertice(entidad)

    agregar_aristas_automaticamente(arbol, grafo)
    
    entidades = {}
    
    # Obtener lista de entidades
    lista_entidades = []
    arbol.raiz.recorrer_entidades(lista_entidades)

    # Construir el diccionario de entidades
    entidades = {entidad.identificador: entidad for entidad in lista_entidades}

    # Crear el mapa centrado en la primera entidad (si hay al menos una)
    if lista_entidades:
        primera = lista_entidades[0]
        mapa = folium.Map(location=[primera.latitud, primera.longitud], zoom_start=12)

        # Agregar marcadores
        for entidad in lista_entidades:
            folium.Marker(
                [entidad.latitud, entidad.longitud],
                popup=f"{entidad.nombre} ({entidad.tipo})",
                tooltip=f"${entidad.precio} - Calificación: {entidad.calificacion_promedio}",
                icon=folium.Icon(color="green" if entidad.tipo == "Hospedaje" else "blue")
            ).add_to(mapa)

        # Dibujar aristas del grafo como líneas
        for origen_id, conexiones in grafo.vertices.items():
            origen = entidades[origen_id]
            for destino_id, _, _, _ in conexiones:
                destino = entidades[destino_id]
                folium.PolyLine(
                    [(origen.latitud, origen.longitud), (destino.latitud, destino.longitud)],
                    color='gray', weight=2, opacity=0.6
                ).add_to(mapa)

        # Guardar el mapa
        mapa.save("mapa_entidades.html")
        print("Mapa guardado como mapa_entidades.html")
    else:
        print("No hay entidades para mostrar en el mapa.")

    #claves = [10, 20, 5, 6, 12, 30, 7, 17]
    #for clave in claves:
        #arbol.insertar(clave)

    #print("Recorrido del árbol en orden:")
    #arbol.recorrer()

    #clave_a_buscar = 12
    #resultado = arbol.buscar(clave_a_buscar)
    #if resultado:
        #print(f"\nLa clave {clave_a_buscar} fue encontrada en el árbol.")
    #else:
        #print(f"\nLa clave {clave_a_buscar} NO está en el árbol.")
        
    # Exportar a formato DOT
    #dot_code = arbol.generar_dot()
    #with open("arbol_b.dot", "w") as f:
        #f.write(dot_code)
    #print("\nArchivo 'arbol_b.dot' generado. Puedes visualizarlo con Graphviz.")
    
    ## Exportar como imagen PNG
    #arbol.exportar_png("mi_arbol_b")  # Esto crea "mi_arbol_b.png"