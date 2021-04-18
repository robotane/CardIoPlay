# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hdp = ["pkg_resources.py2_warn", "pygame_gui","pygame"]  # Added py2_warn for setuptools 45.0 and later.

added_files = [
           ('C:\PycharmProjects\CardIoPlay\cards', 'cards'),
            ('C:\PycharmProjects\CardIoPlay\*.*', '.'),
			(r'C:\Users\Robotane\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\pygame_gui\data\*', 'pygame_gui\data'),
			]

a = Analysis(['ui_main.py'],
             pathex=['C:\PycharmProjects\CardIoPlay'],
             binaries=[],
             datas=added_files,
             hiddenimports= hdp,
             hookspath=[],
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
          name='CardioPlay',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
