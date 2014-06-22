#include <Python.h>;
static PyObject* add(PyObject *self, PyObject *args); 

//一定声明为static，把他们限制在这个文件范围里。 几乎所有的参数都是PyObject类型。 在python，每个东西都是object。 



static PyObject* add(PyObject* self, PyObject* args) 
{ 

   int x=0 ; 

   int y=0;

   int z=0;

	if (! PyArg_ParseTuple(args, "i|i", &x, &y))

		return NULL;
	z=x+y;

	return Py_BuildValue("i", z);
}
extern char* atosl(const char* image,unsigned long long base,unsigned long long address);
extern "C" char * cplus_demangle (const char *mangled, int options);
static PyObject* address(PyObject* self, PyObject* args)
{
    
    int x=0 ;
    
    int y=0;
    
    int z=0;
    const char* s;
	if (! PyArg_ParseTuple(args, "s|i|i",&s,&x, &y))
        
		return NULL;
    printf("SymbolPath \"%s\" Base[0x%x] Address[0x%x]\n",s,x,y);
    s=atosl(s,x,y);
    return Py_BuildValue("s", s);
    
    /*调用完之后我们需要返回结果。这个结果是c的type或者是我们自己定义的类型。必须把他转换成PyObject， 让python认识。这个用Py_BuildValue
     
     来完成。他是PyArg_ParseTuple的逆过程。他的第一个参数和PyArg_ParseTuple的第二个参数一样， 是个格式化符号。第三个参数
     
     是我们需要转换的参数。Py_BuildValue会把所有的返回只组装成一个tutple给python。*/
    
}
static PyObject* cxxfilt(PyObject* self, PyObject* args)
{
    const char* s;
    int opt;
	if (! PyArg_ParseTuple(args, "s|i",&s,&opt))
        
		return NULL;
    char* r=cplus_demangle(s,opt);
    PyObject* ret=Py_BuildValue("s", r);
    return ret;
    
    /*调用完之后我们需要返回结果。这个结果是c的type或者是我们自己定义的类型。必须把他转换成PyObject， 让python认识。这个用Py_BuildValue
     
     来完成。他是PyArg_ParseTuple的逆过程。他的第一个参数和PyArg_ParseTuple的第二个参数一样， 是个格式化符号。第三个参数
     
     是我们需要转换的参数。Py_BuildValue会把所有的返回只组装成一个tutple给python。*/
    
}

PyMethodDef pyTest();
void pyTestAddClass(PyObject* pModule);
static PyMethodDef addMethods[] =
{ 

   {"address",  address, METH_VARARGS, "atols"},
   {"cxxfilt",  cxxfilt, METH_VARARGS, "cxxfilt"},
   pyTest(),
   {NULL, NULL, 0, NULL}
};

/*这个是一个c的结构。他来完成一个映射。 我们需要把我们扩展的函数都映射到这个表里。表的第一个字段是python真正认识的。是python 

里的方法名字。 第二个字段是python里的这个方法名字的具体实现的函数名。 在python里调用add， 真正执行的是用c写的add函数。

第三个字段是METH_VARARGS， 他告诉python，add是调用c函数来实现的。第四个字段是这个函数的说明。如果你在python里来help这个函数，

将显示这个说明。相当于在python里的函数的文档说明。*/


PyMODINIT_FUNC initatosl() 
{ 
     PyObject* pModule;
     if(pModule=Py_InitModule("atosl", addMethods))
     {
	 pyTestAddClass(pModule);

     }
} 
