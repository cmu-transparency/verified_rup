
let check_from_data cnf pf =
  try
    let cnf = Rup.remove_redundant_clauses cnf in
    let pf = Rup.remove_redundant_clauses pf in
    if Rup.check_proof cnf pf then 0 else -1
  with _ -> -6

  let check_step_from_data cnf c =
    try
      let cnf = Rup.remove_redundant_clauses cnf in
      let c = Rup.remove_redundant_clauses c in
      let rec aux cnf cs =
        match cs with
        | [] -> 0
        | c :: cs ->
          if (Rup.check_rup cnf c) || (Rup.check_rat cnf c) then aux cnf cs else -1
      in aux cnf c
    with _ -> -6

let check_proof_from_file cnf_file pf_file = 
  let cnf = try Some (Dimacs.parse_cnf cnf_file) with _ -> None in
  let pf = try Some (Dimacs.parse_drup pf_file) with _ -> None in
  match cnf, pf with
  | None, _ -> -2
  | _, None -> -3
  | Some cnf, Some pf -> check_from_data cnf pf

let check_proof_from_strings cnf pf =
  let cnf = try Some (Dimacs.list_from_string cnf [] 0 |> Dimacs.parse_cnf_file) with _ -> None in
  let pf = try Some (Dimacs.list_from_string pf [] 0 |> Dimacs.parse_drup_file) with _ -> None in
  match cnf, pf with
  | None, _ -> -4
  | _, None -> -5
  | Some cnf, Some pf -> check_from_data cnf (List.rev pf)

let check_step_from_strings cnf c =
  let cnf = try Some (Dimacs.list_from_string cnf [] 0 |> Dimacs.parse_cnf_file) with _ -> None in
  let c = try Some (Dimacs.list_from_string c [] 0 |> Dimacs.parse_drup_file) with _ -> None in
  match cnf, c with
  | None, _ -> -4
  | _, None -> -5
  | Some cnf, Some c -> check_step_from_data cnf c

let check_derivation_from_strings cnf steps =
  let cnf = try Some (Dimacs.list_from_string cnf [] 0 |> Dimacs.parse_cnf_file) with _ -> None in
  let steps = try Some (Dimacs.list_from_string steps [] 0 |> Dimacs.parse_drup_file) with _ -> None in
  match cnf, steps with
  | None, _ -> -4
  | _, None -> -5
  | Some cnf, Some steps -> 
    let rec aux cnf steps =
      match steps with
      | [] -> 0
      | c :: steps -> if (check_step_from_data cnf (c :: [])) == 0 then aux (c :: cnf) steps else -1
    in aux cnf steps

let _ = Callback.register "check_proof_from_file" check_proof_from_file
let _ = Callback.register "check_proof_from_strings" check_proof_from_strings
let _ = Callback.register "check_step_from_strings" check_step_from_strings
let _ = Callback.register "check_derivation_from_strings" check_derivation_from_strings