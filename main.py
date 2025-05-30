import graphviz
import csv
import codecs



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

    arbol.exportar_png("arbol_entidades")
    arbol.importar_csv("entidades - copia.csv",";")
    arbol.exportar_csv("entidades.csv",";")

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