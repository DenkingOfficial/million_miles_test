import asyncio
import aiohttp
import logging
from typing import Dict, List, Set
from datetime import datetime
from dataclasses import dataclass
import uuid

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    session_id: str
    total_cars_found: int
    new_cars: List[Dict]
    updated_cars: List[Dict]
    removed_car_ids: Set[str]
    duration_seconds: float
    error_message: str = None


class EncarAPI:
    BASE_URL = "https://api.encar.com/search/car/list"

    def _setup_headers(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
            "Cache-Control": "no-cache",
            "Origin": "https://www.encar.com",
            "Pragma": "no-cache",
            "Referer": "https://www.encar.com/",
            "Sec-Ch-Ua": '"Not=A?Brand";v="24", "Chromium";v="140"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
        logger.debug(f"🔧 Setup headers: {len(headers)} headers configured")
        return headers

    async def search_premium_async(
        self,
        session,
        page=0,
        limit=500,
        sort_option="PriceAsc",
        query="q=(Or.CarType.N._.CarType.Y.)",
        include_count=True,
    ):
        base_url = f"{self.BASE_URL}/premium"
        url_parts = []

        if include_count:
            url_parts.append("count=true")
        url_parts.append(query)

        offset = page * limit
        url_parts.append(f"sr=|{sort_option}|{offset}|{limit}")

        url = f"{base_url}?{'&'.join(url_parts)}"
        
        logger.debug(f"Making request to: {url}")

        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                
                search_results = data.get("SearchResults", [])
                total_count = data.get("Count", 0)
                
                logger.debug(f"API Response - Page {page}: {len(search_results)} cars, Total: {total_count}")
                
                return data, query, sort_option, page, limit
                
        except Exception as e:
            logger.error(f"API Request failed - Page {page}, Sort: {sort_option}, Query: {query[:30]}...: {e}")
            raise


class EncarParser:
    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
        self.api = EncarAPI()

        self.queries = [
            ("q=(And.Hidden.N._.CarType.N.)", "Hidden_N_CarType_N"),
            ("q=(And.Hidden.Y._.CarType.N.)", "Hidden_Y_CarType_N"),
            ("q=(And.Hidden.N._.CarType.Y.)", "Hidden_N_CarType_Y"),
            ("q=(And.Hidden.Y._.CarType.Y.)", "Hidden_Y_CarType_Y"),
            ("q=(Or.CarType.N._.CarType.Y.)", "Or_CarType_N_Y"),
            ("q=(Or.CarType.Y._.CarType.N.)", "Or_CarType_Y_N"),
        ]

        self.sort_options = [
            "ModifiedDate",
            "PriceAsc",
            "PriceDesc",
            "MileageAsc",
            "MileageDesc",
            "Year",
        ]
        self.page_sizes = [500, 400, 300, 200, 100, 50, 20]
        
        logger.info(f"Parser initialized:")
        logger.info(f"   Queries: {len(self.queries)}")
        logger.info(f"   Sort options: {len(self.sort_options)}")
        logger.info(f"   Page sizes: {len(self.page_sizes)}")
        logger.info(f"   Total configurations: {len(self.queries) * len(self.sort_options) * len(self.page_sizes)}")
        logger.info(f"   Max concurrent: {max_concurrent}")

    def normalize_car_data(self, car_data):
        normalized = {
            "encar_id": str(car_data.get("Id", "")),
            "manufacturer": car_data.get("Manufacturer", ""),
            "model": car_data.get("Model", ""),
            "badge": car_data.get("Badge", ""),
            "badge_detail": car_data.get("BadgeDetail", ""),
            "transmission": car_data.get("Transmission", ""),
            "fuel_type": car_data.get("FuelType", ""),
            "year": car_data.get("Year"),
            "form_year": car_data.get("FormYear", ""),
            "mileage": car_data.get("Mileage"),
            "price": car_data.get("Price"),
            "separation": car_data.get("Separation", []),
            "trust": car_data.get("Trust", []),
            "service_mark": car_data.get("ServiceMark", []),
            "condition": car_data.get("Condition", []),
            "photo": car_data.get("Photo", ""),
            "photos": car_data.get("Photos", []),
            "service_copy_car": car_data.get("ServiceCopyCar", ""),
            "sales_status": car_data.get("SalesStatus", ""),
            "sell_type": car_data.get("SellType", ""),
            "buy_type": car_data.get("BuyType", []),
            "powerpack": car_data.get("Powerpack", ""),
            "ad_words": car_data.get("AdWords", ""),
            "hotmark": car_data.get("Hotmark", ""),
            "office_city_state": car_data.get("OfficeCityState", ""),
            "office_name": car_data.get("OfficeName", ""),
            "dealer_name": car_data.get("DealerName", ""),
        }

        modified_date_str = car_data.get("ModifiedDate", "")
        if modified_date_str:
            try:
                if "+" in modified_date_str:
                    date_part = modified_date_str.split("+")[0].strip()
                elif "-" in modified_date_str[-3:]:
                    date_part = modified_date_str.split("-")[:-1]
                    date_part = "-".join(date_part).strip()
                else:
                    date_part = modified_date_str.strip()

                if "." in date_part:
                    date_part = date_part.split(".")[0]

                normalized["modified_date"] = datetime.strptime(
                    date_part, "%Y-%m-%d %H:%M:%S"
                )
            except Exception as e:
                logger.warning(f"Failed to parse date '{modified_date_str}' for car {normalized['encar_id']}: {e}")
                normalized["modified_date"] = None
        else:
            normalized["modified_date"] = None

        return normalized

    async def search_single_config_async(
        self, query_param, query_name, sort_option, page_size, session
    ):
        config_name = f"{query_name}_{sort_option}_{page_size}"
        logger.info(f"Starting config: {config_name}")
        
        all_cars = []
        page = 0
        consecutive_failures = 0
        consecutive_empty_pages = 0
        consecutive_duplicate_pages = 0
        last_page_signature = None
        estimated_max_pages = min(80, (20000 // page_size) + 10)
        
        logger.debug(f"Config {config_name} - Max pages: {estimated_max_pages}")

        while (
            consecutive_failures < 3
            and consecutive_empty_pages < 3
            and consecutive_duplicate_pages < 2
            and page < estimated_max_pages
        ):
            try:
                logger.debug(f"{config_name} - Fetching page {page}")
                
                data, _, _, _, _ = await self.api.search_premium_async(
                    session, page, page_size, sort_option, query_param
                )

                search_results = data.get("SearchResults", [])

                if not search_results:
                    consecutive_empty_pages += 1
                    logger.debug(f"{config_name} - Empty page {page} (consecutive: {consecutive_empty_pages})")
                    page += 1
                    continue

                consecutive_empty_pages = 0
                consecutive_failures = 0

                first_id = search_results[0].get("Id")
                last_id = search_results[-1].get("Id")
                page_signature = f"{first_id}-{last_id}-{len(search_results)}"

                if page_signature == last_page_signature:
                    consecutive_duplicate_pages += 1
                    logger.debug(f"{config_name} - Duplicate page {page} (consecutive: {consecutive_duplicate_pages})")
                else:
                    consecutive_duplicate_pages = 0
                    last_page_signature = page_signature

                cars_added = 0
                for car in search_results:
                    normalized_car = self.normalize_car_data(car)
                    if normalized_car["encar_id"]:
                        all_cars.append(normalized_car)
                        cars_added += 1

                logger.debug(f"{config_name} - Page {page}: {cars_added} cars added (total: {len(all_cars)})")
                
                if page % 10 == 0 and page > 0:
                    logger.info(f"{config_name} - Progress: {page} pages, {len(all_cars)} cars")

                page += 1
                await asyncio.sleep(0.03)

            except Exception as e:
                consecutive_failures += 1
                logger.error(f"{config_name} - Page {page} failed (consecutive: {consecutive_failures}): {e}")
                page += 1

        logger.info(f"{config_name} completed: {len(all_cars)} cars from {page} pages")
        return all_cars, config_name

    async def parse_all_configurations(self):
        session_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        logger.info(f"Starting parse session: {session_id}")
        logger.info(f"Start time: {start_time}")

        try:
            headers = self.api._setup_headers()
            connector = aiohttp.TCPConnector(
                limit=self.max_concurrent, limit_per_host=self.max_concurrent
            )
            timeout = aiohttp.ClientTimeout(total=30)
            
            logger.info(f"HTTP session configured - Concurrent limit: {self.max_concurrent}")

            all_current_cars = {}
            completed_configs = 0
            total_configs = len(self.queries) * len(self.sort_options) * len(self.page_sizes)

            async with aiohttp.ClientSession(
                headers=headers, connector=connector, timeout=timeout
            ) as session:
                logger.info(f"HTTP session started")
                
                tasks = []
                for query_param, query_name in self.queries:
                    for sort_option in self.sort_options:
                        for page_size in self.page_sizes:
                            task = self.search_single_config_async(
                                query_param, query_name, sort_option, page_size, session
                            )
                            tasks.append(task)

                logger.info(f"Created {len(tasks)} configuration tasks")
                logger.info(f"Starting parallel execution...")

                batch_size = min(self.max_concurrent, 20)
                
                for i in range(0, len(tasks), batch_size):
                    batch = tasks[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    total_batches = (len(tasks) + batch_size - 1) // batch_size
                    
                    logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} configs)")
                    
                    try:
                        results = await asyncio.gather(*batch, return_exceptions=True)
                        
                        for result in results:
                            completed_configs += 1
                            
                            if isinstance(result, Exception):
                                logger.error(f"Config failed: {result}")
                                continue

                            cars, config_name = result
                            
                            new_in_config = 0
                            for car in cars:
                                car_id = car["encar_id"]
                                if car_id and car_id not in all_current_cars:
                                    all_current_cars[car_id] = car
                                    new_in_config += 1
                            
                            logger.info(f"📊 {config_name}: {len(cars)} total, {new_in_config} unique")
                            
                            if completed_configs % 10 == 0:
                                elapsed = (datetime.now() - start_time).total_seconds()
                                progress = (completed_configs / total_configs) * 100
                                logger.info(f"Progress: {completed_configs}/{total_configs} ({progress:.1f}%) - {len(all_current_cars)} unique cars - {elapsed:.1f}s elapsed")
                        
                        if i + batch_size < len(tasks):
                            await asyncio.sleep(1)
                            
                    except Exception as e:
                        logger.error(f"Batch {batch_num} failed: {e}")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Parse session completed!")
            logger.info(f"Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
            logger.info(f"Total unique cars found: {len(all_current_cars)}")
            logger.info(f"Configurations completed: {completed_configs}/{total_configs}")
            logger.info(f"Average speed: {len(all_current_cars)/duration:.1f} cars/second")

            return ParseResult(
                session_id=session_id,
                total_cars_found=len(all_current_cars),
                new_cars=list(all_current_cars.values()),
                updated_cars=[],
                removed_car_ids=set(),
                duration_seconds=duration,
            )

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"Parse session failed after {duration:.2f} seconds: {e}", exc_info=True)

            return ParseResult(
                session_id=session_id,
                total_cars_found=0,
                new_cars=[],
                updated_cars=[],
                removed_car_ids=set(),
                duration_seconds=duration,
                error_message=str(e),
            )