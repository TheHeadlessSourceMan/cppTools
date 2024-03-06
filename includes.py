"""
Tools for searching for #include headers

Can do helpful things like:
    cc=CompileCommand("gcc -I../include foo.cpp","./")
    print(headersAvailable(cc))
"""
import typing
import os


class HeaderNotFoundException(Exception):
    """
    Exception for when a c/c++ header cannot be found
    eg, with findHeaderFromCompileCommand()
    """
    def __init__(self,
        header:str,
        includeDirs:typing.Iterable[str],
        suggestions:typing.Optional[typing.Iterable[str]]=None):
        """ """
        # builds the exception message based upon includeDirs
        # and suggestions if avilable
        msg=[f'header "{header}" not found']
        includeDirs=[f'"{x}"' for x in list(includeDirs)]
        if includeDirs:
            msg.append(' in:\n  '+(', '.join(includeDirs)))
        if suggestions is not None:
            suggestions=[f'"{x}"' for x in list(suggestions)]
            if suggestions:
                msg.append('\nSuggestions:\n  '+(', '.join(suggestions)))
        Exception.__init__(self,''.join(msg))


class HasIncludePaths(typing.Protocol):
    """anything that has an includePaths member"""
    includePaths:typing.Iterable[str]
IncludePathsCompatible=typing.Union[str,typing.Iterable[str],HasIncludePaths]
def asIncludePaths(inc=IncludePathsCompatible)->typing.Iterable[str]:
    """
    take any IncludePathsCompatible and return an iterable of include paths
    """
    if isinstance(inc,str):
        inc=(inc,)
    elif hasattr(inc,"includePaths"):
        inc=inc.includePaths
    return inc


def headersAvailable(
    paths:IncludePathsCompatible,
    fullFilename:bool=True
    )->typing.Generator[str,None,None]:
    """
    list all known header files available in a set of paths
    """
    for p in asIncludePaths(paths):
        if not os.path.exists(p):
            print(f'Include path: "{p}" not found.')
            continue
        for f in os.listdir(p):
            ext=f.rsplit('.',1)[-1].lower()
            if ext in ('h','hpp','h++','hxx'):
                if fullFilename:
                    yield f'{p}{os.sep}{f}'
                else:
                    yield f

def findHeadersLike(
    headerToFind:str,
    paths:IncludePathsCompatible,
    baseDir:typing.Optional[str]=None,
    fullFilename:bool=True
    )->typing.Generator[str,None,None]:
    """
    using a compile string's include paths,
    find where a given header resides.

    yeilds all headers like a given header name
    """
    headerSimple=headerToFind.split('.',1)[0].lower()
    for h in headersAvailable(paths,baseDir):
        hSimple=headerToFind.split('.',1)[0].lower()
        if hSimple.find(headerSimple):
            if fullFilename:
                yield h
            else:
                yield h.rsplit(os.sep,1)[-1]

def findHeader(
    headerToFind:str,
    paths:IncludePathsCompatible,
    baseDir:typing.Optional[str]=None
    )->str:
    """
    Find where in a set of paths a given header resides.

    Always returns only the first one found
    (aka, the one the compiler would use)

    If not found, raises HeaderNotFoundException
    """
    for h in headersAvailable(paths,baseDir):
        hShort=h.rsplit(os.sep,1)[-1]
        if hShort==headerToFind:
            return h
    suggestions=findHeadersLike(headerToFind,paths)
    raise HeaderNotFoundException(headerToFind,paths,suggestions)
