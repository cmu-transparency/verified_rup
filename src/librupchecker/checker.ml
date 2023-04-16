
let check_from_data cnf pf =
  try
    let cnf = Rup.remove_redundant_clauses cnf in
    let pf = Rup.remove_redundant_clauses pf in
    if Rup.check_proof cnf pf then 0 else -1
  with _ -> -6

let check_from_file cnf_file pf_file = 
  let cnf = try Some (Dimacs.parse_cnf cnf_file) with _ -> None in
  let pf = try Some (Dimacs.parse_drup pf_file) with _ -> None in
  match cnf, pf with
  | None, _ -> -2
  | _, None -> -3
  | Some cnf, Some pf -> check_from_data cnf pf

let check_from_strings cnf pf =
  let cnf = try Some (Dimacs.list_from_string cnf [] 0 |> Dimacs.parse_cnf_file) with _ -> None in
  let pf = try Some (Dimacs.list_from_string pf [] 0 |> Dimacs.parse_drup_file) with _ -> None in
  match cnf, pf with
  | None, _ -> -4
  | _, None -> -5
  | Some cnf, Some pf -> check_from_data cnf (List.rev pf)

let _ = Callback.register "check_from_file" check_from_file
let _ = Callback.register "check_from_strings" check_from_strings