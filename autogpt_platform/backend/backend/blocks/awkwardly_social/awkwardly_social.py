import uuid
import csv
import io
from typing import Any, List, Dict

from backend.sdk import (
    APIKeyCredentials,
    Block,
    BlockCategory,
    BlockOutput,
    BlockSchemaInput,
    BlockSchemaOutput,
    CredentialsMetaInput,
    SchemaField,
)

from ._config import social_scraper_config
from ._api import SocialMediaClient

class SocialMediaScraperBlock(Block):
    """
    Scrapes popular social media sites (Facebook, X, Reddit, Youtube, Bluesky)
    and returns structured CSV data for Users, Posts, and Comments.
    """

    class Input(BlockSchemaInput):
        credentials: CredentialsMetaInput = social_scraper_config.credentials_field(
            description="API credentials for the Social Scraper"
        )
        target_urls: list[str] = SchemaField(
            description="List of social media URLs to visit",
            default=[]
        )
        platforms: list[str] = SchemaField(
            description="Platforms to target. Leave empty to auto-detect.",
            default=["Facebook", "X", "Reddit", "Youtube", "Bluesky"]
        )
        max_posts: int = SchemaField(
            description="Maximum number of posts to scrape per URL", 
            default=10,
            ge=1,
            le=100
        )
        include_comments: bool = SchemaField(
            description="Whether to extract comments for found posts",
            default=True
        )

    class Output(BlockSchemaOutput):
        users_csv: str = SchemaField(
            description="CSV string containing user details"
        )
        posts_csv: str = SchemaField(
            description="CSV string containing post details"
        )
        comments_csv: str = SchemaField(
            description="CSV string containing comment details"
        )
        total_items_scraped: int = SchemaField(
            description="Total count of posts and comments processed"
        )

    def __init__(self):
        super().__init__(
            id=str(uuid.uuid4()),
            description="Scrape social media and output relational CSV datasets",
            categories={BlockCategory.SEARCH, BlockCategory.DATA},
            input_schema=self.Input,
            output_schema=self.Output,
            test_input={
                "credentials": social_scraper_config.get_test_credentials().model_dump(),
                "target_urls": ["https://twitter.com/example"],
                "platforms": ["X"],
                "max_posts": 2,
                "include_comments": False
            },
            test_credentials=social_scraper_config.get_test_credentials(),
            test_output=[
                ("total_items_scraped", 3), # 1 user + 2 posts (based on mock)
            ],
            # Mocking the client method for internal tests if needed
            test_mock={
                "scrape_social_media": lambda *args, **kwargs: {
                    "users": [{"user_id": "u1", "username": "test_user"}],
                    "posts": [{"post_id": "p1", "content_text": "test post"}],
                    "comments": []
                }
            }
        )

    async def run(
        self, 
        input_data: Input, 
        *, 
        credentials: APIKeyCredentials,
        **kwargs
    ) -> BlockOutput:
        try:
            # 1. Initialize Client with Credentials
            client = SocialMediaClient(credentials)

            # 2. Scrape the data using the client
            data = await client.scrape_social_media(
                input_data.target_urls, 
                input_data.max_posts,
                input_data.include_comments
            )

            # 3. Convert structured data to CSV format
            users_csv = self.generate_csv(
                data['users'], 
                ['user_id', 'username', 'platform', 'profile_details']
            )
            
            posts_csv = self.generate_csv(
                data['posts'], 
                ['post_id', 'user_id', 'platform', 'timestamp', 'content_text']
            )
            
            comments_csv = self.generate_csv(
                data['comments'], 
                ['comment_id', 'post_id', 'user_id', 'timestamp', 'content_text']
            )

            # 4. Yield outputs
            yield "users_csv", users_csv
            yield "posts_csv", posts_csv
            yield "comments_csv", comments_csv
            yield "total_items_scraped", len(data['posts']) + len(data['comments'])

        except Exception as e:
            yield "error", str(e)

    def generate_csv(self, data_list: list[dict], fieldnames: list[str]) -> str:
        """Helper to convert list of dicts to a CSV string."""
        if not data_list:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in data_list:
            filtered_row = {k: row.get(k, "") for k in fieldnames}
            writer.writerow(filtered_row)
            
        return output.getvalue()