import pytest
from flaskr.prediction import getHeatIndex

def test_getHeatIndex(app):
    # checks the simple one
    assert getHeatIndex(68.92, 88) == 69.284

    # checks the normal version
    assert getHeatIndex(80, 80) == 84.23041599999999

    # checks where RH is < 13 and temp is between 80 and 122
    assert getHeatIndex(90, 12) == 85.6913048473959

    # checks where RH is > 85 and temp is between 80 and 87
    assert getHeatIndex(80, 86) == 85.20116310000016
