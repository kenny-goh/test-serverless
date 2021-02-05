import requests
import os
import json
import subprocess
import pytest
import time

baseUrl = ""

def getPort():
    return os.getenv("PORT", "3000")

def getHost():
    return os.getenv("HOST", "localhost")

def getProtocol():
    return os.getenv("PROTOCOL", "http")

def getStackJsonFile():
    return os.getenv("STACK_JSON_FILE","")

@pytest.fixture(scope="session")
def test_fixture():

    print("running tests!!!")
    process = None

    if (not _isDeployedToCloud()):
        print ("Detected local mode")
        baseUrl = _build_base_url()
        print(baseUrl)
        print("Starting serverless offline")
        process = subprocess.Popen(['serverless', 'offline', '--port', getPort()], stdout=subprocess.PIPE)
        # Give the server time to start
        time.sleep(5)
        # Check it started successfully
        assert not process.poll(), process.stdout.read().decode("utf-8")
        yield process
    else:
        baseUrl = _getServiceEndPoint()

    # yield  # this is where the testing happens

    # Teardown
    if process:
        print("Killing serverless offline")
        process.terminate()

def test_given_url_when_get_hello_verify_status_code(test_fixture):
    baseUrl = _getServiceEndPoint() if (_isDeployedToCloud()) else _build_base_url()
    r = requests.get(baseUrl + '/hello')
    assert r.status_code == 200

def _build_base_url():
    """ Helper function to build base url """
    return getProtocol() + "://" + getHost() + ":" + getPort()

def _isDeployedToCloud():
    return os.path.isfile(getStackJsonFile())

def _getServiceEndPoint():
    if os.path.isfile(getStackJsonFile()):
        with open(getStackJsonFile(), 'r') as f:
            stack = json.load(f.read())
            return stack['ServiceEndpoint']
    raise Exception("stack json file not found")
