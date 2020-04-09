#include <Python.h>
#include <stdlib.h>
#include <stdbool.h>

const int MAX_NUMER_OF_VERTICES = 16;

PyObject* TooManyVerticesError;
PyObject* NoVerticesError;
PyObject* G6Error;

typedef struct Node Node;
struct Node{
    int val;
    Node* next;
};

typedef struct {
    PyObject_HEAD
    size_t numberOfVertices;
    Node** nodes;
} AdjacencyList;


PyObject* None() {
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject* True() {
    PyObject* r = Py_True;
    Py_INCREF(r);
    return r;
}

PyObject* False() {
    PyObject* r = Py_False;
    Py_INCREF(r);
    return r;
}

// Here we assume that there is no such edge in graph
AdjacencyList* addEdge(AdjacencyList* list, int u, int v) {
    if(list == NULL || list->nodes == NULL) {
        return list;
    } 

    Node* newVertexForU = (Node*)malloc(sizeof(Node));
    Node* newVertexForV = (Node*)malloc(sizeof(Node));
    newVertexForU->val = v;
    newVertexForV->val = u;
        
    Node* uNext = list->nodes[u];
    Node* vNext = list->nodes[v];

    newVertexForU->next = uNext;
    newVertexForV->next = vNext;

    list->nodes[u] = newVertexForU;
    list->nodes[v] = newVertexForV;
    return list;
}

AdjacencyList* deleteEdgeFromVertex(AdjacencyList* list, int from, int withValue) {
    if(list == NULL || list->nodes == NULL) {
        return list;
    }
    if(list->nodes[from] == NULL) {
        return list;
    }

    Node* tmp = list->nodes[from];
    if(tmp != NULL && tmp->val == withValue) {
        list->nodes[from] = tmp->next;
        free(tmp);
    } else {
        while(tmp != NULL) {
            if(tmp->next != NULL && tmp->next->val == withValue) {
                Node* tmp2 = tmp->next;
                tmp->next = tmp->next->next;
                free(tmp2);
                // We can break since it is a simple graph - so no multi edges
                break;
            }
            tmp = tmp->next;
        }
    }
    return list;
}

// Here we assume that there is such edge in graph
AdjacencyList* deleteEdge(AdjacencyList* list, int u, int v) {
    if(list == NULL || list->nodes == NULL) {
        return list;
    }
    // Delete edge u - v
    list = deleteEdgeFromVertex(list, u, v);

    // Delete edge v - u
    list = deleteEdgeFromVertex(list, v, u);

    return list;
}

bool isEdge(AdjacencyList* list, int u, int v) {
    int max = u > v ? u : v;
    if(max >= MAX_NUMER_OF_VERTICES || max >= list->numberOfVertices) {
        return false;
    }

    Node* tmp = list->nodes[u];
    while(tmp != NULL) {
        if(tmp->val == v) {
            return true;
        }
        tmp = tmp->next;
    }

    return false;
}

AdjacencyList* removeVertex(AdjacencyList* list, int v) {
    if(list == NULL || list->nodes == NULL) {
        return list;
    }
    if(v >= MAX_NUMER_OF_VERTICES) {
        return list;
    }

    for(size_t i = 0; i < list->numberOfVertices; i++) {
        list = deleteEdgeFromVertex(list, i, v);
    }
    for(size_t i = 0; i < list->numberOfVertices; i++) {
        // Decrease by one its vertex number that is larger that v 
        Node* tmp = list->nodes[i];
        while(tmp != NULL) {
            if((tmp->val) > v) {
                tmp->val = (tmp->val) - 1;
            }
            tmp = tmp->next;
        }
    }
    
    free(list->nodes[v]);
    
    for(size_t i = v; i < list->numberOfVertices - 1; i++) {
        list->nodes[i] = list->nodes[i + 1];
    }
    
    
    list->numberOfVertices--;
    return list;
}

AdjacencyList* addVertex(AdjacencyList* list) {
    if(list == NULL || list->nodes == NULL) {
        return list;
    }
    // New vertex without edges
    size_t newIndex = list->numberOfVertices;
    list->nodes[newIndex] = NULL;
    
    list->numberOfVertices = list->numberOfVertices + 1;
    return list;
}

AdjacencyList* allocateNewList(AdjacencyList* list) {
    list->nodes = (Node**)malloc(MAX_NUMER_OF_VERTICES * sizeof(Node*)); 
    for(int i = 0; i < MAX_NUMER_OF_VERTICES; i++) {
        list->nodes[i] = NULL;
    }
}

void dealocateSingleList(Node* list) {
    if(list == NULL)
        return;
    dealocateSingleList(list->next);
    free(list);
}

AdjacencyList* deallocateList(AdjacencyList* list) {
    for(int i = 0; i < list->numberOfVertices; i++) {
        dealocateSingleList(list->nodes[i]);
    }
    free(list->nodes);
}

PyObject* readListFromString(AdjacencyList* list, char* text) {
    if(text[0] == '\0') {
        PyErr_SetString(G6Error, "too short text");
        return NULL;
    }
    size_t c = ((size_t)text[0]) - 63;

    if(c < 1 || c > 16) {
        PyErr_Format(G6Error, "wrong order %d", c);
        return NULL;
    }

    for(size_t i = 0; i < c; i++) {
        list = addVertex(list);
    }

    int iter = 1;
    int k = 0;

    for(int v = 1; v < list->numberOfVertices; v++) {
        for(int u = 0; u < v; u++) {
            if(k == 0) {
                if(text[iter] == '\0') {
                    PyErr_SetString(G6Error, "too short text");
                    return NULL;
                }
                c = ((int)text[iter]) - 63;
                iter++;
                if(c < 0 || c > 63) {
                    PyErr_Format(G6Error, "wrong character: %c", c + 63);
                    return NULL;
                }
                k = 6;
            }
            k--;
            if((c & (1 << k)) != 0) {
                if(!isEdge(list, u, v)) {
                    addEdge(list, u, v);
                }
            }
            
        }
    }
    
    if(text[iter] != '\0') {
        PyErr_SetString(G6Error, "too long text");
        return NULL;
    }
    
    return None(); 
}

void convertListToString(AdjacencyList* list, char* text) {
    text[0] = (char)((list->numberOfVertices) + 63);
    int k = 5;
    int c = 0;
    int iter = 1;
    
    for(int v = 1; v < list->numberOfVertices; v++) {
        for(int u = 0; u < v; u++) {
            if(isEdge(list, u, v)) {
                c |= (1 << k);
            }
            if(k == 0) {
                text[iter] = (char)(c + 63);
                iter++;
                k = 6;
                c = 0;
            }
            k--;
        }
    }
    
    if(k != 5) {
        text[iter] = (char)(c + 63);
        iter++;
    }
    
    text[iter] = '\0';
}

static PyObject *AdjacencyList__new__(PyTypeObject *type, PyObject *args ) {
    return type->tp_alloc( type, 0 );
}

static void AdjacencyList__del__( AdjacencyList *self ) {
    deallocateList(self);
    Py_TYPE( self )->tp_free( (PyObject *)self );
}

static int AdjacencyList__init__(AdjacencyList *self,  PyObject *args, PyObject *kwds ) {
     char* text=NULL;

    static char *kwlist[] = {"text", NULL};

    if (PyArg_ParseTupleAndKeywords(args, kwds, "|z", kwlist, &text)) {
        if(!text) {
            //set default value
            text = "@";
        }
        // Allocate nodes array
        self = allocateNewList(self);
        PyObject* result = readListFromString(self, text);
        return result == NULL ? -1 : 0;
    }
 
    return -1;
}

static PyObject *AdjacencyListOrder( AdjacencyList *self ) {
    return Py_BuildValue("i", self->numberOfVertices );
}

static PyObject *AdjacencyListAddVertex( AdjacencyList *self ) {
    if(self->numberOfVertices == MAX_NUMER_OF_VERTICES) {
        PyErr_SetString(TooManyVerticesError, "too many vertices");
        return NULL;
    } else {
        self = addVertex(self);
        return None();
    }
    return None();
}

static PyObject *AdjacencyListDeleteVertex( AdjacencyList *self, PyObject *args ) {
    if(self->numberOfVertices == 1) {
        PyErr_SetString(NoVerticesError, "graph must have vertices");
        return NULL;
    }
    int vertex;
    if (PyArg_ParseTuple( args, "i", &vertex)) {
        if(vertex < MAX_NUMER_OF_VERTICES && vertex >= 0 && self->numberOfVertices > 1) {
            self = removeVertex(self, vertex);
        }
        return None();
    }
    return None();
}

static PyObject *AdjacencyListIsEdge( AdjacencyList *self, PyObject *args ) {
    int u, v;
    if (PyArg_ParseTuple( args, "ii", &u, &v)) {
        bool isEdgeThere = isEdge(self, u, v);
        return  isEdgeThere ? True() : False();
    }
    return False();
}

static PyObject *AdjacencyListAddEdge( AdjacencyList *self, PyObject *args ) {
    int u, v;
    if (PyArg_ParseTuple( args, "ii", &u, &v)) {
        int max = u > v ? u : v;
        if(max > self->numberOfVertices || isEdge(self, u, v)) {
            return None();
        }
        self = addEdge(self, u, v);
        return None();
    }
    return None();
}

static PyObject *AdjacencyListDeleteEdge( AdjacencyList *self, PyObject *args ) {
    int u, v;
    if (PyArg_ParseTuple( args, "ii", &u, &v)) {
        int max = u > v ? u : v;
        if(max > self->numberOfVertices || !isEdge(self, u, v)) {
            return None();
        }
        deleteEdge(self, u, v);
        return None();
    }
    return None();
}

static PyObject *AdjacencyListFromString( AdjacencyList *self, PyObject *args ) {
    char* text;
    if (PyArg_ParseTuple( args, "s", &text)) {
        deallocateList(self);
        self = allocateNewList(self);
        return readListFromString(self, text);
    }
    return None();
}

static PyObject* AdjacencyList__str__( AdjacencyList *self ) {
    char* result = (char*)malloc(20 * sizeof(char));
    convertListToString(self, result);
    PyObject* r = Py_BuildValue("s", result);

    free(result);
    return r;
}

static PyObject *
AdjacencyList_richcmp(PyObject *obj1, PyObject *obj2, int op)
{
    PyObject *result;
    int c;

    AdjacencyList* m = (AdjacencyList*)obj1;
    AdjacencyList* n = (AdjacencyList*)obj2;

    bool areEqual = true;
    if(m->numberOfVertices != n->numberOfVertices) {
        areEqual = false;
    } else {
        for(int i = 1; i < m->numberOfVertices; i++) {
            for(int j = 0; j < i; j++) {
                if(isEdge(m, j, i) != isEdge(n, j, i)) {
                    areEqual = false;
                    break;
                }
            }
        }
    }

    switch (op) {
        case Py_LT: return Py_NotImplemented; break;
        case Py_LE: return Py_NotImplemented; break;
        case Py_EQ: c = areEqual; break;
        case Py_NE: c = !areEqual; break;
        case Py_GT: return Py_NotImplemented; break;
        case Py_GE: return Py_NotImplemented; break;
    }
    result = c ? Py_True : Py_False;
    Py_INCREF(result);
    return result;
 }

static PyMethodDef AdjacencyListMethods[] = {
    { "order", (PyCFunction)AdjacencyListOrder, METH_NOARGS,
        "Return amount of vertices." },
    { "addVertex", (PyCFunction)AdjacencyListAddVertex, METH_NOARGS,
        "Add new isolated vertex." },
    { "deleteVertex", (PyCFunction)AdjacencyListDeleteVertex, METH_VARARGS,
        "Delete selected vertex." },
    { "isEdge", (PyCFunction)AdjacencyListIsEdge, METH_VARARGS,
        "Return if given vertices are neighbours." },
    { "addEdge", (PyCFunction)AdjacencyListAddEdge, METH_VARARGS,
        "Add given edge." },
    { "deleteEdge", (PyCFunction)AdjacencyListDeleteEdge, METH_VARARGS,
        "Delete given edge." },
    { "fromString", (PyCFunction)AdjacencyListFromString, METH_VARARGS,
        "Convert string to a graph representation." },
    { NULL }
} ;

static  PyTypeObject AdjacencyListType = {
    PyVarObject_HEAD_INIT( NULL,0 ) // inicjalizacja
    "simple_graphs.AdjacencyList", // nazwa
    sizeof( AdjacencyList ), // rozmiar
    0, //
    (destructor)AdjacencyList__del__, // destruktor
    0,0,0,0,0,0,0,0,0,0, //
    (reprfunc)AdjacencyList__str__, // obiekt->napis
    0,0,0, //
    Py_TPFLAGS_DEFAULT, //
    "adjacency list graph representation.", // opis
    0,0,
    (richcmpfunc)&AdjacencyList_richcmp,
    0,0,0, //
    AdjacencyListMethods, // metody
    0,0,0,0,0,0,0, //
    (initproc)AdjacencyList__init__, // inicjalizator
    0, //
    (newfunc)AdjacencyList__new__ // konstruktor
} ;

static PyModuleDef simple_graphs_module = {
    PyModuleDef_HEAD_INIT,
    "simple_graphs",
    "Implementation of Adjacency List representation of a graph in C",
    -1,
    NULL, NULL, NULL, NULL, NULL
} ;

PyMODINIT_FUNC PyInit_simple_graphs( void ) {
    if (PyType_Ready( &AdjacencyListType ) < 0) return NULL;

    PyObject* m = PyModule_Create( &simple_graphs_module );
    if (m == NULL) return NULL;

    TooManyVerticesError = PyErr_NewException("simple_graphs.TooManyVerticesError", NULL, NULL);
    PyDict_SetItemString(AdjacencyListType.tp_dict, "TooManyVerticesError", TooManyVerticesError);

    NoVerticesError = PyErr_NewException("simple_graphs.NoVerticesError", NULL, NULL);
    PyDict_SetItemString(AdjacencyListType.tp_dict, "NoVerticesError", NoVerticesError);

    G6Error = PyErr_NewException("simple_graphs.G6Error", NULL, NULL);
    PyDict_SetItemString(AdjacencyListType.tp_dict, "G6Error", G6Error);

    Py_INCREF( &AdjacencyListType );
    PyModule_AddObject( m, "AdjacencyList",
    (PyObject *)&AdjacencyListType );

    return m;
}