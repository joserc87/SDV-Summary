# -*- mode: python -*-
LOGO = 'logo.icns'
MAC_APP_LABEL = 'farm.upload.uploader'
version = '2.0'
name = 'upload.farm uploader'
include_files = [(i,i) for i in ['images','help','icons']]

block_cipher = None

a = Analysis(['__init__.py'],
             pathex=['/Users/bob/SDV/sdv-uploader'],
             binaries=[],
             datas=include_files,
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='__init__',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon=LOGO)
app = BUNDLE(exe,
             name='{}.app'.format(name),
             icon=LOGO,
             bundle_identifier=MAC_APP_LABEL,
             version=version)
