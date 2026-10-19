include "rlfap_core.mzn";
solve :: int_search(frequency, first_fail, indomain_min, complete) minimize objective;
