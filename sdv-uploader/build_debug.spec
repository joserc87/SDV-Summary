# -*- mode: python -*-

block_cipher = None


a = Analysis(['__init__.py'],
             pathex=['/Users/bob/SDV/sdv-uploader'],
             binaries=[],
             datas=[('images','images'),
                    ('help','help'),
                    ('icons','icons')],
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
          name='__init__',
          debug=False,
          strip=False,
          upx=True,
          console=True,
          icon='images/logo-square.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='__init__')
