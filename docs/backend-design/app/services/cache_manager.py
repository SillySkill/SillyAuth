# ============================================
# SillyMD Backend - Search Service
# ============================================

from meilisearch import Client
from app.core.config import settings
from typing import Dict, List


class SearchService:
    """Meilisearch service"""

    def __init__(self):
        self.client = None
        self.index_name = "skills"

    async def initialize(self):
        """Initialize Meilisearch"""
        try:
            self.client = Client(
                settings.MEILISEARCH_URL,
                settings.MEILISEARCH_MASTER_KEY
            )

            # Configure index
            self._setup_index()
        except Exception as e:
            print(f"Failed to initialize Meilisearch: {e}")

    def _setup_index(self):
        """Setup search index"""
        if not self.client:
            return

        index_settings = {
            'searchableAttributes': [
                'name', 'description', 'tags', 'author_name'
            ],
            'filterableAttributes': [
                'category', 'type', 'status'
            ],
            'sortableAttributes': [
                'rating_avg', 'download_count', 'created_at'
            ],
            'rankingRules': [
                'words',
                'typo',
                'proximity',
                'attribute',
                'sort',
                'exactness',
                'download_count:desc'
            ],
            'stopWords': [
                'the', 'a', 'an', 'and', 'or',
                '的', '了', '是', '在', '和'
            ]
        }

        try:
            index = self.client.index(self.index_name)
            index.update_settings(index_settings)
        except Exception as e:
            print(f"Failed to setup Meilisearch index: {e}")

    async def index_skill(self, skill: Dict):
        """Index a single skill"""
        if not self.client:
            return

        try:
            index = self.client.index(self.index_name)
            index.add_documents([{
                'id': skill['id'],
                'skill_id': skill.get('skill_id'),
                'name': skill.get('name'),
                'description': skill.get('description'),
                'category': skill.get('category'),
                'type': skill.get('type'),
                'status': skill.get('status'),
                'rating_avg': skill.get('rating_avg', 0),
                'download_count': skill.get('download_count', 0),
                'created_at': skill.get('created_at')
            }])
        except Exception as e:
            print(f"Failed to index skill: {e}")

    async def search(
        self,
        query: str,
        category: str = None,
        type: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """Search skills"""
        if not self.client:
            return []

        try:
            index = self.client.index(self.index_name)

            search_params = {
                'limit': limit
            }

            # Add filters
            filters = []
            if category:
                filters.append(f'category = {category}')
            if type:
                filters.append(f'type = {type}')

            if filters:
                search_params['filter'] = ' AND '.join(filters)

            results = index.search(query, search_params)
            return results.get('hits', [])
        except Exception as e:
            print(f"Search failed: {e}")
            return []


# Create service instance
search_service = SearchService()
