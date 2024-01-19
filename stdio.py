
"""
mimic stdio in a pythonic way

eg printf(r"I got %d problems, but \"%s\" aint one\n", 99, "print-effin")
"""
import typing
import regex as re


class PrinfIncorrectValues(Exception):
    """
    Exception to be raised when the values
    passed to printf() are incorrect
    """

class PrintfFormatPlaceholder:
    r"""
    as in "%02d"
    """

    PARAMETER_RE=r"""(?<parameter>[0-9]+[$])?"""
    FLAGS_RE=r"""(?<flags>[-+ 0'#])*"""
    WIDTH_RE=r"""(?<width>[0-9]+)?"""
    PRECISION_RE=r"""(?<precision>[.][0-9]+)?"""
    LENGTH_RE=r"""(?<length>hh|h|ll|l|L|z|j|t)?"""
    TYPE_RE=r"""(?<type>%|d|i|u|f|F|e|E|g|G|x|X|o|s|c|p|a|A|n)"""
    PARSER:typing.Pattern=re.compile(r'%'+PARAMETER_RE+
        FLAGS_RE+WIDTH_RE+PRECISION_RE+LENGTH_RE+TYPE_RE)

    def __init__(self,
        parameter:typing.Union[None,str,int]=None,
        flags:typing.Iterable[str]=[],
        width:typing.Union[None,str,int]=None,
        precision:typing.Union[None,str,int]=None,
        length:typing.Optional[str]=None,
        type:str=''):
        """ """
        self.parameter:typing.Optional[int]
        if parameter is None or isinstance(parameter,int):
            self.parameter=parameter
        else:
            self.parameter=int(parameter.split('$',1)[0])
        self.flags:typing.List[str]
        if flags is None:
            self.flags=[]
        else:
            self.flags=list(flags)
        self.width:typing.Optional[int]
        if width is None or isinstance(width,int):
            self.width=width
        else:
            self.width=int(width)
        self.precision:typing.Optional[int]
        if precision is None or isinstance(width,int):
            self.precision=precision
        else:
            self.precision=int(precision.rsplit('.',1)[-1])
        self.length:typing.Optional[str]=length
        self.type:str=type
        
    def __repr__(self):
        return '\n'.join(['---',
            f'parameter: {self.parameter}',
            f'flags: {self.flags}',
            f'width: {self.width}',
            f'precision: {self.precision}',
            f'length: {self.length}',
            f'type: {self.type}'])


class Printf:
    """
    Represents a c/c++ printf statement

    TODO: ultimately the goal is to work with things
    like c_integral_types to be able to interepret
    and generate c code at will
    """

    def __init__(self,fmt:str):
        self._fmt:str=fmt
        self._tape:typing.List[typing.Union[str,PrintfFormatPlaceholder]]=[]
        self._valuePlaceholders:typing.List[PrintfFormatPlaceholder]=[]
        self._fmtToTape()

    @property
    def fmt(self)->str:
        """
        get/set the format string
        """
        return self._fmt
    @fmt.setter
    def fmt(self,fmt:str):
        self._fmt=fmt
        self._fmtToTape()

    @property
    def numParameters(self)->int:
        """
        how many parameters are required for this printf format
        """
        return len(self._valuePlaceholders)
    
    @property
    def parameters(self)->typing.Iterable[PrintfFormatPlaceholder]:
        """
        info about all parameter placeholders
        """
        return self._valuePlaceholders    
    @property
    def placeholders(self)->typing.Iterable[PrintfFormatPlaceholder]:
        """
        info about all parameter placeholders
        """
        return self._valuePlaceholders

    def _fmtToTape(self):
        """
        turn the member printf format into an executable tape
        """
        self._tape=[]
        self._valuePlaceholders=[]
        p=0
        for m in PrintfFormatPlaceholder.PARSER.finditer(self._fmt):
            if m.start()>p:
                # text before the %, eg: "TEXT %d"
                txt=decodeCEscapeSequences(self._fmt[p:m.start()])
                self._tape.append(txt)
            # the % format decoded by the regex
            placeholder=PrintfFormatPlaceholder(**m.groupdict())
            self._tape.append(placeholder)
            self._valuePlaceholders.append(placeholder)
            p=m.end()
        if p<len(self._fmt):
            # trailing text at the end eg: "blah %d blah %d TEXT"
            txt=decodeCEscapeSequences(self._fmt[p:])
            self._tape.append(txt)

    def sprintf(self,*values)->str:
        """
        Get this printf string as applied to a set of value
        """
        ret=[]
        currentVal=0
        for step in self._tape:
            if isinstance(step,str):
                ret.append(step)
            else:
                if currentVal>=len(values):
                    raise PrinfIncorrectValues("Too few values for printf format")
                value=values[currentVal]
                currentVal+=1
                # TODO: use the actual parts of the % statement to determine how to print
                ret.append(str(value))
        if currentVal<len(values):
            raise PrinfIncorrectValues("Too many values for printf format")
        return ''.join(ret)

    def printf(self,*values):
        """
        Call this to printf a set of values to stdout

        NOTE: remember that unlike python print(), c printf()
            does not auto-add a newline
        """
        print(self.sprintf(*values),end='')
    __call__=printf

    def __repr__(self):
        return f'printf("{self._fmt}",...)'


def sprintf(fmt:str,*args)->str:
    """
    implement c/c++ sprintf for python

    NOTE: if you want to do a lot of printf's with
        the same format, you can gain speed by using
        the Printf class!
    """
    return Printf(fmt).sprintf(*args)


def printf(fmt:str,*args)->None:
    """
    implement c/c++ printf for python

    NOTE: remember that unlike python print(), c printf()
        does not auto-add a newline

    NOTE: if you want to do a lot of printf's with
        the same format, you can gain speed by using
        the Printf class!
    """
    return Printf(fmt)(*args)


def decodeCEscapeSequences(s:str)->str:
    r"""
    Decode backslashed values such as "\n"

    see also:
        https://en.wikipedia.org/wiki/Escape_sequences_in_C
    """
    ret=[]
    for bs in s.split('\\'):
        if ret:
            if bs[0]=='n':
                ret.append('\n')
                ret.append(bs[1:])
            elif bs[0]=='r':
                ret.append('\r')
                ret.append(bs[1:])
            elif bs[0]=='t':
                ret.append('\t')
                ret.append(bs[1:])
            elif bs[0]=='b':
                raise NotImplementedError(r'Dont know how to add backspace ("\b") to python string')
            elif bs[0]=='e':
                raise NotImplementedError(r'Dont know how to add escape ("\e") to python string')
            elif bs[0]=='f':
                raise NotImplementedError(r'Dont know how to add formfeed ("\f") to python string')
            elif bs[0]=='v':
                raise NotImplementedError(r'Dont know how to add vertical tab ("\v") to python string')
            elif bs[0]=='a':
                raise NotImplementedError(r'Dont know how to add alert/bell ("\a") to python string')
            elif bs[0] in '01234567':
                raise NotImplementedError(r'Dont know how to add octals to python string')
            elif bs[0]=='x':
                raise NotImplementedError(r'Dont know how to add hex char to python string')
            elif bs[0] in 'uU':
                raise NotImplementedError(r'Dont know how to add unicode char to python string')
            else:
                ret.append(bs)
        else:
            ret.append(bs)
    return ''.join(ret)


p=Printf(r"Got %d problems but %s aint one\n")
print(p.parameters)
#p(99,"pie")
