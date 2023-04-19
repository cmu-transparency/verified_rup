#include <stdio.h>
#include <string.h>
#include <caml/mlvalues.h>
#include <caml/callback.h>
#include <caml/alloc.h>

int check_derivation_from_strings(const char *dimacs, const char *cs)
{
	static const value *check_d_from_strings_closure = NULL;
  	if (check_d_from_strings_closure == NULL)
		check_d_from_strings_closure = caml_named_value("check_derivation_from_strings");
  	return Int_val(caml_callback2(*check_d_from_strings_closure, caml_copy_string(dimacs), caml_copy_string(cs)));
}

int check_proof_from_file(const char *dimacs, const char *drup)
{
	static const value *check_p_from_file_closure = NULL;
  	if (check_p_from_file_closure == NULL)
		check_p_from_file_closure = caml_named_value("check_proof_from_file");
  	return Int_val(caml_callback2(*check_p_from_file_closure, caml_copy_string(dimacs), caml_copy_string(drup)));
}

int check_proof_from_strings(const char *dimacs, const char *drup)
{
	static const value *check_p_from_strings_closure = NULL;
  	if (check_p_from_strings_closure == NULL)
		check_p_from_strings_closure = caml_named_value("check_proof_from_strings");
  	return Int_val(caml_callback2(*check_p_from_strings_closure, caml_copy_string(dimacs), caml_copy_string(drup)));
}

int check_step_from_strings(const char *dimacs, const char *c)
{
	static const value *check_s_from_strings_closure = NULL;
  	if (check_s_from_strings_closure == NULL)
		check_s_from_strings_closure = caml_named_value("check_step_from_strings");
  	return Int_val(caml_callback2(*check_s_from_strings_closure, caml_copy_string(dimacs), caml_copy_string(c)));
}

int do_startup(char **argv) {
	caml_startup(argv);
}