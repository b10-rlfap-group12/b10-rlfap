% B10 Radio Link Frequency Assignment (RLFAP)
% Compact model used for the reproducible synthetic experiment.
% Frequency variables are integer channels in a bounded band.
int: seed; % recorded provenance seed; it does not affect solving
int: n_vars;
int: n_constraints;
int: max_frequency;
array[1..n_constraints] of int: v1;
array[1..n_constraints] of int: v2;
array[1..n_constraints] of int: min_distance;
array[1..n_constraints] of int: weight;

% Duplex pairs: the two links must use a fixed frequency offset.
% The generator currently uses gap 0 for a same-channel duplex pair.
int: n_duplex;
array[1..n_duplex] of int: duplex_a;
array[1..n_duplex] of int: duplex_b;
array[1..n_duplex] of int: duplex_gap;

% Decision variable: one integer frequency per radio link.
array[1..n_vars] of var 1..max_frequency: frequency;
% Reified soft-constraint violation indicators.
array[1..n_constraints] of var 0..1: violated;

% Interfering links must be separated by at least min_distance[c].
constraint forall(c in 1..n_constraints)(
  violated[c] = bool2int(abs(frequency[v1[c]] - frequency[v2[c]]) < min_distance[c])
);

% Duplex links obey an exact frequency relation.
constraint forall(k in 1..n_duplex)(
  frequency[duplex_a[k]] - frequency[duplex_b[k]] = duplex_gap[k]
);

% Minimize weighted interference violations.
var int: objective = sum(c in 1..n_constraints)(weight[c] * violated[c]);

output [
  "objective=", show(objective), ";\n",
  "frequency=", show(frequency), ";\n",
  "violated=", show(violated), ";\n"
];
