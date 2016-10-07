command! -nargs=? -complete=file Uppy call Reload(<f-args>) 

function! PubInit()
python << EOF
import os
import sys
from vimenv import env
sPath=env.var("$VIM")+r"\vimfiles\bundle"
for sDir in os.listdir(sPath):
	sPythonx="%s\\%s\\pythonx"%(sPath,sDir)
	if not os.path.isdir(sPythonx):
		continue
	if not sPythonx in sys.path:
		sys.path.append(sPythonx)
EOF
endfunction

function! Reload(...)
    if a:0==#0
        let sMod=""
    else
        let sMod=a:1
    endif
python << EOF
import xreload
import sys
from vimenv import env
def DoUppy(sMod):
    if sMod=="":
        sMod=env.var('expand("%:p")')
        if not sMod.endswith(".py"):
            env.message("not py")
            return
        sMod=sMod.replace(".py","")
        sMod=sMod.replace("\\__init__","")
        for sPath in sys.path:
            if not sPath in sMod:
                continue
            sMod=sMod[len(sPath)+1:]
            sMod=sMod.replace("\\",".")
            break
        env.exe("w")
    exec("import "+sMod)
    xreload.xreload(eval(sMod))
    env.message("comreload "+sMod)
sMod=env.var("sMod")
DoUppy(sMod)
EOF
endfunction

call PubInit()
