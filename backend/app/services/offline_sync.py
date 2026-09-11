import time
from typing import List, Dict, Any
from pydantic import BaseModel
from app.core.logging import logger
from app.services.weather_provider import weather_provider


class SyncItem(BaseModel):
    latitude: float
    longitude: float
    location_name: str
    last_synced_timestamp: float


class SyncBatchRequest(BaseModel):
    device_id: str
    items: List[SyncItem]


class OfflineSyncModule:
    """
    Offline Synchronization Manager.
    Receives batch delta sync requests from mobile devices reconnecting to network.
    """

    async def sync_device_data(self, batch: SyncBatchRequest) -> Dict[str, Any]:
        logger.info(f"Processing offline sync batch from device '{batch.device_id}' with {len(batch.items)} locations.")
        synced_results = []

        for item in batch.items:
            weather = await weather_provider.get_weather(
                latitude=item.latitude,
                longitude=item.longitude,
                location_name=item.location_name,
                days=3,
                low_bandwidth=True
            )
            synced_results.append({
                "location_name": item.location_name,
                "synced_at": time.time(),
                "weather": weather.model_dump()
            })

        return {
            "status": "success",
            "device_id": batch.device_id,
            "synced_count": len(synced_results),
            "synced_data": synced_results
        }


offline_sync_module = OfflineSyncModule()
