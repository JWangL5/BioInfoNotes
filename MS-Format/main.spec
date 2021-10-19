# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
SETUP_DIR = 'F:\\PythonCode\\MS-Format\\MS-Format\\'

a = Analysis(['.\\MS-Format\\main.py', '.\\MS-Format\\ms_tools.py'],
             pathex=['F:\\PythonCode\\MS-Format\\MS-Format', 'F:\\PythonCode\\MS-Format'],
             binaries=[],
             datas=[
				(SETUP_DIR+"ref\\fbgn_annotation_ID_fb_2020_06.tsv", "ref\\fbgn_annotation_ID_fb_2020_06.tsv"),
				(SETUP_DIR+"ref\\fbgn_fbtr_fbpp_expanded_fb_2020_06.tsv", "ref\\fbgn_fbtr_fbpp_expanded_fb_2020_06.tsv"),
				(SETUP_DIR+"ref\\gene_association_v2.2.fb", "ref\\gene_association_v2.2.fb"),
				(SETUP_DIR+"ref\\go.obo", "ref\\go.obo"),
				(SETUP_DIR+"ref\\go.csv", "ref\\go.csv"),
				(SETUP_DIR+"ref\\gene_snapshots_fb_2020_06.tsv", "ref\\gene_snapshots_fb_2020_06.tsv"),
				(SETUP_DIR+"ref\\logo.png", "ref\\logo.png")],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
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
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
