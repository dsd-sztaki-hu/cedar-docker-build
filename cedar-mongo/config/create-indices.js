db["template-elements"].createIndex({ "@id": 1 }, { unique: true });
db["templates"].createIndex({ "@id": 1 }, { unique: true });
db["template-instances"].createIndex({ "@id": 1 }, { unique: true });
db["users"].createIndex({ "id": 1 }, { unique: true });