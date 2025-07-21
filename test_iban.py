#!/usr/bin/env python3
"""
Simple test script for IBAN enrichment functionality.
Tests both free (OpenIBAN) and paid (IbanApi.com) scenarios.
"""

import asyncio
import logging
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, 'app')

from app.providers.iban import IbanEnrichmentClient # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set specific loggers to DEBUG
logging.getLogger("app.providers.iban").setLevel(logging.DEBUG)

# Test IBAN from user
TEST_IBAN = "PL26105010121000009031550438"

async def test_free_scenario():
    """Test free scenario (OpenIBAN.com only)."""
    print("\n" + "="*60)
    print("🆓 TESTING FREE SCENARIO (OpenIBAN.com only)")
    print("="*60)

    client = IbanEnrichmentClient(
        ibanapi_com_key=None,  # No API key
        apilayer_api_key=None
    )

    result = await client.enrich_bank_account(TEST_IBAN)

    print("\n📋 RESULT:")
    print(f"Account: {result.get('account_number')}")
    print(f"Valid: {result.get('validated')}")
    print(f"Bank Name: {result.get('bank_name')}")
    print(f"BIC: {result.get('bic')}")
    print(f"Enrichment Available: {result.get('enrichment_available')}")
    print(f"Enrichment Source: {result.get('enrichment_source')}")

    return result


async def test_paid_scenario():
    """Test paid scenario (IbanApi.com)."""
    print("\n" + "="*60)
    print("💰 TESTING PAID SCENARIO (IbanApi.com)")
    print("="*60)

    # Get API key from environment
    ibanapi_key = os.getenv('IBANAPI_COM_KEY')
    if not ibanapi_key:
        print("❌ No IBANAPI_COM_KEY found in environment variables!")
        print("Set it with: export IBANAPI_COM_KEY=your_api_key")
        return None

    print(f"✅ Found API key: {ibanapi_key[:10]}...")

    client = IbanEnrichmentClient(
        ibanapi_com_key=ibanapi_key,
        apilayer_api_key=None
    )

    result = await client.enrich_bank_account(TEST_IBAN)

    print(f"\n📋 RESULT:")
    print(f"Account: {result.get('account_number')}")
    print(f"Valid: {result.get('validated')}")
    print(f"Bank Name: {result.get('bank_name')}")
    print(f"BIC: {result.get('bic')}")
    print(f"Enrichment Available: {result.get('enrichment_available')}")
    print(f"Enrichment Source: {result.get('enrichment_source')}")

    return result


async def test_invalid_iban():
    """Test with invalid IBAN."""
    print("\n" + "="*60)
    print("❌ TESTING INVALID IBAN")
    print("="*60)

    invalid_iban = "INVALID123"

    client = IbanEnrichmentClient()
    result = await client.enrich_bank_account(invalid_iban)

    print(f"\n📋 RESULT:")
    print(f"Account: {result.get('account_number')}")
    print(f"Valid: {result.get('validated')}")
    print(f"Error: {result.get('enrichment_error')}")

    return result


async def compare_results():
    """Compare free vs paid results."""
    print("\n" + "="*60)
    print("🔄 COMPARING FREE VS PAID RESULTS")
    print("="*60)

    free_result = await test_free_scenario()
    paid_result = await test_paid_scenario()

    if paid_result is None:
        print("❌ Cannot compare - paid scenario failed")
        return

    print(f"\n📊 COMPARISON:")
    print(f"{'Field':<20} {'Free':<20} {'Paid':<20}")
    print("-" * 60)
    print(f"{'Bank Name':<20} {str(free_result.get('bank_name', 'N/A')):<20} {str(paid_result.get('bank_name', 'N/A')):<20}")
    print(f"{'BIC':<20} {str(free_result.get('bic', 'N/A')):<20} {str(paid_result.get('bic', 'N/A')):<20}")
    print(f"{'Source':<20} {str(free_result.get('enrichment_source', 'N/A')):<20} {str(paid_result.get('enrichment_source', 'N/A')):<20}")
    print(f"{'Available':<20} {str(free_result.get('enrichment_available', False)):<20} {str(paid_result.get('enrichment_available', False)):<20}")


async def main():
    """Run all tests."""
    print("🧪 IBAN ENRICHMENT TEST SUITE")
    print(f"Testing IBAN: {TEST_IBAN}")

    try:
        # Test invalid IBAN first
        await test_invalid_iban()

        # Test free scenario
        await test_free_scenario()

        # Test paid scenario (if API key available)
        paid_result = await test_paid_scenario()

        # Compare if both worked
        if paid_result:
            await compare_results()

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
