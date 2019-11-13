import argparse
import asyncio
import csv
import os
import sys

import dateutil.parser
from main import access_methods, checksums, contents, database, objects

csv.field_size_limit(sys.maxsize)

HASH_HEADERS = ["type", "id", "name", "dataset", "bundle", "size", "timestamp",
                "crc32c", "md5", "sha256", "sha512", "trunc512", "blake2b",
                "contents"]
URL_HEADERS = ['object_id', 'type', 'access_url', 'region', 'headers', 'access_id']


def read_csv(filename):
  """Read DATA from CSV in filename"""
  with open(filename) as f:
    reader = csv.DictReader(f)
    DATA = [r for r in reader]
    return DATA


def write_csv(filename, DATA, header=None):
  """Write DATA as CSV in filename"""
  with open(filename, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    writer.writerows(DATA)


def get_csv_files(dataset, bundle):
  file_list = "data/{0}/{1}/{1}.files.csv".format(dataset, bundle)
  url_list = "data/{0}/{1}/{1}.urls.csv".format(dataset, bundle)
  return file_list, url_list


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


async def process_objects(data):
  object_values = []
  for d in data:
    print("Inserting {}..., {}...".format(d['id'][0:7], d['name'][0:10]))
    timestamp = dateutil.parser.parse(d['timestamp'])
    object_values.append({
      'id': d['id'],
      'name': d['name'],
      'size': d['size'],
      'created_time': timestamp,
      'updated_time': timestamp,
    })
    await process_checksums(d)
    await process_contents(d)

  query = objects.insert()
  local_object_id = await database.execute_many(query, values=object_values)
  print("Local ID: {}".format(local_object_id))


async def process_bundle(dataset, bundle):
  file_list, url_list = get_csv_files(dataset, bundle)

  hash_data = read_csv(file_list)
  url_data = read_csv(url_list)

  await process_objects(hash_data)
  await process_access_methods(url_data)


async def process_dataset(dataset):
  for directory in os.listdir("data/{}".format(dataset)):
    print(dataset, str(directory))
    await process_bundle(dataset, str(directory))


async def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('dataset', type=str, help='Dataset')
  parser.add_argument('--bundle', type=str, help='Bundle', default=None)
  args = parser.parse_args()

  await database.connect()
  if args.bundle is None:
    await process_dataset(args.dataset)
  else:
    await process_bundle(args.dataset, args.bundle)
  await database.disconnect()


if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
  loop.close()
