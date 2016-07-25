LANGUAGES = {
  'python': {
    'true': 'True',
    'false': 'False'
  },
  'java': {
  },
  'js': {
  }
}

def value(value, language):
  return LANGUAGES.get(language, {}).get(value, value)
