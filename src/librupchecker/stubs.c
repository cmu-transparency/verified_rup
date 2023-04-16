#include <stdio.h>
#include <string.h>
#include <caml/mlvalues.h>
#include <caml/callback.h>
#include <caml/alloc.h>

int check_from_file(const char *dimacs, const char *drup)
{
	static const value *check_from_file_closure = NULL;
  	if (check_from_file_closure == NULL)
		check_from_file_closure = caml_named_value("check_from_file");
  	return Int_val(caml_callback2(*check_from_file_closure, caml_copy_string(dimacs), caml_copy_string(drup)));
}

int check_from_strings(const char *dimacs, const char *drup)
{
	static const value *check_from_strings_closure = NULL;
  	if (check_from_strings_closure == NULL)
		check_from_strings_closure = caml_named_value("check_from_strings");
  	return Int_val(caml_callback2(*check_from_strings_closure, caml_copy_string(dimacs), caml_copy_string(drup)));
}

int do_startup(char **argv) {
	caml_startup(argv);
}