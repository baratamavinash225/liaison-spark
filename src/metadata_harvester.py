import json
import os

def load_metadata():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'mock_data.json')
    with open(json_path, 'r') as f:
        return json.load(f)

def get_schema_context():
    metadata = load_metadata()
    context = "Available Tables in Data Catalog:\n\n"
    for table in metadata['tables']:
        context += f"Table: {table['name']} ({table['size']} size)\n"
        context += f"Description: {table['description']}\n"
        context += f"Partition Keys: {', '.join(table['partition_keys']) if table['partition_keys'] else 'None'}\n"
        context += "Columns:\n"
        for col in table['columns']:
            context += f" - {col['name']} ({col['type']}): {col['description']}\n"
        context += "\n"
    return context
