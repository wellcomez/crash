//
//  symbolFile.h
//  libatosl
//
//  Created by zhu jialai on 14/6/8.
//  Copyright (c) 2014年 Kingsoft. All rights reserved.
//

#ifndef __libatosl__symbolFile__
#define __libatosl__symbolFile__

#include <iostream>
using namespace std;
#include <string>
class symbolFileImplement;
class symbolFile
{
public:
    symbolFile();
    bool open(const char* s);
    char* find(unsigned long long address);
    bool close();
    ~symbolFile();
protected:
    string name;
    symbolFileImplement* handle;
};
#endif /* defined(__libatosl__symbolFile__) */
