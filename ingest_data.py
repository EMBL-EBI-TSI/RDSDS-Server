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
  with open(filename, mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    DATA = [r for r in reader]
    return DATA


async def process_checksums(folder_path):
  data = read_csv(folder_path + '/checksums.csv')
  checksum_values = []
  for d in data:
    checksum_values.append({
      'object_id': d['object_id'],
      'type': d['type'],
      'checksum': d['checksum'],
    })
  query = insert(checksums).on_conflict_do_nothing()
  local_checksum_id = await database.execute_many(query, values=checksum_values)
  #print("Local Checksum ID: {}".format(local_checksum_id))


async def process_contents(folder_path):
  contents_values = []
  data = read_csv(folder_path + '/contents.csv')
  for d in data:
    contents_values.append({
      'object_id': d['object_id'],
      'type': d['type'],
      'id': d['id'],
      'name': d['name'],
    })
  query = insert(contents).on_conflict_do_nothing()
  local_contents_id = await database.execute_many(query, values=contents_values)
  #print("Local Contents ID: {}".format(local_contents_id))


async def process_access_methods(folder_path):
  access_method_values = []
  data = read_csv(folder_path + '/access_methods.csv')
  for d in data:
    access_method_values.append({
      'object_id': d['object_id'],
      'type': d['type'],
      'access_url': d['access_url'],
      'region': d['region'],
      'headers': d['headers'],
      'access_id': d['access_id']
    })
  query = insert(access_methods).on_conflict_do_nothing()
  local_access_method_id = await database.execute_many(query, values=access_method_values)
  #print("Local Access Method ID: {}".format(local_access_method_id))


async def process_objects(folder_path):
  data = read_csv(folder_path + '/objects.csv')
  object_values = []
  for d in data:
    #print("Inserting {}..., {}...".format(d['id'][0:7], d['name'][0:10]))
    timestamp = dateutil.parser.isoparse(d['created_time'])
    object_values.append({
      'id': d['id'],
      # 'name': d['name'],
      'size': int(d['size']),
      'created_time': timestamp.replace(tzinfo=None),
      'updated_time': timestamp.replace(tzinfo=None),
    })
    
    #await process_checksums(d)
    #await process_contents(d)



  query = insert(objects).on_conflict_do_nothing(
                index_elements=[objects.c.id],
          )
  
  await database.execute_many(query, values=object_values)
  #print("Local ID: {}".format(local_object_id))
  #await process_dataset(data)
  
  
async def get_current_version(dataset: dict):
  query = select([datasets.c.version,datasets.c.object_id]).\
                where(
                    and_(
                        datasets.c.dataset == dataset['dataset'],
                        datasets.c.bundle == dataset['bundle'],
                        datasets.c.name == dataset['name']
                    )
                )
  #print(query)
  results = await database.fetch_all(query)
  
  current_version = 0
  current_objectid = ''
  
  if results:
      for v in results:
          #print(v['version'])
          if (v['version'] > current_version):
              current_version = v['version']
              current_objectid = v['object_id']
  
  return current_version, current_objectid
    
async def process_dataset(folder_path):
  dataset = read_csv(folder_path + '/objects.csv')
  dataset_values = []
  for d in dataset:
    #print(d)
    timestamp = dateutil.parser.isoparse(d['created_time'])
    created_time = timestamp.replace(tzinfo=None)
    #print(created_time)
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
  await database.execute_many(query, values=dataset_values)


async def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('folder_path', type=str, help='Folder Path for csv files', default='.')
  args = parser.parse_args()

  await database.connect()
  await process_objects(args.folder_path)
  await process_dataset(args.folder_path)
  await process_access_methods(args.folder_path)
  await process_contents(args.folder_path)
  await process_checksums(args.folder_path)
  
  await database.disconnect()


if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
  loop.close()
