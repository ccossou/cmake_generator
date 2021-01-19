import pytest
from cmake_generator import parser
import numpy as np

test_data = [
    ("project(JSONUtils 1.1.0 CXX)", ("project", ("JSONUtils", "1.1.0", "CXX"))),
    ("install($ENV{HOME}/install)", ("install", ("$ENV{HOME}/install",))),
]


@pytest.mark.parametrize("text, ref", test_data)
def test_parse_command(text, ref):
    """
    Test parse_command

    """
    ref_command, ref_args = ref

    command, args = parser.parse_command(text)

    assert command == ref_command

    np.testing.assert_array_equal(args, ref_args)