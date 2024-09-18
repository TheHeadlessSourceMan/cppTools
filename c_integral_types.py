"""
Defines primitive C integral number data types
"""
from enum import Enum
from math import ceil


class IntegralCTypeGoal(Enum):
    """
    The way the byte is to be determined
    """
    FAST=0 # fastest to process size that can handle this many bits
    LEAST=1 # smallest size that can handle this many bits
    EXACT=2 # like SMALLEST, only will fail if it's not exact


class IntegralCType:
    """
    A c type representing a integer number

    This can handle things like "unsigned short"
    or more explicit things like "uint16_t"
    """

    def __init__(self,
        numBits:int,
        signed:bool=True,
        goal:IntegralCTypeGoal=IntegralCTypeGoal.FAST,
        preferCanonical:bool=True,
        baseFormat:str="int",
        preferCaps:bool=True):
        """
        :preferCanonical: whether to prefer canonical
            like "short" or explicit like "int16_t"
        :baseFormat: how the type should generally be treated
            can be "int"(default),"hex","oct","bin"

        TODO: be able to create one of these from a string containing c code
            eg "unsigned int"
        """
        self.preferCanonical=preferCanonical
        self.signed=signed
        self.goal=goal
        self.numBits=numBits
        self.baseFormat=baseFormat
        self.preferCaps=preferCaps

    @property
    def fullNumBits(self)->int:
        """
        like numBits, but rounded up to a full byte,
        eg if numbits is 12, fullNumBits is 16
        (because it takes 2 bytes to house 12 bits)
        """
        return self.bytes*8

    @property
    def maxValue(self)->int:
        """
        the actual max value based on the number of bits
        """
        if self.signed:
            return pow(2,self.numBits)//2
        return pow(2,self.numBits)

    @property
    def minValue(self)->int:
        """
        the actual min value based on the number of bits
        """
        if self.signed:
            return pow(2,self.numBits)//2-1
        return 0

    @property
    def _printfLengthSpec(self)->str:
        nb=self.numBytes
        if nb==1:
            return 'hh'
        if nb==2:
            return 'h'
        if nb==4:
            return 'l'
        if nb==8:
            return 'll'
        raise Exception(f"No way to format {nb} bytes")

    @property
    def scanfString(self)->str:
        """
        get a string to be used in a scanf, eg
            scanf(buf,scanfString,&val);

        NOTE: scanf string and printf
            string may not always be the same
        """
        pLen=self._printfLengthSpec
        if self.baseFormat=='oct':
            return f'%{pLen}o'
        return f'%{pLen}i'

    @property
    def printfString(self)->str:
        """
        get a string to be used in a scanf, eg
            printf(scanfString,val);

        NOTE: scanf string and printf
            string may not always be the same
        """
        pLen=self._printfLengthSpec
        if self.baseFormat=='oct':
            return f'0%0{self.numBits<<2}{pLen}o'
        if self.baseFormat=='hex':
            if self.preferCaps:
                return f'0x%0{self.numBytes<<1}{pLen}X'
            return f'0x%0{self.numBytes<<1}{pLen}x'
        if self.baseFormat=='bin':
            return f'0b%0{self.numBits}{pLen}b'
        if self.signed:
            return f'%{pLen}d'
        return f'%{pLen}u'

    @property
    def cTypeName(self)->str:
        """
        The c type name
        """
        goal=''
        if self.goal==IntegralCTypeGoal.LEAST:
            goal='_least'
        elif self.goal==IntegralCTypeGoal.FAST:
            goal='_fast'
            if self.preferCanonical:
                # TODO: return the max type for eg CHAR not INT8_MAX
                raise NotImplementedError()
        if self.signed:
            prefix=''
        else:
            prefix='1'
        return f'{prefix}int{goal}{self.fullNumBits}'

    @property
    def cMinValueName(self)->str:
        """
        The c definition name for the minimum value
        """
        goal=''
        if self.goal==IntegralCTypeGoal.LEAST:
            goal='_LEAST'
        elif self.goal==IntegralCTypeGoal.FAST:
            goal='_FAST'
            if self.preferCanonical:
                # TODO: return the max type for eg CHAR not INT8_MAX
                raise NotImplementedError()
        if self.signed:
            prefix=''
        else:
            prefix='U'
        return f'{prefix}INT{goal}{self.fullNumBits}_MIN'

    @property
    def cMaxValueName(self)->str:
        """
        The c definition name for the maximum value
        """
        goal=''
        if self.goal==IntegralCTypeGoal.LEAST:
            goal='_LEAST'
        elif self.goal==IntegralCTypeGoal.FAST:
            goal='_FAST'
            if self.preferCanonical:
                # TODO: return the max type for eg CHAR not INT8_MAX
                raise NotImplementedError()
        if self.signed:
            prefix=''
        else:
            prefix='U'
        return f'{prefix}INT{goal}{self.fullNumBits}_MAX'

    @property
    def bytes(self)->int:
        """
        number of bytes required to contain this type
        """
        return ceil(self.numBits/8)
    @bytes.setter
    def bytes(self,b:int):
        self.numBits=b*8

    @property
    def numBytes(self)->int:
        """
        number of bytes required to contain this type
        """
        return ceil(self.numBits/8)
    @numBytes.setter
    def numBytes(self,b:int):
        self.numBits=b*8
