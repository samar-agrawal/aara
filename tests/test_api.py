import pytest
from app.api import app, get_abi, ContractEventRead

mock_abi = [{'anonymous': False,
  'inputs': [{'indexed': False, 'name': 'name', 'type': 'string'},
   {'indexed': True, 'name': 'label', 'type': 'bytes32'},
   {'indexed': True, 'name': 'owner', 'type': 'address'},
   {'indexed': False, 'name': 'cost', 'type': 'uint256'},
   {'indexed': False, 'name': 'expires', 'type': 'uint256'}],
  'name': 'NameRegistered',
  'type': 'event'}]

def test_hc():
    resp = app.test_client().get('/public/hc')
    assert resp.status_code == 200, "URL not set correctly"

def test_missing_params():
    resp = app.test_client().get('/api/data/')
    assert resp.status_code == 422, "Should fail when no address code supplied"

def test_invalid_address():
    with pytest.raises(AssertionError):
        ContractEventRead(address='testaddr01', event_name='testevnt01', abi=mock_abi)

def test_invalid_event():
    with pytest.raises(AssertionError):
        address = '0xF0AD5cAd05e10572EfcEB849f6Ff0c68f9700455'
        ContractEventRead(address=address, event_name='testevnt01', abi=mock_abi)

def test_valid_contract():
    address = '0xF0AD5cAd05e10572EfcEB849f6Ff0c68f9700455'
    contract = ContractEventRead(address=address, event_name='NameRegistered', abi=mock_abi)
    assert contract, "Failed"

def test_valid_lower_address():
    address = '0xf0ad5cad05e10572efceb849f6ff0c68f9700455'
    contract = ContractEventRead(address=address, event_name='NameRegistered', abi=mock_abi)
    assert contract, "Failed"

### need internet connection / valid node key

def test_invalid_contract():
    resp = app.test_client().get('/api/data/?address=0xd3CdA913deB6f67967B99D67aCDFa1712C293601&event_name=test02')
    assert resp.json['error'] == 'Contract source code not verified', 'Should fail with invalid contract'

def test_valid_event_with_no_data():
    resp = app.test_client().get('/api/data/?address=0xF0AD5cAd05e10572EfcEB849f6Ff0c68f9700455&event_name=NewPriceOracle')
    assert resp.status_code == 204, "no data, should send 204"

def test_inject_get_param():
    resp = app.test_client().get('/api/data/?address=0xF0AD5cAd05e10572EfcEB849f6Ff0c68f9700455&event_name=NewPriceOracle;%20select%20sleep%20(5);')
    assert resp.json['error'].startswith('Invalid Event'), "Should fail with invalid event"

def test_valid_request():
    resp = app.test_client().get('/api/data/?address=0xF0AD5cAd05e10572EfcEB849f6Ff0c68f9700455&event_name=NameRegistered')
    assert resp.status_code == 200 and len(resp.json) > 5, "Should pass"

def test_get_abi_invalid_address():
    with pytest.raises(AssertionError):
        get_abi('foobar')
