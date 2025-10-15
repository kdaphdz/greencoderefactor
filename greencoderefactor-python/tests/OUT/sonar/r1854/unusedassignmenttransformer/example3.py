class ProcesadorDeDatos:

    def __init__(self, datos):
        self.datos = datos
        self.resultado = []
        self.estado = 'listo'

    def limpiar_datos(self):
        datos_limpios = [d.strip() for d in self.datos if isinstance(d, str)]
        self.datos = datos_limpios

    def procesar(self):
        resultado = self._filtrar_datos()
        self.resultado = resultado

    def _filtrar_datos(self):
        temp = [d for d in self.datos if d]
        return [d.upper() for d in temp if isinstance(d, str)]

    def exportar(self):
        salida = ''
        if not self.resultado:
            self.procesar()
        salida = '\n'.join(self.resultado)
        return salida