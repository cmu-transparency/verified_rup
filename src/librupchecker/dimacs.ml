(*
 * Adapted from code written by Jonathan Laurent for
 * the course "Bug Catching: Automated Program Verification"
 * at Carnegie Mellon University in Fall 2018.
 *)

 open String

 let read_from_file filename =
   let lines = ref "" in
   let chan = open_in filename in
     set_binary_mode_in chan false ;
     try
       while true; do
         let line = input_line chan in
         if (length line>0)&&(not ((line.[0]) = 'c' || (line.[0] = 'd'))) then 
           lines := (!lines)^"\n"^(String.trim line)
       done; ""
     with End_of_file ->
       close_in chan;
       !lines
 
 let latexescaped = function
   | '%' | '{' | '}' as c -> "\\"^Char.escaped c
   | c -> Char.escaped c
 
 let rec list_from_string s list_so_far n = 
   if (n>=length s) then List.rev list_so_far 
   else
     match s.[n] with 
       | ' ' | '\n' | '\t' -> list_from_string s list_so_far (n+1)
       | '-'  -> list_from_string s ("-"::list_so_far) (n+1)
       |  _   ->
       let rec word_from_string s word_so_far n =
       if (n>=length s) then List.rev (word_so_far::list_so_far) 
       else
         begin
           match s.[n] with
           | ' '| '\n' | '\t' -> list_from_string s (word_so_far::list_so_far) n
           | c    -> word_from_string s (word_so_far^(latexescaped c)) (n+1)
         end
       in word_from_string s "" n
 
 module PairLit = struct
   type t = bool*string
   let negation (b,s) = (not b,s)
 end
 
 let rec parse_cnf_list cnf_so_far: string list -> Rup.lit list list  = function
   | []     -> cnf_so_far
   | "0"::l -> parse_cnf_list ([]::cnf_so_far) l
   | l -> let rec parse_clause clause_so_far ispos = function
            | []     -> parse_cnf_list ((List.rev clause_so_far)::cnf_so_far) []
            | "0"::l -> parse_cnf_list ((List.rev clause_so_far)::cnf_so_far) l
            | "-"::l -> parse_clause clause_so_far false l
            | s::l   -> 
             try 
               let var = int_of_string s in
               parse_clause ({Rup.var1=var-1; Rup.sign=ispos}::clause_so_far) true l  
             with Failure _ -> parse_clause clause_so_far true l
          in parse_clause [] true l
 
 let rec parse_cnf_file = function
   | []     -> []
   | "p"::"cnf"::_::_::l -> parse_cnf_list [] l
   | a::l -> parse_cnf_file l
 
 let parse_drup_file = function
   | []     -> []
   | l      -> parse_cnf_list [] l
 
 let parse_cnf x = (list_from_string (read_from_file x) [] 0 |> parse_cnf_file) 
 
 let parse_drup x =
   let clause_list = (list_from_string (read_from_file x) [] 0 |> parse_drup_file) in
   List.rev clause_list