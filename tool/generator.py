import os
import argparse
import yaml, json
from jinja2 import Template, Environment

from filters.casing import pascal, snake
from filters.pluralize import plural
from filters.values import value

env = Environment(trim_blocks=True)
env.filters['pascal'] = pascal
env.filters['snake'] = snake
env.filters['plural'] = plural
env.filters['value'] = value

def parse(path):
  # TODO: Add JSON support
  params = yaml.load(file(path, 'r'))
  return params

def cleanup(root, d=None):
  d = d or root
  for k, v in d.iteritems():
    if k.lower().startswith('x-'):
      d['x_' + k[2:]] = v
      del d[k]
    if isinstance(v, dict):
      cleanup(root, v)

def resolve_ref(base_path, root, d=None):
  d = d or root
  for k, v in d.iteritems():
    if isinstance(v, dict):
      resolve_ref(base_path, root, v)

  if '$ref' in d:
    ref = {}
    if d['$ref'].startswith('#'):
      name = d['$ref'].split('/')[-1]
      ref = root['definitions'][name]
    elif d['$ref'].startswith('.'):
      path = os.path.join(base_path, d['$ref'])
      ref = parse(path)
    else:
      path = d['$ref']
      ref = parse(path)

    del d['$ref']
    for k, v in ref.iteritems():
      d[k] = v
    resolve_ref(base_path, root, d)

def find_node(params, path):
  tokens = path.split('.')
  for token in tokens:
    if token in params:
      params = params[token]
    else:
      raise Exception('Path not found ' + path)
  return params

def import_filters(package):
  pass

def templatize(from_, to_, params, item=None, content=True):
  if content:
    tpl = file(from_).read().decode('utf-8')
    output_template = env.from_string(tpl)
    output = output_template.render(root=params, item=item, env=os.environ).encode('utf-8')
  else:
    output = file(from_).read()

  filename_template = env.from_string(to_)
  filename_ = filename_template.render(root=params, item=item, env=os.environ)

  if not os.path.exists(os.path.dirname(filename_)):
    try:
        os.makedirs(os.path.dirname(filename_))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

  # print "Generating", filename_
  with open(filename_, 'w') as f:
    f.write(output)

def extend_with_parsers(root):
  from parsers.apis import parse as parse_apis
  from parsers.failures import parse as parse_failures
  parse_apis(params)
  parse_failures(params)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input', nargs='?', help='input file')
  parser.add_argument('-o', '--output', nargs='?', help='output folder')
  parser.add_argument('-t', '--template', nargs='?', help='templates folder')
  parser.add_argument('-f', '--filters', nargs='?', help='filters folder')
  parser.add_argument('-p', '--parsers', nargs='?', help='parsers folder')
  parser.add_argument('-v', '--verbose', nargs='?', help='verbose')

  args = parser.parse_args()

  # TODO: for templates in args.template

  params = parse(args.input)
  resolve_ref(os.path.split(args.input)[0], params)
  cleanup(params)

  extend_with_parsers(params)

  for subdir, dirs, files in os.walk(args.template):
    relative = subdir[len(args.template) + 1:]
    for filename in files:
      filepath = os.path.join(subdir, filename)
      print "Processing", filepath

      is_template = '.tpl' in filepath
      if is_template:
        is_array = '[[' in filepath
        array_path = ''
        # TODO: Use regex
        if is_array:
          array_path = filename[filename.index('[[') + 2 : filename.index(']]')]
          filename = filename[:filename.index('[[')]

          node = find_node(params, array_path)
          for item in node:
            outputpath = os.path.join(args.output, relative, filename)
            templatize(filepath, outputpath, params, item)

        else:
          filename = filename[:-4]
          outputpath = os.path.join(args.output, relative, filename)
          templatize(filepath, outputpath, params)
      else:
        outputpath = os.path.join(args.output, relative, filename)
        templatize(filepath, outputpath, params, None, False)