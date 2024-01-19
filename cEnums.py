"""
Tools for extracting enums (and simple value defines)
from a c file
"""
import typing
from collections.abc import Mapping
from enum import Enum
import re

    
def globalize(thing:typing.Union[typing.Dict,Enum,typing.List])->None:
    """
    Break something apart into values and put it in the global namespace
    
    can globalize dict, enum, or object
    
    NOTE: this does not put thing itself in the global namespace
    """
    g=globals()
    if isinstance(thing,Enum):
        for x in thing: # type: ignore
            g[x.name]=x.value
    elif isinstance(thing,Mapping):
        for k,v in thing.items():
            g[k]=v
    else:
        for k,v in thing.__dict__.items():
            g[k]=v
        
def stripCComments(cCode:str)->str:
    """
    removes all comments from code to make it better to parse
    """
    result:typing.List[str]=[]
    for item in cCode.split('/*'):
        if not result:
            result=[item]
        else:
            cols=item.split('*/',1)
            if len(cols)>1:
                result.append(cols[-1])
    cCode=''.join(result)
    for item in cCode.split('//'):
        if not result:
            result=[item]
        else:
            cols=item.split('\n',1)
            if len(cols)>1:
                result.append('\n')
                result.append(cols[-1])
    return ''.join(result)
        
def loadCEnums(filename:str,globalizeAll:bool=False
    )->typing.Dict[typing.Optional[str],typing.Dict[str,typing.Union[str,int]]]:
    """
    Loads all enums from a c file.
    
    :globalizeAll: will add all enums and all of their values to the global namespace
    """
    enums:typing.Dict[typing.Optional[str],typing.Dict[str,typing.Union[str,int]]]={} # {enum_name:{k:v}} or for #defines {None:{k:v}}
    with open(filename,'r') as f:
        cCode=f.read()
    cCode=stripCComments(cCode)
    # grab all the #defines
    poundDefines:typing.Dict[str,typing.Union[str,int]]={}
    regexStr=r"""\n#define\s+(?P<name>[a-zA-Z_]+)\s*(?P<value>[0-9.]+)"""
    regex=re.compile(regexStr)
    for m in regex.finditer(cCode):
        name=m.group('name')
        value=int(m.group('value'))
        poundDefines[name]=value
    enums[None]=poundDefines
    # next grab all the enums
    typedefRegexStr=r"""\n\s*typedef\s+enum\s+(?P<name>[a-zA-Z_]+)\s+\{\s+(?P<values>[^}]+)\}\s*(?P<name2>[a-zA-Z_]+)"""
    typedefRegex=re.compile(typedefRegexStr,re.DOTALL)
    for m in typedefRegex.finditer(cCode):
        name=m.group('name')
        values=''.join(m.group('values').split()).split(',')
        mapping:typing.Dict[str,typing.Union[str,int]]={}
        currentVal=0
        for item in values:
            kv=item.split('=',1)
            k=kv[0]
            if not k:
                continue
            if len(kv)>1:
                v:typing.Union[str,int]=kv[1]
                if not kv[1].isdecimal():
                    if kv[1][0]=='-' and kv[1][1:].isdecimal():
                        v=int(kv[1])
                    elif v in mapping:
                        v=mapping[kv[1]]
                    else:
                        # find in all known enums
                        for e in enums.values():
                            if v in e:
                                v=e[kv[1]]
                                break
                else:
                    v=int(kv[1])
            else:
                v=currentVal
            if isinstance(v,int):
                currentVal=v+1
            else:
                print(f'WARN: possible error parsing {v}')
            mapping[k]=v
            enums[name]=mapping
    if globalizeAll:
        valDict:typing.Dict[str,typing.Any]
        for enumName,valDict in enums.items():
            if enumName is None:
                globalize(values)
            else:
                tmpEnum=Enum(enumName,valDict) # type: ignore
                globals()[enumName]=tmpEnum
                globalize(typing.cast(Enum,tmpEnum))
                # shouldn't have to do this, but here we are
                targetModule=__import__(__name__)
                for kk,vv in valDict.items():
                    setattr(targetModule,kk,vv)
    return enums