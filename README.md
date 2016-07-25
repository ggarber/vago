# Metacode

Tool to generate code from a tree model described in a file (for example to generate implementations in differente languages for an API described in a JSON/YAML file)

Swagger is great but if can limit your ability to tune every single bit of the generated code.   Metacode is:
- Freed: You can generate as many files as you want.
- Extensible: You can add parsing and filters without recompiling.
- Powerful: Jinja2 for templates instead of mustache.

Steps:

Parsing:
- Read the description
- Extend it with extra parsers (to aggregate data in different ways)

Generation:
Iterate all the files:
  - Static files: Generate a single static file
  - Template files: Generate a single dynamic file
  - Meta template files: Can generate multiple files
Use Jinja Templates
