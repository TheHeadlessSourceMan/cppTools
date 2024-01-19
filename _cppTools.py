
import typing
import regex as re
from paths import FileLocation
from paths.urlTyping import UrlCompatible, asURL


_multiLineCommentRe=r"""(?:/[*](?P<multiLineComment>.*?)[*]/)"""
_singleLineCommentRe=r"""(?://(?P<singleLineComment>[^\r\n]*))"""
_bothCommentsRe=re.compile(f'(?P<code>.*?)(?:{_multiLineCommentRe}|{_singleLineCommentRe}|$)',re.DOTALL)
def cppSeparateComments(code:str)->typing.Generator[str,None,None]:
    """
    yields [code,comment,code,comment,...]
    """
    for m in _bothCommentsRe.finditer(code):
        yield m.group('code')
        comment=m.group('multiLineComment')
        if comment is None:
            comment=m.group('singleLineComment')
        if comment is not None:
            yield comment
def cppRemoveComments(code:str)->str:
    """
    Removes all comments from a block of code
    (usually used to make parsing easier)
    """
    ret=[]
    for i,txt in enumerate(cppSeparateComments(code)):
        if i%2==0:
            ret.append(txt)
    return ''.join(ret)

def cppValue2PyValue(code:str)->str:
    """
    Attempt to convert the value of a cpp variable (eg, as found in a debugger)
    into a first-class python value.
    """
    v=code.strip()
    if v[0] in ('\'','"'):
        vv:typing.Any=v[1:-1]
    else:
        vv=v.lower()
        if vv=='null':
            vv=None
        elif vv=='true':
            vv=True
        elif vv=='false':
            vv=False
        elif vv.startswith('0x'):
            raise NotImplementedError('hex')
        elif vv.startswith('0'):
            raise NotImplementedError('octal')
        elif vv.isnumeric():
            vv=int(vv)
        else:
            if vv.endswith('f'):
                vv=v[0:-1]
            try:
                vv=float(vv)
            except ValueError:
                raise ValueError(f'Unknown python data type for "{v}"')
    return vv
    
_varnameRe=re.compile(r"""(?P<name>[A-Za-z_][A-Za-z0-9_]*)""")
def cppIsLeagalVarName(varname:str)->bool:
    """
    Check to see if a variable name is legal
    """
    return _varnameRe.match(varname)!=None
def cppMakeLegalVarName(varname:str)->str:
    """
    Make a variable name legal
    """
    varname=''.join([(c if c.isalpha() or c.isdigit() else '_') for c in varname.strip()])
    if not varname:
        varname='_'
    else:
        # can't start with a number
        if varname[0].isdigit():
            varname='number'+varname
    # obscure c rule that #defines beginning with _ are reserved
    if varname[0]=='_' and varname==varname.upper():
        varname='X'+varname
    return varname

_declRe=r"""(?:(?P<type>[a-z_]+(\s*[*]+)?)?\s*"""+_varnameRe.pattern+')'
_paramRe='(?P<param>'+_declRe+r"""(?:\s*=\s*(?P<default>[^\s\n$]))?)"""
_paramsListRe=re.compile(f"(?:^\s*|\s*,\s*){_paramRe}",re.DOTALL)
_funcParseReStr=_declRe+r"?\s*[(]\s*(?P<params>[^)]*)\s*[)]"
_funcParseRe=re.compile(_funcParseReStr,re.DOTALL)
def cppFunctionInfo(functionDefinition:str
    )->typing.Tuple[str,str,typing.Dict[str,typing.Union[typing.Tuple[str,typing.Any],typing.Tuple[str]]]]:
    """
    given a funcion header like
        "void myfunc(int a,float b=10)"
        returns
        {"a":("int"),"b":("float",10)}
    returns (returnType,name,parameters{name:(datatype,default)})
    """
    returnType=''
    name=''
    parameters:typing.Dict[str,typing.Union[typing.Tuple[str,typing.Any],typing.Tuple[str]]]={}
    m=_funcParseRe.search(cppRemoveComments(functionDefinition))
    if m.group('type') is not None:
        returnType=m.group('type')
    if m.group('name') is not None:
        name=m.group('name')
    if m.group('params') is not None:
        for mm in _paramsListRe.finditer(m.group('params')):
            if mm.group('default') is None:
                parameters[mm.group('name')]=(mm.group('type'),)
            else:
                val=cppValue2PyValue(mm.group('default'))
                parameters[mm.group('name')]=(mm.group('type'),val)
    return (returnType,name,parameters)
def cppFunctionParameters(functionDefinition:str
    )->typing.Dict[str,typing.Union[typing.Tuple[str,typing.Any],typing.Tuple[str]]]:
    return cppFunctionInfo(functionDefinition)[2]

class CppScope:
    """
    Variable scope for cpp code
    """
    def __init__(self,location:FileLocation,contexts:'CppScopes',parent:typing.Optional['CppScope']):
        self.contexts=contexts
        self.parent=parent
        self.location=location
        self.chilren:typing.List['CppScope']=[]
        
    @property
    def root(self)->'CppScope':
        return self.contexts


class CppScopes(CppScope):
    """
    Does not cover single-line scopes like
        if(x)
            theny();
    This is generally not a problem because there is little time to do anything context-ey.
    """

    def __init__(self,code:str,path:UrlCompatible):
        location=FileLocation(path)
        CppScope.__init__(self,location,self,None)
        self.assign(code,path)

    def assign(self,code:str,path:UrlCompatible):
        path=asURL(path)
        code=cppRemoveComments(code)
        linearpos=0
        for ctx in code.split('{'):
            start=FileLocation(path,)
            linearpos+=len(ctx)+1
            raise NotImplementedError()


def cppFileLocationToFunctionDefinition(location:str)->typing.Optional[str]:
    """
    TODO:
    """
    return None
fileLocationToFunctionDefinition=cppFileLocationToFunctionDefinition