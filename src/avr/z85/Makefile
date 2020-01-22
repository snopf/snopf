test:	
	@gcc -shared -Wl,-soname,z85 -o z85.so -fPIC z85.c -D TEST_NO_MCU -std=c99
	@gcc -shared -Wl,-soname,z85_ref -o z85_ref.so -fPIC z85_reference.c
	python z85_test.py