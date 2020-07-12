 #!/bin/bash
 
$dist_path="..\dist\pc\snopf\"
 
Remove-Item -Path ${dist_path}libQt5WebEngineCore.so.5 -ErrorAction Ignore
Remove-Item -Path ${dist_path}libQt53DRender.so.5 -ErrorAction Ignore
Remove-Item -Path ${dist_path}libcrypto.so.1.1 -ErrorAction Ignore
Remove-Item -Path ${dist_path}libQt5Charts.so.5 -ErrorAction Ignore
Remove-Item -Path ${dist_path}libQt5Bluetooth.so.5 -ErrorAction Ignore
Remove-Item -Path ${dist_path}libQt5Multimedia.so.5 -ErrorAction Ignore
Remove-Item -Path ${dist_path}libQt5Quick3DRuntimeRender.so.5 -ErrorAction Ignore
Remove-Item -Path ${dist_path}PySide2/QtQml.abi3.so -ErrorAction Ignore
Remove-Item -Path ${dist_path}PySide2/qml -Recurse -ErrorAction Ignore
 
