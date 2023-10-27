import pymongo


class Database:

    def __init__(self):
        self.client = None
        self.webcrawler_db = None
        self.projects_collection = None
        self.urls_collection = None
        self.setup()

    def setup(self):

        # Create connection
        connection_url = 'mongodb://localhost:27017/'
        self.client = pymongo.MongoClient(connection_url)

        # Create database
        database_name = 'webcrawler'
        self.webcrawler_db = self.client[database_name]

        # Create collections
        self.projects_collection = self.webcrawler_db['projects']
        self.urls_collection = self.webcrawler_db['urls']

    def add_new_project(self, url: str) -> str:
        document = self.projects_collection.insert_one({'url': url})
        return str(document.inserted_id)

    def get_url(self, project_id: str) -> str:
        document = self.urls_collection.find_one(
            {'crawled': False, 'type': 'url', 'project_id': project_id}, {'_id': 0, 'url': 1}
        )
        if document:
            return document.get('url')
        return document

    def get_urls(self, project_id: str) -> list[str]:
        documents = self.urls_collection.find({'project_id': project_id}, {'_id': 0, 'url': 1})
        return [document.get('url') for document in documents]

    def add_url(self, url: dict):
        self.urls_collection.insert_one(url)

    def add_urls(self, urls: list[dict]):
        if urls:
            self.urls_collection.insert_many(urls)

    def update_to_crawled(self, url: str, project_id: str):
        query = {'url': url, 'project_id': project_id}
        new_values = {'$set': {'crawled': True}}
        self.urls_collection.update_one(query, new_values)

    def delete_all_urls(self, project_id: str):
        self.urls_collection.delete_many({'project_id': project_id})

    def delete_project(self, _id: str):
        self.projects_collection.delete_one({'_id': _id})


if __name__ == '__main__':
    db = Database()
    project_id = '653aa7b5153790a8d712c9ad'

    db.urls_collection.delete_many({})
