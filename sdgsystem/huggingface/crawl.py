import requests
from huggingface_hub import HfApi, hf_hub_download
from typing import Optional, List, Dict, Any


class HFCrawler:
    """
    A simple wrapper client for interacting with Hugging Face datasets and metadata.
    """

    BASE_URL = "https://datasets-server.huggingface.co"

    def __init__(self, hf_token):
        self.api = HfApi(token=hf_token)

    # -------------------------------
    # Dataset Search & Metadata
    # -------------------------------
    def search_datasets(self, query: str, limit: int) -> List[Any]:
        """
        Search for datasets on Hugging Face Hub by query keyword.
        Results are filtered to JSON datasets and sorted by downloads.
        """
        try:
            datasets = list(
                self.api.list_datasets(
                    search=query,
                    filter="format:json",
                    sort="downloads"
                )
            )[:limit]
            return datasets
        except Exception as e:
            print(f"Error searching datasets with query '{query}': {e}")
            return []

    def get_readme(self, repo_id: str, repo_type: str = "dataset") -> str:
        """
        Download and return the README.md content of a dataset repository.
        """
        try:
            readme_path = hf_hub_download(
                repo_id=repo_id,
                repo_type=repo_type,
                filename="README.md"
            )
            with open(readme_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error fetching README for {repo_id}: {e}")
            return ""

    # -------------------------------
    # Dataset Server Endpoints
    # -------------------------------
    def get_splits(self, dataset: str, config: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve the available splits (train/test/validation) of a dataset.
        """
        try:
            url = f"{self.BASE_URL}/splits"
            params = {"dataset": dataset}
            if config:
                params["config"] = config

            resp = requests.get(url, params=params)
            resp.raise_for_status()
            return resp.json()["splits"]
        except Exception as e:
            print(f"Error fetching splits for dataset {dataset}: {e}")
            return []

    def get_first_rows(
        self,
        dataset: str,
        dataset_splits: List[Dict[str, Any]],
        sample_limit: int
    ) -> Dict[str, Any]:
        """
        Get the first few rows of a dataset split.
        """
        try:
            first_split = dataset_splits[0]["split"]
            first_config = dataset_splits[0]["config"]
            url = f"{self.BASE_URL}/first-rows"
            params = {"dataset": dataset, "split": first_split, "config": first_config}

            resp = requests.get(url, params=params)
            resp.raise_for_status()
            return resp.json()["rows"][:sample_limit]
        except Exception as e:
            print(f"Error fetching first rows for dataset {dataset}: {e}")
            return []

    def get_info(self, dataset: str, config: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve dataset information and metadata.
        """
        try:
            url = f"{self.BASE_URL}/info"
            params = {"dataset": dataset}
            if config:
                params["config"] = config

            resp = requests.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error fetching info for dataset {dataset}: {e}")
            return {}

