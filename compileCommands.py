"""
Tools for managing compile commands
"""
import typing
import os
from includes import headersAvailable


class CompileCommand:
    """
    breaks down a compile command to
    obtain useful information
    """
    def __init__(self,compileCommand:str,baseDir:typing.Optional[str]=None):
        """
        :baseDir: is necessary for deciphering relative paths
        """
        if baseDir is None:
            baseDir=os.getcwd()
        self.baseDir=os.path.abspath(os.path.expandvars(baseDir))
        self.compileCommand=compileCommand

    @property
    def includePaths(self)->typing.Generator[str,None,None]:
        """
        Yield up a list of include paths found in the command
        """
        for p in self.compileCommand.split(' -I')[1:]:
            p=p[2:]
            if p[0]=='"':
                p=p.split('"',2)[1]
            else:
                p=p.split(' ',1)[0]
            if os.sep!='/':
                p=p.replace('/',os.sep)
            p=os.path.expandvars(p)
            if p[0]!='/' and p[1]!=':':
                p=f'{self.baseDir}{os.sep}{p}'
            yield os.path.normpath(p)

    def compile(self,*args,**kwargs)->typing.Tuple[int,str]:
        """
        run the compile command

        any extra params will attempt to be
        added to the compile command, such as
            cc=CompileCommand("gcc")
            compile(self,"foo.c","bar.out",I="../includes")
            "gcc -I../Includes foo.c bar.out"
        (But it's generally better to include that stuff in the
        original compile command so you're sure to get it the
        way you want intend to!)

        returns (return_code,output)
        """
        import subprocess
        cmd=[self.compileCommand]
        if kwargs:
            for k,v in kwargs:
                k=str(k)
                if v is None:
                    v=''
                else:
                    v=str(v)
                if k.startswith('--'):
                    cmd.append(k)
                    cmd.append(v)
                elif k.startswith('-'):
                    cmd.append(k+v)
                elif len(k)==1:
                    cmd.append(f'-{k}{v}')
                else:
                    cmd.append(f'--{k}')
                    cmd.append(v)
        if args:
            cmd.extend([str(x) for x in args])
        po=subprocess.Popen(cmd,shell=True,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        out,_=po.communicate()
        ret=po.returncode
        out=out.strip().decode('utf-8',errors='ignore')
        return (ret,out)
    run=compile
    def __call__(self,*args,**argv)->typing.Tuple[int,str]:
        """
        run the compile command

        any extra params will attempt to be
        added to the compile command, such as
            cc=CompileCommand("gcc")
            compile(self,"foo.c","bar.out",I="../includes")
            "gcc -I../Includes foo.c bar.out"
        (But it's generally better to include that stuff in the
        original compile command so you're sure to get it the
        way you want intend to!)

        returns (return_code,output)
        """
        return self.compile(*args,**argv)

    @property
    def headersAvailable(self)->typing.Generator[str,None,None]:
        """
        yield all headers available in the include paths
        """
        yield from headersAvailable(self.baseDir)
