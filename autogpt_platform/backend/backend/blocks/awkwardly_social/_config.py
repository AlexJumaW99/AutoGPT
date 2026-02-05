"""
Configuration for the Awkwardly Social block.
"""

from backend.sdk import BlockCostType, ProviderBuilder

# Define the provider for the social scraper
# This handles the API Key credential injection automatically
social_scraper_config = (
    ProviderBuilder("social_scraper")
    .with_api_key(
        api_key_env_var="SOCIAL_SCRAPER_API_KEY",
        title="Social Scraper API Key"
    )
    .with_base_cost(1, BlockCostType.RUN)
    .build()
)