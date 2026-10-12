import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from sensor_core import Window, check_alerts, parse_payload


def test_parse_valid():
    r = parse_payload('{"device":"esp32-01","temp":27.4,"hum":55.2}')
    assert r.device == "esp32-01" and r.temperature == 27.4 and r.humidity == 55.2


@pytest.mark.parametrize("bad", ["not json", '{"temp": 20}', '{"temp":"x","hum":1}', '{"temp":500,"hum":50}', '{"temp":20,"hum":150}'])
def test_parse_rejects_bad(bad):
    with pytest.raises(ValueError):
        parse_payload(bad)


def test_alerts():
    assert check_alerts(parse_payload('{"temp":25,"hum":50}')) == []
    assert len(check_alerts(parse_payload('{"temp":40,"hum":90}'))) == 2


def test_window_stats_and_limit():
    w = Window(3)
    for t in (20, 30, 40, 50):
        w.add(parse_payload(f'{{"temp":{t},"hum":50}}'))
    s = w.stats()
    assert s["count"] == 3 and s["temp_max"] == 50 and s["temp_avg"] == 40
