# Macro Jython 2.7 para Modelio: casos de uso de "Reconoce tu Barrio: El Tintal".
# Si hay un paquete seleccionado lo usa; si no, usa la raiz del proyecto.
from org.modelio.api.modelio import Modelio

SISTEMA = u"Reconoce tu Barrio: El Tintal"
CASOS = [
    u"CU-01: Centros Educativos",
    u"CU-02: Escenarios Deportivos",
    u"CU-03: Sistemas de C\xe1maras de Seguridad",
    u"CU-04: Zonas Verdes",
    u"CU-05: Datos Catastrales",
    u"CU-06: Estado de Calles",
    u"CU-07: Estaciones del Sistema de Transporte",
    u"CU-08: Sitios de Comida",
    u"CU-09: Librer\xedas",
    u"CU-10: Datos sobre Robos",
    u"CU-11: Informaci\xf3n o Datos de la Localidad",
    u"CU-12: Centros de Atenci\xf3n Inmediata",
    u"CU-13: Veterinarias",
    u"CU-14: Barber\xedas"
]
modelio = Modelio.getInstance()
session = modelio.getModelingSession()
model = session.getModel()
from org.modelio.metamodel.uml.statik import Package, NameSpace

def util(x):  # solo un paquete que el usuario pueda modificar
    return isinstance(x, Package) and x.isModifiable()

def como_namespace(x):  # acepta un paquete o una lista de paquetes
    if util(x):
        return x
    try:
        for e in x:
            if util(e):
                return e
    except TypeError:
        pass
    return None

def raiz_del_modelo():
    for mod in ("org.modelio.metamodel.mda",
                "org.modelio.metamodel.uml.infrastructure"):
        try:
            clase = getattr(__import__(mod, fromlist=["Project"]), "Project")
            for proyecto in session.findByClass(clase):
                r = como_namespace(proyecto.getModel())
                if r is not None:
                    return r
        except Exception as e:
            print("Aviso (%s): %s" % (mod, e))
    for p in session.findByClass(Package):
        if not isinstance(p.getOwner(), Package) and util(p):
            return p
    return None

duenio = None
try:
    if len(selectedElements) > 0:
        duenio = como_namespace(selectedElements[0])
except NameError:
    pass
if duenio is None:
    duenio = raiz_del_modelo()
if duenio is None:
    raise Exception("Selecciona un paquete en el explorador y reintenta")
print("Paquete contenedor: %s (%s)" % (duenio.getName(), type(duenio).__name__))

tx = session.createTransaction("Casos de uso Vecino")
try:
    # Re-ejecutable: borra el paquete que dejo una ejecucion anterior.
    for viejo in list(duenio.getOwnedElement()):
        if viejo.getName() == SISTEMA:
            viejo.delete()
    paquete = model.createPackage(SISTEMA, duenio)
    actor = model.createActor(u"Vecino", paquete)
    casos = [model.createUseCase(nombre, paquete) for nombre in CASOS]
    enlaces = [model.createAssociation(actor, uc, u"") for uc in casos]
    diagrama = model.createUseCaseDiagram(u"Casos de uso", paquete, None)
    handle = modelio.getDiagramService().getDiagramHandle(diagrama)
    handle.unmask(actor, 100, 350)
    # Una columna en abanico: ninguna linea cruza un caso de uso.
    for i, uc in enumerate(casos):
        nodo = handle.unmask(uc, 520, 20 + i * 72).get(0)
        nodo.setSize(300, 58)
    for enlace in enlaces:
        try:
            handle.unmask(enlace, 0, 0)
        except Exception as e:
            print("Aviso al dibujar un enlace: %s" % e)
    handle.save()
    handle.close()
    tx.commit()
except:
    tx.rollback()
    raise
print("Listo: 1 actor, %d casos, %d asociaciones" % (len(casos), len(enlaces)))
# Muestra el diagrama en el explorador y lo abre en el editor.
modelio.getNavigationService().fireNavigate(diagrama)
modelio.getEditionService().openEditor(diagrama)
