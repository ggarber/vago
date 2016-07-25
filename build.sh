rm -rf sdks/*
sdkVersion=2.4 sdkUserAgent=Python-SDK python tool/generator.py -i spec/opentok_api.yml -t templates/python -o sdks/python
