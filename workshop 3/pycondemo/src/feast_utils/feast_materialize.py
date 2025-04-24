import os
from datetime import UTC, datetime, timedelta

from feast import FeatureStore

store = FeatureStore(repo_path=os.environ["FEAST_REPO_PATH"])
end_time = datetime.now(UTC)
start_time = end_time - timedelta(days=7)

store.materialize(start_date=start_time, end_date=end_time)
