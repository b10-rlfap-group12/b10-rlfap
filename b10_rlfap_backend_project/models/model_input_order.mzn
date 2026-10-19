include "rlfap_core.mzn";
solve :: int_search(frequency, input_order, indomain_min, complete) minimize objective;
