#!/bin/python

REQUIREMENTS = []
def CheckLibDependency():
    try:
        #check dependencies
        import socket
    except:
        import os, sys
        pip_args = [ '-m', 'pip' ];
        pip_args.append('install');
        for req in REQUIREMENTS:
            pip_args.append( req )
        print('Installing requirements: ' + str(REQUIREMENTS))
        os.system(sys.executable+" "+" ".join(pip_args));

def boot():
    import sys
    if sys.platform == "linux" or sys.platform == "linux2":
        pass;
        # linux
    elif sys.platform == "darwin":
        pass;
        # OS X
    elif sys.platform == "win32":
        pass;
        # Windows...
    print(f"We are on {sys.platform}");
    import boot
    boot.CheckLibDependency();
    import wakeonlan;
    wakeonlan.main();

if __name__ == '__main__':
    boot();
