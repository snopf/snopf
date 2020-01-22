test:	
	@gcc -shared -Wl,-soname,sha256 -o sha256.so -fPIC sha256.c -D TEST_NO_MCU -std=c99
	python sha256_test.py