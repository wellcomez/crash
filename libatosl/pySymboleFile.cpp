// TestPython.cpp : 定义控制台应用程序的入口点。  
// author: 游蓝海  
// blog: http://blog.csdn.net/you_lan_hai  
#include <iostream>  
using namespace std;  
  
#include <Python.h>
#include <structmember.h>
#include "symbolFile.h" 
//有多个参数的python导出函数  
static PyObject* py_test(PyObject* self, PyObject * args)  
{  
    cout<<"this message comes from C++"<<endl;  
  
    Py_IncRef(Py_None);  
    return Py_None;  
}  
  
//方法定义  
static PyMethodDef lazyMethods[] =  
{  
    {"test", PyCFunction(py_test), METH_VARARGS, "just for test"},  
    {NULL, NULL, NULL, NULL}, //结束标志  
};  
  
//python导出类  
class atolsWrapPyClass : public PyObject  
{  
protected:
    symbolFile* file;
public:  
    atolsWrapPyClass(PyTypeObject * pType)  
        : id_(0)  
        , score_(99) 
	, file(NULL)
    {  
        if(PyType_Ready(pType) < 0)    
        {  
            cout<<"PyType_Ready faild."<<endl;  
        }
	file=new symbolFile();	
        PyObject_INIT(this, pType);  
    }  
    virtual ~atolsWrapPyClass()  
    {  
  	if(file)
	{
	   file->close();
	}
    }  
  
    static PyObject* py_new(PyTypeObject * pType, PyObject *, PyObject *)  
    {  
        return new atolsWrapPyClass(pType);  
    }  
  
    static void py_dealloc(PyObject * self)  
    {  
        delete (atolsWrapPyClass*)self;  
    }  
  
    //init方法。  
    static int py_init(PyObject * self, PyObject * args, PyObject *)  
    {  
        atolsWrapPyClass* pThis = (atolsWrapPyClass*)self;  
        if(!PyArg_ParseTuple(args, "ii", &pThis->id_, &pThis->score_))  
        {  
            return 0;  
        }  
        return 1;  
    }  
    static PyObject* _py_close(PyObject* self, PyObject * args)  
    {  
        return ((atolsWrapPyClass*)self)->py_close(args);  
    }
    PyObject* py_close(PyObject * args)
    {
	if(this->file)
	{
	   this->file->close();
	}
	return NULL;	
    } 
    static PyObject* _py_open(PyObject* self, PyObject * args)  
    {  
        return ((atolsWrapPyClass*)self)->py_open(args);  
    }
    PyObject* py_open(PyObject * args)
    {
	char* s;
	if (! PyArg_ParseTuple(args, "s",&s))
		return Py_BuildValue("i", 0);
	int i=this->file->open(s);
	return Py_BuildValue("i", i);
    }
    static PyObject* _py_find(PyObject* self, PyObject * args)  
    {  
        return ((atolsWrapPyClass*)self)->py_find(args);  
    }  
  
    PyObject* py_find(PyObject * args)
    {
	int s;
	if (! PyArg_ParseTuple(args, "i",&s))
	{
        	Py_IncRef(Py_None);  
	        return Py_None;  
	}
	char* ret=this->file->find(s);	
	return Py_BuildValue("s",ret);
    }  
    PyObject* py_test(PyObject * args)  
    {  
        cout<<"this message comes from atolsWrapPyClass."<<endl;  
        Py_IncRef(Py_None);  
        return Py_None;  
    }  
  
    static PyObject* _py_test(PyObject* self, PyObject * args)  
    {  
        return ((atolsWrapPyClass*)self)->py_test(args);  
    }  
  
    int id_;  
    int score_;  
};  
  
/*如果类中有虚函数，则类对象开始地址为一个虚函数表的地址。 
由于PyObject没有虚函数，而子类有虚函数，则子类与基类不共起始地址。 
*/  
#define offsetofVirtual(type, member) ( (unsigned long) & ((type*)0) -> member - sizeof(void*))  
  
//成员变量  
static PyMemberDef atoslWrapClassMembers[] =  
{  
    {"id", T_INT, offsetofVirtual(atolsWrapPyClass, id_), 0, "id"},  
    {"score", T_INT, offsetofVirtual(atolsWrapPyClass, score_), 0, "score"},  
    {NULL, NULL, NULL, 0, NULL},  
};  
  
//成员函数  
static PyMethodDef atolsWrapClassMethods[] =  
{  
    {"test", PyCFunction(atolsWrapPyClass::_py_test), METH_VARARGS, "just for test"},  
    {"open", PyCFunction(atolsWrapPyClass::_py_open), METH_VARARGS, "just for test"},  
    {"close", PyCFunction(atolsWrapPyClass::_py_close), METH_VARARGS, "just for test"},  
    {"find", PyCFunction(atolsWrapPyClass::_py_find), METH_VARARGS, "just for test"},  
    {NULL, NULL, NULL, NULL},  
};  
PyMethodDef pyTest()
{
    return {"test", PyCFunction(atolsWrapPyClass::_py_test), METH_VARARGS, "just for test"};
}

//类类型  
static PyTypeObject atolsWrapPyClass_Type = {  
    PyVarObject_HEAD_INIT(&PyType_Type, 0)  
    "atolsWrapPyClass",  
    sizeof(atolsWrapPyClass),  
    0,  
    (destructor)atolsWrapPyClass::py_dealloc,        /* tp_dealloc */  
    0,                                          /* tp_print */  
    0,                                          /* tp_getattr */  
    0,                                          /* tp_setattr */  
    0,                                          /* tp_compare */  
    0,                                          /* tp_repr */  
    0,                                          /* tp_as_number */  
    0,                                          /* tp_as_sequence */  
    0,                                          /* tp_as_mapping */  
    0,                                          /* tp_hash */  
    0,                                          /* tp_call */  
    0,                                          /* tp_str */  
    0,                                          /* tp_getattro */  
    0,                                          /* tp_setattro */  
    0,                                          /* tp_as_buffer */  
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE ,  /* tp_flags */  
    0,                                          /* tp_doc */  
    0,                                          /* tp_traverse */  
    0,                                          /* tp_clear */  
    0,                                          /* tp_richcompare */  
    0,                                          /* tp_weaklistoffset */  
    0,                                          /* tp_iter */  
    0,                                          /* tp_iternext */  
    atolsWrapClassMethods,                           /* tp_methods */  
    atoslWrapClassMembers,                           /* tp_members */  
    0,                                          /* tp_getset */  
    0,                                          /* tp_base */  
    0,                                          /* tp_dict */  
    0,                                          /* tp_descr_get */  
    0,                                          /* tp_descr_set */  
    0,                                          /* tp_dictoffset */  
    (initproc)atolsWrapPyClass::py_init,             /* tp_init */  
    0,                                          /* tp_alloc */  
    (newfunc)atolsWrapPyClass::py_new,               /* tp_new */  
    0,                                          /* tp_free */  
}; 
void pyTestAddClass(PyObject* pModule)
{
	Py_IncRef((PyObject*)&atolsWrapPyClass_Type);  
	PyModule_AddObject(pModule, "atosl", (PyObject*)&atolsWrapPyClass_Type);
}
