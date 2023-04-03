import os
import constants

DIR_NAME = (os.path.split(__file__)[0])
VERSION = '0.0.2.1'


spec = r'''# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis([r"{dir}\\init.py"],
             pathex=[],
             binaries=[],
             datas=[(r"{assets_dir}",r'.\\{assets}')],
             hiddenimports=[
             r"{dir}\\GUI.py",
             r"{dir}\\functions.py",
             r"{dir}\\constants.py",
             r"{dir}\\scene\main.py",
             r"{dir}\\main.py",
             r"{dir}\\report.py",
],
             hookspath=[],
             hooksconfig={dct},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='{name}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
	  icon=r"{assets_dir}\ico.png",
          version=r'{version_file}')
'''.format(dct='{}', dir=DIR_NAME, assets=constants.DATAS_FOLDER_NAME, assets_dir=os.path.join(DIR_NAME, constants.DATAS_FOLDER_NAME), name=constants.NAME.replace(' ', ''), version_file=os.path.join(DIR_NAME, 'build', 'version.txt'))

version = r'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({split_version}),
    prodvers=({split_version}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{author}'),
        StringStruct(u'FileDescription', '{name}'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'InternalName', u'ESP'),
        StringStruct(u'LegalCopyright', u'MIT License'),
        StringStruct(u'LegalTrademarks', u'{author}'),
        StringStruct(u'OriginalFilename', u'{name}.exe'),
        StringStruct(u'ProductName', u'{name}'),
        StringStruct(u'ProductVersion', u'{version}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''.format(dir=DIR_NAME, name=constants.NAME.replace(' ', ''), version_file=VERSION, version=VERSION, split_version=VERSION.replace('.', ','), author=constants.AUTHOR)

if not os.path.exists(os.path.join(DIR_NAME, 'build')):
    os.mkdir(os.path.join(DIR_NAME, 'build'))

with open(os.path.join(DIR_NAME, 'build', 'main.spec'), 'w') as f:
    f.write(spec)

with open(os.path.join(DIR_NAME, 'build', 'version.txt'), 'w') as f:
    f.write(version)
os.chdir(os.path.join(DIR_NAME, 'build'))
os.system('pyinstaller main.spec')

