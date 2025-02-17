import json
import os
import pandas as pd
import requests
from typing import Union, List
from PIL import Image
from io import BytesIO

class ZaraDBAPI:
    def __init__(self, base_path: str = 'kaggle/zara_database'):
        """
        Initialize the API with a base path for the database.
        :param base_path: Path to the database folder (default: 'database').
        """
        self.base_path = base_path

    def _get_csv_path(self, gender: str, category: str) -> str:
        """
        Resolve the path to a CSV file.
        :param gender: 'men' or 'women'.
        :param category: Name of the category file (without '.csv').
        :return: Path to the CSV file.
        """
        path = os.path.join(self.base_path, gender, f"{category}.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"The file '{category}.csv' does not exist in '{gender}'.")
        return path

    def get_all_data(self, gender: str, category: str) -> pd.DataFrame:
        """
        Retrieve all data from a specific category.
        :param gender: 'men' or 'women'.
        :param category: Category name.
        :return: DataFrame containing all data.
        """
        path = self._get_csv_path(gender, category)
        return pd.read_csv(path)

    def get_by_field(self, gender: str, category: str, field: str) -> List:
        """
        Retrieve all values from a specific field.
        :param gender: 'men' or 'women'.
        :param category: Category name.
        :param field: Column name.
        :return: List of values from the field.
        """
        df = self.get_all_data(gender, category)
        if field not in df.columns:
            raise ValueError(f"Field '{field}' does not exist in the dataset.")
        return df[field].tolist()

    def filter_by_field(self, gender: str, category: str, field: str, value: Union[str, int, float]) -> pd.DataFrame:
        """
        Filter data based on a specific field and value.
        :param gender: 'men' or 'women'.
        :param category: Category name.
        :param field: Column name.
        :param value: Value to filter by.
        :return: Filtered DataFrame.
        """
        df = self.get_all_data(gender, category)
        if field not in df.columns:
            raise ValueError(f"Field '{field}' does not exist in the dataset.")
        return df[df[field] == value]

    def search_in_field(self, gender: str, category: str, field: str, keyword: str) -> pd.DataFrame:
        """
        Search for a keyword in a specific field.
        :param gender: 'men' or 'women'.
        :param category: Category name.
        :param field: Column name.
        :param keyword: Keyword to search for.
        :return: DataFrame with matching rows.
        """
        df = self.get_all_data(gender, category)
        if field not in df.columns:
            raise ValueError(f"Field '{field}' does not exist in the dataset.")
        return df[df[field].str.contains(keyword, na=False, case=False)]

    def handle_images(self, gender: str, category: str, field: str, value: str, action: str, limit: int = 3):
        """
        Handle images by showing or downloading based on the action provided.
        :param gender: 'men' or 'women'.
        :param category: Category name.
        :param field: Column name containing JSON image data.
        :param value: Value to match in the specified field.
        :param action: 'show' to display images or 'download' to save them locally.
        """
        df = self.get_all_data(gender, category)
        if field not in df.columns:
            raise ValueError(f"Field '{field}' does not exist in the dataset.")

        matched_rows = df[df[field].str.contains(value, na=False, case=False)]
        if matched_rows.empty:
            raise ValueError(f"No rows found for value '{value}' in field '{field}'.")

        count = 0;
        for index, row in matched_rows.iterrows():
            image_str = row[field].replace("'", '"')
            image_json = json.loads(image_str)

            image_urls = [list(image.keys())[0] for image in image_json]
            for image_url in image_urls:
                if count >= limit:
                    break
                count+1
                if action == 'show':
                    self.show_image(image_url)
                elif action == 'download':
                    self.download_image(image_url)
                else:
                    raise ValueError(f"Invalid action '{action}'. Use 'show' or 'download'.")

    def download_image(self, url: str, output_folder: str = 'downloads') -> str:
        """
        Download an image from a URL and save it locally.
        :param url: URL of the image.
        :param output_folder: Folder to save the downloaded image (default: 'downloads').
        :return: Path to the downloaded image.
        """
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download image: {e}")

        filename = os.path.join(output_folder, os.path.basename(url))
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return filename

    def show_image(self, url: str):
        """
        Download and display an image from a URL without saving it.
        :param url: URL of the image.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img.show()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch image: {e}")
        

    def save_filtered_data(self, gender: str, category: str, df: pd.DataFrame):
        """
        Save filtered or modified data back to the original CSV file.
        :param gender: 'men' or 'women'.
        :param category: Category name.
        :param df: DataFrame to save.
        """
        path = self._get_csv_path(gender, category)
        df.to_csv(path, index=False)

# Example Usage
if __name__ == "__main__":
    api = ZaraDBAPI()

    # Example operations
    data = api.get_all_data('Men', 'TROUSERS')
    print(data.head())

    images = api.get_by_field('Women', 'SHIRTS', 'Product_Image')
    print(images[0])

    filtered = api.filter_by_field('Men', 'JACKETS', 'product_name', "HOODED BOMBER JACKET")
    print(filtered)

    search_results = api.search_in_field('Women', 'SHOES', 'Product_Name', 'sneakers')
    print(search_results)

    image_url = "https://static.zara.net/photos///2023/I/0/2/p/3833/407/800/2/w/448/3833407800_1_1_1.jpg?ts=1692780182587"  # Replace with an actual URL from the dataset
    api.show_image(image_url)

    images = api.get_by_field('Women', 'SHIRTS', 'Product_Image')
    image_str = images[0].replace("'", '"')
    image_json = json.loads(image_str)
    
    images_url = [list(image.keys()) for image in image_json]
    api.show_image(images_url[0][0])
    api.show_image(images_url[1][0])

    api.handle_images('Women', 'SHIRTS', 'Product_Image', 'DENIM', 'show')



