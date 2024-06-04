import httpx  # type: ignore


def test_server_health(antares_web_server):
    """
    Test the health endpoint of the Antares web server.
    """

    res = httpx.get("http://localhost:8000/health", timeout=0.25)
    assert res.status_code == 200, res.json()
    assert res.json() == {"status": "available"}
