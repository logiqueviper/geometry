import numpy as np
import pytest
from .statistics import holm,tests as paired_tests

def test_holm_against_known_stepdown_example():
    assert holm([.01,.04,.03,.002]).tolist()==pytest.approx([.03,.06,.06,.008])

def test_holm_permutation_and_boundaries():
    original=np.array([0,.02,.02,1,.7]);order=[4,1,0,3,2]
    assert np.allclose(holm(original)[order],holm(original[order]))
    assert holm([0,1]).tolist()==[0,1]

@pytest.mark.parametrize("invalid",[[-.1],[1.1],[np.nan],[[.1,.2]]])
def test_invalid_pvalues_rejected(invalid):
    with pytest.raises(ValueError):holm(invalid)

def test_equal_timings_do_not_reject_difference():
    result=paired_tests(np.ones(30),np.ones(30))
    assert result["wilcoxon_p"]==1
    assert result["tost_p"]==0
    assert result["mean_paired_speedup"]==1

def test_large_effect_is_not_equivalence():
    result=paired_tests(np.linspace(.5,.7,30),np.ones(30))
    assert result["wilcoxon_p"]<1e-5 and result["tost_p"]>.9
    assert result["ratio_ci_low"]>1

def test_small_precise_effect_can_be_equivalent():
    result=paired_tests(np.linspace(.9995,1.0005,30),np.ones(30))
    assert result["tost_p"]<.001

def test_noisy_null_does_not_prove_equivalence():
    result=paired_tests(np.array([.7,1.3]*15),np.ones(30))
    assert result["tost_p"]>.05

def test_nonzero_deterministic_effect_is_not_fake_finite_effect_size():
    result=paired_tests(np.full(30,.8),np.ones(30))
    assert result["paired_cohen_dz"] is None

def test_pair_shape_must_match():
    with pytest.raises(ValueError):paired_tests(np.ones(30),np.ones(29))
