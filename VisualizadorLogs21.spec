# -*- mode: python -*-

import sys
sys.setrecursionlimit(5000)

block_cipher = None


a = Analysis(['view\\Visualizador.py'],
             pathex=['C:\\Users\\eduardo.sachser\\Documents\\PyTests\\visualizador-de-logs'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='VisualizadorLogs21',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='view\\VisIcon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='VisualizadorLogs21')
