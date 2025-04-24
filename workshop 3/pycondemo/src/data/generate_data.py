import random
import uuid
from datetime import datetime, timedelta

CLOUD_PROVIDERS = {
    "AWS": {
        "instance_types": [
            "t3.micro",
            "t3.medium",
            "m5.large",
            "m5.xlarge",
            "c5.large",
            "r5.large",
        ],
        "regions": ["us-east-1", "us-west-2", "eu-central-1"],
    },
    "Azure": {
        "instance_types": [
            "Standard_B1s",
            "Standard_D2s_v3",
            "Standard_E4s_v3",
            "Standard_F4s",
        ],
        "regions": ["eastus", "westeurope", "southeastasia"],
    },
    "GCP": {
        "instance_types": [
            "e2-medium",
            "n1-standard-2",
            "n2-highmem-4",
            "c2-standard-4",
        ],
        "regions": ["us-central1", "europe-west1", "asia-southeast1"],
    },
}


def random_timestamp(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )


def generate_node_metadata(index):
    provider = random.choice(list(CLOUD_PROVIDERS.keys()))
    instance_type = random.choice(CLOUD_PROVIDERS[provider]["instance_types"])
    region = random.choice(CLOUD_PROVIDERS[provider]["regions"])

    base_time = datetime.now() - timedelta(days=random.randint(1, 30))
    created = base_time
    interrupted = None
    deleted = None

    if random.random() < 0.4:
        interrupted = created + timedelta(minutes=random.randint(5, 100))
    if random.random() < 0.6:
        deleted = created + timedelta(minutes=random.randint(10, 200))

    is_spot = random.choice([True, False])  # Simulates mixed capacity

    return {
        "id": uuid.uuid4().__str__(),
        "name": f"{provider.lower()}-node-{index:04d}",
        "cloud": provider,
        "instance_type": instance_type,
        "region": region,
        "created_at": created,
        "interrupted_at": interrupted,
        "deleted_at": deleted,
        "is_spot": is_spot,
        "cpu_count": random.choice([2, 4, 8, 16]),
        "memory_gb": random.choice([4, 8, 16, 32, 64]),
        "event_timestamp": datetime.now(),
    }
