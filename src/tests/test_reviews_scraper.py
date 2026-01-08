# File: src\tests\test_reviews_scraper.py

"""
Test de l'accessibilité de l'URL.

Ce test effectue une requête HTTP GET sur l'URL d'une entreprise
pour vérifier si la page est accessible (statut HTTP 200).
"""

import pytest
import aiohttp


@pytest.mark.asyncio
async def test_trustpilot_url():
    # URL à tester
    enterprise_url = "www.showroomprive.com"
    url_base = f"https://www.trustpilot.com/review/{enterprise_url}"
    
    # Effectuer une requête HTTP GET à l'URL
    async with aiohttp.ClientSession() as session:
        async with session.get(url_base) as response:
            # Vérifier si la requête est réussie (statut HTTP 200)
            assert response.status == 200
