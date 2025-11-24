"""
Test script for ML Prediction Service
Run this to verify the service is working correctly
"""
import requests
import json

BASE_URL = "http://localhost:5000"


def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing /health endpoint")
    print("="*60)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Health check passed")


def test_housing_prediction():
    """Test housing prediction endpoint"""
    print("\n" + "="*60)
    print("Testing /predict-housing endpoint")
    print("="*60)

    # Test case 1: Terraced house in Greater London
    test_data = {
        "property_type": "T",
        "is_new": "N",
        "duration": "F",
        "county": "GREATER LONDON",
        "year": 2016,
        "month": 6
    }

    print(f"\nTest data: {json.dumps(test_data, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/predict-housing",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )

    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    result = response.json()
    assert 'price' in result
    assert result['price'] > 0
    print(f"✓ Prediction: £{result['price']:,.2f}")

    # Test case 2: Detached house (should be more expensive)
    test_data2 = {
        "property_type": "D",
        "is_new": "N",
        "duration": "F",
        "county": "GREATER LONDON",
        "year": 2016,
        "month": 6
    }

    response2 = requests.post(
        f"{BASE_URL}/predict-housing",
        json=test_data2,
        headers={"Content-Type": "application/json"}
    )

    result2 = response2.json()
    print(f"✓ Detached house: £{result2['price']:,.2f}")
    print(f"  Price difference: £{result2['price'] - result['price']:,.2f}")


def test_invalid_input():
    """Test error handling"""
    print("\n" + "="*60)
    print("Testing error handling")
    print("="*60)

    # Missing required field
    test_data = {
        "property_type": "T",
        "year": 2016
    }

    response = requests.post(
        f"{BASE_URL}/predict-housing",
        json=test_data
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 400
    print("✓ Error handling works correctly")


def test_models_endpoint():
    """Test models listing endpoint"""
    print("\n" + "="*60)
    print("Testing /models endpoint")
    print("="*60)

    response = requests.get(f"{BASE_URL}/models")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Models endpoint works")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ML PREDICTION SERVICE TESTS")
    print("="*80)
    print("\nMake sure the service is running on http://localhost:5000")
    print("Run: python server.py")
    print("\n" + "="*80)

    try:
        test_health()
        test_models_endpoint()
        test_housing_prediction()
        test_invalid_input()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to service")
        print("Make sure the service is running: python server.py")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
