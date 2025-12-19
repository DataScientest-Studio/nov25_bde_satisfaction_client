# File: src\etl\utils\http_client.py

"""
Module pour la gestion d'un client HTTP asynchrone unique basé sur 'httpx.AsyncClient'.

Ce module permet de créer un client HTTP unique (Singleton) qui peut être utilisé pour effectuer des requêtes HTTP 
asynchrones. Il fournit une méthode pour récupérer le client et une méthode pour le fermer proprement.

Le client utilise HTTP/2 et possède des en-têtes par défaut pour l'acceptation de contenu, la langue et l'agent utilisateur.
"""

from httpx import AsyncClient
from loguru import logger
from typing import Optional


class HttpClient:
    """Classe pour gérer un client HTTP asynchrone unique (Singleton)."""

    _client: Optional[AsyncClient] = None

    @classmethod
    def get_client(cls) -> AsyncClient:
        """
        Retourne le client HTTP asynchrone unique (Singleton). Si le client n'existe pas, il est créé.

        Cette méthode crée une instance d''AsyncClient' si elle n'existe pas déjà et la retourne. L'instance utilise 
        HTTP/2 et des en-têtes personnalisés pour les requêtes HTTP, avec un délai d'attente de 30 secondes par défaut.

        Parameters
        --------
        AsyncClient
            L'instance de 'AsyncClient' utilisée pour effectuer les requêtes HTTP.

        Raises
        -----
        Exception
            Si une erreur se produit lors de la création du client HTTP.
        """
        if cls._client is None:
            try:
                logger.info("Création du client AsyncClient...")
                cls._client = AsyncClient(
                    http2=True,
                    headers={
                        "accept-language": "fr-FR,fr;q=0.9",
                        "user-agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/96.0.4664.110 Safari/537.36"
                        ),
                        "accept": (
                            "text/html,application/xhtml+xml,application/xml;q=0.9,"
                            "image/webp,image/apng,*/*;q=0.8"
                        ),
                        "accept-encoding": "gzip, deflate, br",
                    },
                    timeout=30.0,
                )
                logger.success("Client AsyncClient créé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la création du client HTTP : {e}")
                raise
        return cls._client

    @classmethod
    async def close(cls) -> None:
        """
        Ferme proprement le client HTTP unique (Singleton).

        Cette méthode ferme l'instance 'AsyncClient' active, libérant ainsi les ressources utilisées. Si aucune instance 
        n'est présente, cette méthode ne fait rien. Si une erreur survient lors de la fermeture du client, elle est loggée.

        Lève:
        -----
        Exception
            Si une erreur se produit lors de la fermeture du client HTTP.
        """
        if cls._client:
            try:
                logger.info("Fermeture du client AsyncClient...")
                await cls._client.aclose()
                logger.success("Client AsyncClient fermé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture du client HTTP : {e}")
                raise
            finally:
                cls._client = None
