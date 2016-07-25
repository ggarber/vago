# def read_dict(root, key):
#   obj = root.get(key, {})
#   if obj is not dict:
#     raise Exception('')
#   return obj.iteritems()

'''
apis:
  - tag:
  - operations
      -
  - models
      -

'''
def parse(root):
  apis = []
  for defn, schema in root.get('definitions', {}).iteritems():
    schema['title'] = schema.get('title') or defn
    tags = schema.get('tags', [])
    for tag in tags:
      api = get_or_create(apis, tag)
      parse_model(api, schema)

  for path, path_info in root.get('paths', {}).iteritems():
    for verb, verb_info in path_info.iteritems():
      tags = verb_info.get('tags', [])
      for tag in tags:
        api = get_or_create(apis, tag)
        api['operations'].append(verb_info)

        responses = verb_info.get('responses', [])
        for _, response in responses.iteritems():
          schema = response.get('schema')
          parse_model(api, schema)

  root['apis'] = apis

def parse_model(api, schema):
  get_or_create_model(api, schema)

  properties = schema.get('properties', {})
  for name, schema in properties.iteritems():
    if schema.get('title'):
      parse_model(api, schema)
    if schema.get('type') == 'array' and schema.get('items', {}).get('title'):
      parse_model(api, schema.get('items'))


  if schema.get('type') == 'array' and schema.get('items', {}).get('title'):
    parse_model(api, schema.get('items'))

def get_or_create_model(api, new_model):
  for model in api['models']:
    if model['title'] == new_model['title']:
      return model

  api['models'].append(new_model)
  return new_model

def get_or_create(apis, tag):
  for api in apis:
    if api['tag'] == tag:
      return api
  api = { 'tag': tag, 'operations': [], 'models': [] }
  apis.append(api)
  return api

