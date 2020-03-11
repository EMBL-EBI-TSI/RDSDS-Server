import argparse
import asyncio
import csv
import os
import sys
import logging
import dateutil.parser
from databases import DatabaseURL, Database
from app.models.schema import datasets, access_methods, checksums, contents, objects
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func, and_
from sqlalchemy import select

csv.field_size_limit(sys.maxsize)

DATABASE_URL_STR = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://")

database = Database(DatabaseURL(DATABASE_URL_STR), min_size=10, max_size=15)


def read_csv(filename):
  """Read DATA from CSV in filename"""
  with open(filename) as f:
    reader = csv.DictReader(f)
    DATA = [r for r in reader]
    return DATA


async def process_checksums(data):
  object_checksums = {
    'crc32c': data['crc32c'],
    'md5': data['md5'],
    'sha256': data['sha256'],
    'sha512': data['sha512'],
    'trunc512': data['trunc512'],
    'blake2b': data['blake2b']
  }
  checksum_values = []
  for c_type, c_value in object_checksums.items():
    checksum_values.append({
      'object_id': data['id'],
      'type': c_type,
      'checksum': c_value,
    })
  query = checksums.insert()
  local_checksum_id = await database.execute_many(query, values=checksum_values)
  print("Local Checksum ID: {}".format(local_checksum_id))


async def process_contents(data):
  contents_values = []
  if data['contents']:
    object_conetnts = data['contents'].split(';')
    for oc in object_conetnts:
      if oc:
        split_oc = oc.split('::')
        contents_values.append({
          'object_id': data['id'],
          'type': split_oc[0],
          'id': split_oc[1],
          'name': split_oc[2]
        })
  query = contents.insert()
  local_contents_id = await database.execute_many(query, values=contents_values)
  print("Local Contents ID: {}".format(local_contents_id))


async def process_access_methods(data):
  access_method_values = []
  for d in data:
    access_method_values.append({
      'object_id': d['object_id'],
      'type': d['type'],
      'access_url': d['access_url'],
      'region': d['region'],
      'headers': d['headers'],
      'access_id': d['access_id']
    })
  query = access_methods.insert()
  local_access_method_id = await database.execute_many(query, values=access_method_values)
  print("Local Access Method ID: {}".format(local_access_method_id))


async def process_objects(folder_path):
  data = read_csv(folder_path + '/objects.csv')
  object_values = []
  for d in data:
    print("Inserting {}..., {}...".format(d['id'][0:7], d['name'][0:10]))
    timestamp = dateutil.parser.isoparse(d['created_time'])
    object_values.append({
      'id': d['id'],
      # 'name': d['name'],
      'size': int(d['size']),
      'created_time': timestamp.replace(tzinfo=None),
      'updated_time': timestamp.replace(tzinfo=None),
    })
    
    # await process_checksums(d)
    # await process_contents(d)

  query = insert(objects).on_conflict_do_nothing(
                index_elements=[objects.c.id],
          )
  
  local_object_id = await database.execute_many(query, values=object_values)
  print("Local ID: {}".format(local_object_id))
  await process_dataset(data)
  
  
async def get_current_version(dataset: dict):
  query = select([datasets.c.version,datasets.c.object_id]).\
                where(
                    and_(
                        datasets.c.dataset == dataset['dataset'],
                        datasets.c.bundle == dataset['bundle'],
                        datasets.c.name == dataset['name']
                    )
                )
  print(query)
  results = await database.fetch_all(query)
  
  current_version = 0
  current_objectid = ''
  
  if results:
      for v in results:
          print(v['version'])
          if (v['version'] > current_version):
              current_version = v['version']
              current_objectid = v['object_id']
  
  return current_version, current_objectid
    
async def process_dataset(dataset):
  dataset_values = []
  for d in dataset:
    timestamp = dateutil.parser.isoparse(d['created_time'])
    created_time = timestamp.replace(tzinfo=None)
    print(created_time)
    current_version, current_objectid = await get_current_version(d)
    if (d['id'] != current_objectid):
        version = current_version + 1
        dataset_values.append({
          'object_id': d['id'],
          'type': d['type'],
          'name': d['name'],
          'dataset': d['dataset'],
          'bundle': d['bundle'],
          'version': version ,
          'created_time': created_time
        })
    
  query = insert(datasets).on_conflict_do_nothing()
  #query = datasets.insert()
  local_dataset = await database.execute_many(query, values=dataset_values)
  print("Local Dataset: {}".format(local_dataset))


async def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('folder_path', type=str, help='Folder Path for csv files', default='.')
  args = parser.parse_args()

  await database.connect()
  # process_dataset(args.folder_path)
  
  await process_objects(args.folder_path)
  # process_access_methods(args.folder_path)
  # process_contents(args.folder_path)
  # process_checksums(args.folder_path)
  
  await database.disconnect()


if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
  loop.close()
