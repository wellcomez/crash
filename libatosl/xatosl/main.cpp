//
//  main.cpp
//  xatosl
//
//  Created by zhu jialai on 14/6/8.
//  Copyright (c) 2014年 Kingsoft. All rights reserved.
//

#include <iostream>
#include "../symbolFile.h"
void atosl(const char* image,unsigned long long base,unsigned long long address);
extern "C" char *
cplus_demangle (const char *mangled, int options);
int main(int argc, const char * argv[])
{

    // insert code here...
    atosl("/Users/zhujialai/Downloads/libatosl/ksmobilebrowser",0x1000,0x80000);
    atosl("/Users/zhujialai/Downloads/libatosl/ksmobilebrowser",0x1000,0x80000);
    atosl("/Users/zhujialai/Downloads/libatosl/ksmobilebrowser",0x1000,0x80000);
    std::cout << "Hello, World!\n";
    char* s=cplus_demangle("_ZN7WebCore4Page8goToItemEPNS_11HistoryItemENS_13FrameLoadTypeE", 0);
    symbolFile file;
    file.open("/Users/zhujialai/Downloads/libatosl/ksmobilebrowser");
    s=file.find(0x80000);
    s=file.find(0x80000);
    s=file.find(0x80000);
    file.close();
    return 0;
}

