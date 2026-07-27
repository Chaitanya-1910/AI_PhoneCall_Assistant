import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class WorkerPoolManager:
    """
    Manages the Auto-Scaling worker pools across different regions.
    Supports Queue Sharding to distribute AI workloads based on tenant priority
    and regional locality (e.g., EU tenants process in eu-central-1).
    """
    def __init__(self, primary_region: str, multi_region_enabled: bool):
        self.primary_region = primary_region
        self.multi_region_enabled = multi_region_enabled
        self.active_workers: Dict[str, int] = {} # Queue Name -> Worker Count
        
    def scale_queue(self, queue_name: str, target_workers: int):
        logger.info(f"Scaling {queue_name} queue to {target_workers} workers in region {self.primary_region}.")
        self.active_workers[queue_name] = target_workers
        # In a real environment, this makes an API call to Kubernetes to scale a Deployment replica count.
        
    def get_sharded_queue(self, tenant_id: str, region: str) -> str:
        """
        Calculates which celery/arq queue should process a background task 
        based on the tenant and region for strict data residency.
        """
        if not self.multi_region_enabled:
            return "default_queue"
            
        return f"queue_{region}_{hash(tenant_id) % 4}"
