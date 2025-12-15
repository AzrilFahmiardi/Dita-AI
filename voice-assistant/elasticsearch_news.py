import os
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from config_manager import get_elasticsearch_config, get_news_config
import dateutil.parser
from dotenv import load_dotenv

load_dotenv()


class NewsQueryProcessor:
    """Process user queries for Elasticsearch search"""
    def __init__(self):
        self.temporal_patterns = {
            r'\bhari ini\b': 'today',
            r'\bkemarin\b': 'yesterday', 
            r'\bminggu lalu\b': 'last_week',
            r'\bminggu ini\b': 'this_week',
            r'\bbulan lalu\b': 'last_month',
            r'\bbulan ini\b': 'this_month',
            r'\bterbaru\b': 'latest',
            r'\bsekarang\b': 'now'
        }
    
    
    def extract_temporal_filter(self, query: str) -> Optional[Dict]:
        """Extract date range from query"""
        query_lower = query.lower()
        
        for pattern, period in self.temporal_patterns.items():
            if re.search(pattern, query_lower):
                return self._get_date_range(period)
        
        return None
    
    def _get_date_range(self, period: str) -> Dict:
        """Convert period to Elasticsearch date range"""
        now = datetime.now()
        
        if period == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == 'yesterday':
            yesterday = now - timedelta(days=1)
            start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == 'last_week':
            start = now - timedelta(days=7)
            end = now
        elif period == 'this_week':
            start = now - timedelta(days=now.weekday())
            end = now
        elif period == 'last_month':
            start = now - timedelta(days=30)
            end = now
        elif period == 'this_month':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period in ['latest', 'now']:
            start = now - timedelta(hours=24)  # Last 24 hours
            end = now
        else:
            start = now - timedelta(days=7)  # Default: last week
            end = now
        
        return {
            "gte": start.isoformat(),
            "lte": end.isoformat()
        }
    
    def clean_query(self, query: str) -> str:
        """Remove temporal markers and clean query for search"""
        cleaned = query.lower()
        
        # Remove temporal patterns
        for pattern in self.temporal_patterns.keys():
            cleaned = re.sub(pattern, '', cleaned)
        
        # Remove common stopwords
        stopwords = ['apa', 'ada', 'yang', 'dari', 'di', 'ke', 'untuk', 'tentang', 'dengan']
        words = cleaned.split()
        words = [word for word in words if word not in stopwords and len(word) > 2]
        
        return ' '.join(words).strip()


class ElasticsearchNewsRAG:
    """News search with Elasticsearch"""
    
    def __init__(self):
        self.config = get_elasticsearch_config()
        self.news_config = get_news_config()
        self.query_processor = NewsQueryProcessor()
        
        # Configuration
        self.vpn_mode = os.getenv('VPN_MODE', 'false').lower() == 'true'
        self.timeout = int(os.getenv('ES_TIMEOUT', str(self.config.get('timeout', 20))))
        self.max_retries = int(os.getenv('ES_MAX_RETRIES', str(self.config.get('max_retries', 3))))
        self.request_interval = float(os.getenv('ES_REQUEST_INTERVAL', '0.5'))
        
        # Request throttling to prevent VPN overload
        self._last_request_time = 0
        
        # Initialize Elasticsearch client
        es_host = self.config.get('host', 'localhost')
        es_port = self.config.get('port', 9200)
        es_url = f"http://{es_host}:{es_port}"
        
        self.es_client = Elasticsearch(
            es_url,
            basic_auth=(
                self.config.get('username', 'elastic'),
                self.config.get('password', '')
            ),
            request_timeout=self.timeout,
            retry_on_timeout=self.config.get('retry_on_timeout', True),
            max_retries=self.max_retries,
            http_compress=self.config.get('http_compress', self.vpn_mode),
            verify_certs=not self.vpn_mode
        )
        
        self.index_name = self.news_config.get('index_name')
        self.keyword_filter = self.news_config.get('keyword_filter')
        
        if self.vpn_mode:
            print(f"VPN mode enabled: timeout={self.timeout}s, retries={self.max_retries}, interval={self.request_interval}s")
      
        connection_result = self.test_connection()
        self.es_available = connection_result['status'] == 'connected'
        
        if self.es_available:
            print(f"Elasticsearch connection successful")
        else:
            print(f"Elasticsearch connection error: {connection_result.get('error', 'Unknown error')}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Elasticsearch connection and return cluster info"""
        try:
            self._throttle_request()
            
            connection_start = time.time()
            
            cluster_info = self.es_client.info()
            
            index_exists = self.es_client.indices.exists(index=self.index_name)
            
            connection_duration = time.time() - connection_start
            
            if self.vpn_mode:
                print(f"Connection test completed in {connection_duration:.2f}s")
            
            # Get sample documents count
            if index_exists:
                count_response = self.es_client.count(index=self.index_name)
                doc_count = count_response['count']
            else:
                doc_count = 0
                
            return {
                "status": "connected" if index_exists else "failed",
                "cluster_name": cluster_info.get('cluster_name', 'unknown'),
                "version": cluster_info.get('version', {}).get('number', 'unknown'),
                "index_exists": index_exists,
                "document_count": doc_count,
                "host": self.config.get('host'),
                "index": self.index_name,
                "error": "Index not found" if not index_exists else None
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def search_news(self, query: str) -> List[Dict]:
        """Main news search function"""
        if not self.es_available:
            print("Elasticsearch not available")
            return []
        
        try:
            self._throttle_request()
            
            # Process query
            temporal_filter = self.query_processor.extract_temporal_filter(query)
            clean_query = self.query_processor.clean_query(query)
            
            if not clean_query.strip():
                clean_query = query  # Use original query if cleaning removes everything
            
            print(f"Searching news for: '{query}' -> clean: '{clean_query}'")
            if temporal_filter:
                print(f"Temporal filter: {temporal_filter}")
            
            # Build Elasticsearch query
            search_body = self._build_search_query(clean_query, temporal_filter)
            
            # Execute search with timing
            search_start = time.time()
            response = self.es_client.search(
                index=self.index_name,
                body=search_body
            )
            search_duration = time.time() - search_start
            
            if self.vpn_mode:
                print(f"Search completed in {search_duration:.2f}s")
            
            # Check if we got results
            hits = response['hits']['hits']
            
            # If no results with temporal filter, try without it for "terbaru/latest" queries
            if not hits and temporal_filter and self._is_latest_query(query):
                print("No results with temporal filter, trying without time restriction...")
                
                # Throttle before retry
                self._throttle_request()
                
                search_body_no_time = self._build_search_query(clean_query, None)
                retry_start = time.time()
                response = self.es_client.search(
                    index=self.index_name,
                    body=search_body_no_time
                )
                retry_duration = time.time() - retry_start
                
                if self.vpn_mode:
                    print(f"Retry search completed in {retry_duration:.2f}s")
                
                hits = response['hits']['hits']
                if hits:
                    print(f"Found {len(hits)} results without temporal filter")
            
            # Process results
            results = self._process_search_results(response, query)
            
            if results:
                print(f"Found {len(results)} news articles")
            else:
                print(f"No news found for query: {query}")
            
            return results
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Elasticsearch search error: {e}")
            
            # Log if error might be VPN-related
            if any(keyword in error_msg for keyword in ['timeout', 'connection', 'refused', 'unreachable']):
                print("Warning: Possible VPN connection issue detected")
                print("Suggestion: Check VPN status and connection stability")
            
            return []
    
    def _is_latest_query(self, query: str) -> bool:
        """Check if query asks for latest/recent news using existing temporal patterns"""
        # Use patterns from query processor that indicate "latest" intent
        latest_temporal_types = ['latest', 'now']
        query_lower = query.lower()
        
        # Check against existing temporal patterns
        for pattern, period in self.query_processor.temporal_patterns.items():
            if period in latest_temporal_types and re.search(pattern, query_lower):
                return True

        # Check for additional latest indicators not in temporal patterns
        additional_latest_patterns = [r'\bterkini\b', r'\bbaru\b']
        return any(re.search(pattern, query_lower) for pattern in additional_latest_patterns)
    
    def _build_search_query(self, query: str, temporal_filter: Optional[Dict]) -> Dict:
        """Build Elasticsearch query"""
        
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "title^3",
                                    "summary^2",
                                    "fulltext^1"
                                ],
                                "type": "best_fields",
                                "fuzziness": "AUTO",
                                "prefix_length": 2,
                                "max_expansions": 50,
                                "minimum_should_match": "75%"
                            }
                        }
                    ]
                }
            },
            "min_score": 0.5,
            "sort": [
                {"published": {"order": "desc"}},
                {"_score": {"order": "desc"}}
            ],
            "size": self.news_config.get('max_results', 5),
            "_source": ["title", "summary", "fulltext", "published", "site"]
        }
        
        # Add temporal filter if present
        if temporal_filter:
            search_body["query"]["bool"]["filter"] = [{
                "range": {
                    "published": temporal_filter
                }
            }]
        
        return search_body
    
    def _throttle_request(self):
        """Throttle requests to prevent VPN overload"""
        if not self.vpn_mode or self.request_interval <= 0:
            return
        
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.request_interval:
            sleep_time = self.request_interval - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _process_search_results(self, response: Dict, original_query: str) -> List[Dict]:
        """Process Elasticsearch results into structured format"""
        hits = response.get('hits', {}).get('hits', [])
        
        if not hits:
            print(f"No news found for query: {original_query}")
            return []
        
        processed_results = []
        for hit in hits:
            source = hit['_source']
            
            # Extract and format data
            result = {
                'headline': source.get('title', 'Tidak ada judul'),
                'summary': source.get('summary', ''),
                'fulltext': source.get('fulltext', ''),
                'tanggal': source.get('published', ''),
                'source': source.get('site', 'Tidak diketahui'),
                'score': hit['_score'],
                'relevance': self._calculate_relevance(hit, original_query)
            }
            
            # Limit summary length
            max_summary_length = self.news_config.get('summary_max_length', 300)
            if len(result['summary']) > max_summary_length:
                result['summary'] = result['summary'][:max_summary_length] + '...'
            
            processed_results.append(result)
        
        print(f"Found {len(processed_results)} news articles")
        return processed_results
    
    def _calculate_relevance(self, hit: Dict, query: str) -> float:
        """Calculate custom relevance score"""
        base_score = hit['_score']
        
        # Boost recent articles
        try:
            article_date = dateutil.parser.parse(hit['_source'].get('published', ''))
            days_old = (datetime.now() - article_date.replace(tzinfo=None)).days
            recency_boost = max(0, 1 - (days_old / 30))  # Boost recent articles
            
            return base_score * (1 + recency_boost)
        except:
            return base_score