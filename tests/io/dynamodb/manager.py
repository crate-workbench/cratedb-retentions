import json
from pathlib import Path

from yarl import URL

from cratedb_toolkit.io.dynamodb.adapter import DynamoDBAdapter


class DynamoDBTestManager:
    def __init__(self, url: str):
        self.adapter = DynamoDBAdapter(URL(url).with_query({"region": "us-east-1"}))

    def load_product_catalog(self):
        table = self.adapter.dynamodb_resource.Table("ProductCatalog")
        try:
            table.delete()
        except Exception:  # noqa: S110
            pass

        table = self.adapter.dynamodb_resource.create_table(
            TableName="ProductCatalog",
            KeySchema=[
                {"AttributeName": "Id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "Id", "AttributeType": "N"},
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1,
            },
            TableClass="STANDARD",
        )
        table.wait_until_exists()

        data = json.loads(Path("tests/io/dynamodb/productcatalog.json").read_text())
        self.adapter.dynamodb_client.batch_write_item(RequestItems=data)
        table.load()
        return table