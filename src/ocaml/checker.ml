
let check_from_data cnf pf =
  let cnf = Rup.remove_redundant_clauses cnf in
  let pf = Rup.remove_redundant_clauses pf in
  if Rup.check_proof cnf pf then 0 else -1

let check_from_file cnf_file pf_file = 
  try
    let cnf = Dimacs.parse_cnf cnf_file in
    let pf = Dimacs.parse_drup pf_file in
    check_from_data cnf pf
  with _ -> -2

let check_from_strings cnf pf =
  try
    let cnf, _ = (Dimacs.list_from_string cnf [] 0 |> Dimacs.parse_cnf_file) in
    let pf = (Dimacs.list_from_string pf [] 0 |> Dimacs.parse_drup_file) in  
    check_from_data cnf (List.rev pf)
  with _ -> -3

let _ = Callback.register "check_from_file" check_from_file
let _ = Callback.register "check_from_strings" check_from_strings