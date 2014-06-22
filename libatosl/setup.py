from distutils.core import setup, Extension
#/Users/zhujialai/Library/Developer/Xcode/DerivedData/libatosl-hidgoaqisgitjlcopwrelmrjiwzx/Build/Products/Release
module1 = Extension('atosl', 
                    sources = ['pyatosl.cpp',"common.cc","subprograms.cc","libatosl.cc","pySymboleFile.cpp","symbolFile.cpp"],
                    include_dirs=['/usr/local/Cellar/libdwarf/20130729/include/'],
                    libraries=['dwarf', 'bfd','iberty','opcodes'],
                    library_dirs=["."]) 
setup(name="PackageName atosl", version="1.0",description="This is Test",ext_modules=[module1])
