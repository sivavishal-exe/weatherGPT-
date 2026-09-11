import pytest
import time
from app.services.offline_sync import offline_sync_module, SyncBatchRequest, SyncItem


@pytest.mark.asyncio
async def test_offline_sync_batch():
    batch = SyncBatchRequest(
        device_id="mobile-dev-001",
        items=[
            SyncItem(latitude=35.6762, longitude=139.6503, location_name="Tokyo", last_synced_timestamp=time.time() - 3600)
        ]
    )
    res = await offline_sync_module.sync_device_data(batch)
    assert res["status"] == "success"
    assert res["synced_count"] == 1
    assert res["device_id"] == "mobile-dev-001"
