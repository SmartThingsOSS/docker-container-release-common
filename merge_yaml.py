#!/usr/bin/env python

import argparse, sys, ruamel.yaml, re
from jinja2 import Environment, FunctionLoader, select_autoescape
from ruamel.yaml.compat import StringIO


def main():
  template_args = {}

  class StoreDictKeyPair(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
      self._nargs = nargs
      super(StoreDictKeyPair, self).__init__(option_strings, dest, nargs=nargs, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
      for kv in values:
        k,v = kv.split("=")
        template_args[k] = v
      setattr(namespace, self.dest, template_args)

  parser = argparse.ArgumentParser(description="Yaml Merge")
  parser.add_argument('--version', required=True)
  parser.add_argument('-f', '--files', nargs='+', required=True)
  parser.add_argument('-a', '--args', dest='template_args', action=StoreDictKeyPair, nargs='+', metavar='KEY=VAL')

  args = parser.parse_args()

  template_args['version'] = args.version

  run(args.files, template_args)

def run(files, template_args):
  yaml = ruamel.yaml.YAML()

  data = {}

  def merge(source, dest):
    for key, value in source.items():
      if isinstance(value, dict):
        node = dest.setdefault(key, {})
        merge(value, node)
      elif isinstance(value, list):
        dest[key] = dest.setdefault(key, []) + value
      else:
        dest[key] = value

  for f in files:
    with open(f) as fp:
      merge(yaml.load(fp), data)

  if template_args is None:
    yaml.dump(data, sys.stdout)
  else:
    stream = StringIO()
    yaml.dump(data, stream)
    print render(stream.getvalue(), template_args)

def render(doc, template_args):
  
  def load_template(name):
    return doc

  env = Environment(loader=FunctionLoader(load_template))

  template = env.get_template('config.yaml')
  return template.render(template_args)

if __name__ == '__main__':
  main()
