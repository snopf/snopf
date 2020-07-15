 #!/bin/bash
 
$dist_path=".\..\dist\pc\snopf\"
 
Remove-Item -Path ${dist_path}libcrypto-1_1.dll
Remove-Item -Path ${dist_path}Qt5Pdf.dll
Remove-Item -Path ${dist_path}Qt5Quick.dll
Remove-Item -Path ${dist_path}Qt5VirtualKeyboard.dll
