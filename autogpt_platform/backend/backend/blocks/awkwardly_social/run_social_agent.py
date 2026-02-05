import sys
import os
import asyncio

# --- Path Setup (unchanged) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ------------------------------

from backend.sdk import APIKeyCredentials
from backend.blocks.awkwardly_social.awkwardly_social import SocialMediaScraperBlock

async def main():
    print("--- Starting Social Media Agent (Sibling Mode) ---")

    # 1. Initialize
    block = SocialMediaScraperBlock()

    # 2. Mock Inputs
    # Note: We do NOT pass credentials here in the Input object for the SDK.
    # Credentials are passed separately in the run() method.
    input_data = SocialMediaScraperBlock.Input(
        target_urls=["https://twitter.com/example", "https://reddit.com/r/example"],
        platforms=["X", "Reddit"],
        max_posts=5,
        include_comments=True
    )

    # 3. Mock Credentials
    # This matches the APIKeyCredentials expected by the Block
    mock_creds = APIKeyCredentials(
        api_key=os.getenv("SOCIAL_SCRAPER_API_KEY", "AIzaSyB-0o6TlEIf6FQtZrbdSiO1uxyCmoeRkp0") 
    )

    # 4. Run
    try:
        async for output_name, output_value in block.run(input_data, credentials=mock_creds):
            if "csv" in output_name:
                print(f"\n[OUTPUT] {output_name} (preview):")
                preview_len = min(len(output_value), 150)
                print(output_value[:preview_len] + "...")
            else:
                print(f"\n[METADATA] {output_name}: {output_value}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())