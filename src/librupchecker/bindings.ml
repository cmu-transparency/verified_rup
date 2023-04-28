open Ctypes

type lit_t
type lit = lit_t structure
let struct_lit : lit_t structure typ = structure "lit_t"
let lit = typedef struct_lit "lit"
let (--) s f = field struct_lit s f
let l_var = "var" -- int
let l_sign = "sign" -- int
let l_root = "root" -- ptr void
let () = seal struct_lit

type clause_t
type clause = clause_t structure
let struct_clause : clause_t structure typ = structure "clause_t"
let clause = typedef struct_clause "clause"
let (--) s f = field struct_clause s f
let c_lits = "lits" -- ptr lit
let c_len = "len" -- int
let c_root = "root" -- ptr void
let () = seal struct_clause

type chain_t
type chain = chain_t structure
let struct_chain : chain_t structure typ = structure "chain_t"
let chain = typedef struct_chain "chain"
let (--) s f = field struct_chain s f
let ch_lits = "lits" -- ptr lit
let ch_len = "len" -- int
let ch_root = "root" -- ptr void
let () = seal struct_chain

type cnf_t
type cnf = cnf_t structure
let struct_cnf : cnf_t structure typ = structure "cnf_t"
let cnf = typedef struct_cnf "cnf"
let (--) s f = field struct_cnf s f
let cn_clauses = "clauses" -- ptr clause
let cn_len = "len" -- int
let cn_root = "root" -- ptr void
let () = seal struct_cnf

type rup_info_t
type rup_info = rup_info_t structure
let struct_rup_info : rup_info_t structure typ = structure "rup_info_t"
let rup_info = typedef struct_rup_info "rup_info"
let (--) s f = field struct_rup_info s f
let ru_clause = "rup_clause" -- clause
let ru_chain = "chain" -- chain
let ru_root = "root" -- ptr void
let () = seal struct_rup_info

type rat_info_t
type rat_info = rat_info_t structure
let struct_rat_info : rat_info_t structure typ = structure "rat_info_t"
let rat_info = typedef struct_rat_info "rat_info"
let (--) s f = field struct_rat_info s f
let ra_clause = "rat_clause" -- clause
let ra_pivot_clause = "pivot_clause" -- clause
let ra_pivot_info = "pivot_info" -- rup_info
let ra_root = "root" -- ptr void
let () = seal struct_rat_info

type result_t
type result = result_t structure
let struct_result : result_t structure typ = structure "result_t"
let result = typedef struct_result "cresult"
let (--) s f = field struct_result s f
let r_valid = "valid" -- int
let r_steps = "steps" -- cnf
let r_rup_info = "rup_info" -- rup_info
let r_rat_info = "rat_info" -- rat_info
let r_root = "root" -- ptr void
let () = seal struct_result

let of_lit l = 
  let l_t = make lit in
  let root = Root.create l_t in
  setf l_t l_var l.Rup.var1 ;
  setf l_t l_root root ;
  if l.Rup.sign then setf l_t l_sign 1 else setf l_t l_sign 0 ;
  l_t

let free_lit l =
  let root = getf l l_root in
  Root.release root

let to_lit (l : lit) : Rup.lit =
  let sign = getf l l_sign in
  { Rup.var1 = (getf l l_var) ; Rup.sign = if sign <= 0 then false else true }

let of_clause (c : Rup.lit list) =
  let c_t = make clause in
  let o = CArray.make lit (List.length c) in
  let root = Root.create o in
  List.iteri (fun i -> fun x -> CArray.set o i (of_lit x)) c ;
  setf c_t c_lits (CArray.start o) ;
  setf c_t c_len (List.length c) ;
  setf c_t c_root root ;
  c_t

let free_clause c =
  let root = getf c c_root in
  let lit_arr = CArray.from_ptr (getf c c_lits) (getf c c_len) in
  List.iter free_lit (CArray.to_list lit_arr) ;
  Root.release root

let to_clause (c : clause) : Rup.clause =
  let lit_arr = CArray.from_ptr (getf c c_lits) (getf c c_len) in
  List.map to_lit (CArray.to_list lit_arr)

let of_chain c =
  let c_t = make chain in
  let o = CArray.make lit (List.length c) in
  let root = Root.create o in
  List.iteri (fun i -> fun x -> CArray.set o i (of_lit x)) c ;
  setf c_t ch_lits (CArray.start o) ;
  setf c_t ch_len (List.length c) ;
  setf c_t ch_root root ;
  c_t

let free_chain c =
  let root = getf c ch_root in
  let lit_arr = CArray.from_ptr (getf c ch_lits) (getf c ch_len) in
  List.iter free_lit (CArray.to_list lit_arr) ;
  Root.release root

let of_cnf f =
  let cnf_t = make cnf in
  let o = CArray.make clause (List.length f) in
  let root = Root.create o in
  List.iteri (fun i -> fun x -> CArray.set o i (of_clause x)) f ;
  setf cnf_t cn_clauses (CArray.start o) ;
  setf cnf_t cn_len (List.length f) ;
  setf cnf_t cn_root root ;
  cnf_t

let free_cnf c =
  let root = getf c cn_root in
  let clause_arr = CArray.from_ptr (getf c cn_clauses) (getf c cn_len) in
  List.iter free_clause (CArray.to_list clause_arr) ;
  Root.release root

let of_rup_info info =
  let rup_info_t = make rup_info in
  let root = Root.create rup_info_t in
  setf rup_info_t ru_clause (of_clause info.Rup.rup_clause) ;
  setf rup_info_t ru_chain (of_chain info.Rup.chain2) ;
  setf rup_info_t ru_root root ;
  rup_info_t

let free_rup_info info =
  let info = !@info in
  let root = getf info ru_root in
  free_clause (getf info ru_clause) ;
  free_chain (getf info ru_chain) ;
  Root.release root

let of_rat_info info =
  let rat_info_t = make rat_info in
  let root = Root.create rat_info_t in
  setf rat_info_t ra_clause (of_clause info.Rup.rat_clause) ;
  setf rat_info_t ra_pivot_clause (of_clause info.Rup.pivot_clause) ;
  setf rat_info_t ra_pivot_info (of_rup_info info.Rup.pivot_info) ;
  setf rat_info_t ra_root root ;
  rat_info_t

let free_rat_info info =
  let info = !@info in
  let root = getf info ra_root in
  free_clause (getf info ra_clause) ;
  free_clause (getf info ra_pivot_clause) ;
  let rup_p = allocate rup_info (getf info ra_pivot_info) in
  free_rup_info rup_p ;
  Root.release root

let print_clause c =
  let rec aux c =
    match c with
    | [] -> Printf.printf "0\n" ; flush stdout
    | l :: ls -> 
      if l.Rup.sign then Printf.printf "%d " l.Rup.var1 
      else Printf.printf "-%d " l.Rup.var1 ; 
      aux ls
  in aux c

let print_clauses cs =
  let rec aux cs =
    match cs with
    | [] -> flush stdout
    | c :: cs -> print_clause c ; aux cs
  in aux cs

let free_result r =
  let r = !@r in
  let root = getf r r_root in
  Root.release root

let check cnf pf =
  let cnf_arr = CArray.from_ptr (getf !@cnf cn_clauses) (getf !@cnf cn_len) in
  let cnf = List.map to_clause (CArray.to_list cnf_arr) in
  let pf_arr = CArray.from_ptr (getf !@pf cn_clauses) (getf !@pf cn_len) in
  let pf = List.map to_clause (CArray.to_list pf_arr) in
  let cnf = Rup.remove_redundant_clauses cnf in
  let pf = Rup.remove_redundant_clauses pf in
  let result_t = make result in
  match Rup.check_proof cnf pf [] with
  | Rup.Valid -> 
    setf result_t r_valid 1 ; 
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p
  | Rup.InvalidEmpty (steps, info) -> 
    setf result_t r_valid 0 ; 
    setf result_t r_steps (of_cnf steps) ;
    setf result_t r_rup_info (of_rup_info info) ;
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p
  | Rup.InvalidStep (steps, rup_info, rat_info) -> 
    setf result_t r_valid (-1) ; 
    setf result_t r_steps (of_cnf steps) ;
    setf result_t r_rup_info (of_rup_info rup_info) ; 
    setf result_t r_rat_info (of_rat_info rat_info) ;
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p

let check_derivation cnf pf =
  let cnf_arr = CArray.from_ptr (getf !@cnf cn_clauses) (getf !@cnf cn_len) in
  let cnf = List.map to_clause (CArray.to_list cnf_arr) in
  let pf_arr = CArray.from_ptr (getf !@pf cn_clauses) (getf !@pf cn_len) in
  let pf = List.map to_clause (CArray.to_list pf_arr) in
  let cnf = Rup.remove_redundant_clauses cnf in
  let pf = Rup.remove_redundant_clauses pf in
  let result_t = make result in
  match Rup.check_derivation cnf pf [] with
  | Rup.Valid -> 
    setf result_t r_valid 1 ; 
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p
  | Rup.InvalidEmpty (steps, info) -> 
    setf result_t r_valid 0 ; 
    setf result_t r_steps (of_cnf steps) ;
    (* print_clause info.Rup.rup_clause ; *)
    setf result_t r_rup_info (of_rup_info info) ;
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p
  | Rup.InvalidStep (steps, rup_info, rat_info) -> 
    setf result_t r_valid (-1) ; 
    setf result_t r_steps (of_cnf steps) ;
    setf result_t r_rup_info (of_rup_info rup_info) ; 
    setf result_t r_rat_info (of_rat_info rat_info) ;
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p
  
let check_fast cnf pf =
  let cnf_arr = CArray.from_ptr (getf !@cnf cn_clauses) (getf !@cnf cn_len) in
  let cnf = List.map to_clause (CArray.to_list cnf_arr) in
  let pf_arr = CArray.from_ptr (getf !@pf cn_clauses) (getf !@pf cn_len) in
  let pf = List.map to_clause (CArray.to_list pf_arr) in
  let cnf = Rup.remove_redundant_clauses cnf in
  let pf = Rup.remove_redundant_clauses pf in
  let result_t = make result in
  match Rup.check_proof cnf pf [] with
  | Rup.Valid -> 
    setf result_t r_valid 1 ; 
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p
  | Rup.InvalidEmpty (_, _) -> 
    setf result_t r_valid 0 ; 
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p
  | Rup.InvalidStep (_, _, _) -> 
    setf result_t r_valid (-1) ; 
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p

let check_derivation_fast cnf pf =
  let cnf_arr = CArray.from_ptr (getf !@cnf cn_clauses) (getf !@cnf cn_len) in
  let cnf = List.map to_clause (CArray.to_list cnf_arr) in
  let pf_arr = CArray.from_ptr (getf !@pf cn_clauses) (getf !@pf cn_len) in
  let pf = List.map to_clause (CArray.to_list pf_arr) in
  let cnf = Rup.remove_redundant_clauses cnf in
  let pf = Rup.remove_redundant_clauses pf in
  let result_t = make result in
  match Rup.check_derivation cnf pf [] with
  | Rup.Valid -> 
    setf result_t r_valid 1 ; 
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p
  | Rup.InvalidEmpty (_, _) -> 
    setf result_t r_valid 0 ; 
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p
  | Rup.InvalidStep (_, _, _) -> 
    setf result_t r_valid (-1) ; 
    let result_p = Ctypes.allocate result result_t in
    let root = Root.create result_p in
    setf !@result_p r_root root ;
    result_p

module Stubs(I: Cstubs_inverted.INTERNAL) = 
struct

  let () = I.structure struct_lit
  let () = I.typedef struct_lit "lit"
  let () = I.structure struct_clause
  let () = I.typedef struct_clause "clause"
  let () = I.structure struct_cnf
  let () = I.typedef struct_cnf "cnf"
  let () = I.structure struct_chain
  let () = I.typedef struct_chain "chain"
  let () = I.structure struct_rup_info
  let () = I.typedef struct_rup_info "rup_info"
  let () = I.structure struct_rat_info
  let () = I.typedef struct_rat_info "rat_info"
  let () = I.structure struct_result
  let () = I.typedef struct_result "cresult"
  let () = I.internal "check" (ptr cnf @-> ptr cnf @-> returning (ptr result)) check
  let () = I.internal "check_derivation" (ptr cnf @-> ptr cnf @-> returning (ptr result)) check_derivation
  let () = I.internal "check_fast" (ptr cnf @-> ptr cnf @-> returning (ptr result)) check_fast
  let () = I.internal "check_derivation_fast" (ptr cnf @-> ptr cnf @-> returning (ptr result)) check_derivation_fast
  let () = I.internal "free_rup_info" (ptr rup_info @-> returning void) free_rup_info
  let () = I.internal "free_rat_info" (ptr rat_info @-> returning void) free_rat_info
  let () = I.internal "free_result" (ptr result @-> returning void) free_result

end