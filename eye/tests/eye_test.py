import pathlib
import eye as Eye


def test_eye_load_file():
    e = Eye.Eye()
    e.load_file(pathlib.Path(__file__).parent.resolve() / "test.asc")
    assert len(e.trial) == 2
