if [[ $TRAVIS_TAG != "" ]]; then
   poetry config pypi-token.pypi $PYPI_TOKEN
   poetry publish
fi
